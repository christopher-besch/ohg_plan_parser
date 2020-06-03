import datetime
from flask import render_template, redirect, url_for, jsonify, request
from flask_login import current_user, login_required
from app import db
from app.main import bp
from app.models import Visitors
import plan_parser


# save last seen time
@bp.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.datetime.utcnow()
        db.session.commit()
    visitors = Visitors.query.filter_by(date=datetime.date.today()).first()
    # create instance if not already existent
    if visitors is None:
        visitors = Visitors(visitors=1)
        db.session.add(visitors)
        db.session.commit()
    else:
        visitors.visitors += 1
        db.session.commit()


# start page
@bp.route('/')
@bp.route('/index')
def index():
    # visitors = Visitors.query.filter_by(date=datetime.date.today()).first()
    # return render_template("index.html", visitors_today=visitors)

    # redirect to url creation form
    return redirect(url_for("main.new_plan_link_creator"))


# create a personal link for new_plan()
@bp.route("/new_plan_link_creator")
def new_plan_link_creator():
    # get groups
    groups = request.args.get("groups")
    if groups is not None:
        groups = groups.split(";")
        # add padding
        groups += [None] * (7 - len(groups))
    else:
        groups = [None] * 7
    # get name
    name = request.args.get("name")

    plan_raw = request.args.get("plan")
    # False when the plan is unusable
    ok = True
    # final original plan, one entry per day in each week
    plan = []

    if plan_raw is None or plan_raw.strip() == "":
        ok = False
    else:
        # cut at day breaks and period breaks -> two dimensional list
        plan_days = [plan_day.split("|") for plan_day in plan_raw.split(";")]

        # when there isn't one entry for each weekday
        if len(plan_days) != 5:
            ok = False

        # going through every weekday
        for plan_day in plan_days:
            # when there are no periods
            if len(plan_day) <= 0:
                ok = False
                break

            # one entry per period
            day = []
            for period in plan_day:
                # empty messages are ok <- no school in this period
                if period == "":
                    day.append(None)
                else:
                    # when there is not enough info
                    if len(period.split("_")) != 3:
                        ok = False
                        break
                    day.append(period.split("_"))

            # add padding, so that each day has 10 periods
            day += [None] * (10 - len(day))

            # end the loop when an error has been found
            if not ok:
                break
            # save this day
            plan.append(day)

    # return list of Nones when the info is broken in any way
    if not ok:
        plan = [[None] * 10] * 5

    # turn plan so that each entry contains one period of each day
    return render_template("new_plan_link_creator.html", groups=groups, name=name, plan=list(zip(*plan)))


# get new plan for named groups
@bp.route("/new_plan")
def new_plan():

    ################################
    # extract and verify variables #
    ################################

    # False when the supplied values don't make sense
    ok = True

    # get variables
    groups_raw = request.args.get("groups")
    plan_days_raw = request.args.get("plan")
    # test if variables existent
    if groups_raw is None or groups_raw.strip() == "" or \
            plan_days_raw is None or plan_days_raw.strip() == "":
        ok = False
    else:
        # get variables from request
        groups = groups_raw.split(";")
        name = request.args.get("name")
        # cut at day breaks and period breaks -> two dimensional list
        plan_days = [plan_day.split("|") for plan_day in plan_days_raw.split(";")]

        # final original plan, one entry per day in each week
        plan = []
        # when there isn't one entry for each day in the week or the groups data is faulty
        if len(plan_days) != 5 or not groups:
            ok = False
        else:
            for plan_day in plan_days:
                # when there are no periods
                if len(plan_day) <= 0:
                    ok = False
                    break

                # on entry per period
                day = []
                for period in plan_day:
                    # empty messages are ok <- no school in this period
                    if period == "":
                        day.append(None)
                    else:
                        # when there is not enough info
                        if len(period.split("_")) != 3:
                            ok = False
                            break
                        day.append(period)

                # end the loop when an error has been found
                if not ok:
                    break
                # save this day
                plan.append(day)

    if not ok:
        return render_template("new_plan_faulty_url.html")

    ##########################
    # get intel for each day #
    ##########################

    # get dict with text and date of each day
    days_raw = plan_parser.get_raw()

    # last day from the "Vertretungsplan"
    last_day = datetime.date.fromisoformat(days_raw[0]["date"])
    days = []
    for day_raw in days_raw:
        # get dictionary with every line sorted in different entries
        lines_dict = plan_parser.get_intel(day_raw["text"], groups)
        # create datetime.date object
        date = datetime.date.fromisoformat(day_raw["date"])

        # update last_day
        if date > last_day:
            last_day = date

        # list with every change on this day
        period_changes = []
        # convert each line to a Change object
        for line in lines_dict["groups_intel"]:
            line_obj = plan_parser.Change(line, date.weekday(), date.year)
            period_changes.append(line_obj)

        # save relevant data for part after table and Change objects for changes in table
        days.append({
            "date": date,
            "text": lines_dict["text"],
            "groups_intel_raw": lines_dict["groups_intel"],
            "pressure": lines_dict["pressure"],
            "group_changes": period_changes
        })

    #####################
    # creating new plan #
    #####################

    # create Change objects representing the normal plan
    plan_old = plan_parser.create_change_objects(plan)

    # table that is actually being displayed on the website
    new_table = []
    # day, one before the plan starts = today -> yesterday
    current_day = datetime.date.today() - datetime.timedelta(days=1)
    # amount of days with changes
    len_changed_days = 0
    while True:
        # raise current day by one (skipping weekends)
        while True:
            # raise current day by one
            current_day += datetime.timedelta(days=1)
            # stop raising the current day when it is not in a weekend
            if current_day.weekday() not in {5, 6}:
                break

        # searching for day with changes in "vertretungsplan" with same date as current_day
        for day in days:
            if day["date"] == current_day:
                # save changed day
                new_table.append({
                    # copy data from day dictionary
                    "text": day["text"],
                    "raw": day["groups_intel_raw"],
                    "pressure": day["pressure"],
                    "date": current_day,
                    # overwrite "old" periods
                    "table": plan_parser.apply_changes(plan_old[current_day.weekday()], day["group_changes"])
                })
                len_changed_days += 1
                break
        # when there is no plan for this day
        else:
            new_table.append({
                "text": [],
                "raw": [],
                "date": current_day,
                # save "normal" day
                "table": plan_old[current_day.weekday()]
            })

        # stop when every day from the "Vertretungsplan" is done and each weekday is shown at least once
        used_weekdays = {day["date"].weekday() for day in new_table}
        if current_day >= last_day and len(used_weekdays) >= 5:
            break

    # list of every german weekday (excluding weekends)
    weekdays = [
        "Montag",
        "Dienstag",
        "Mittwoch",
        "Donnerstag",
        "Freitag"
    ]

    # list with the times of each period
    times = [
        ("07:50", "08:40"),
        ("08:45", "09:35"),
        ("09:40", "10:30"),
        ("10:35", "11:25"),
        ("11:30", "12:20"),
        ("12:25", "13:15"),
        ("13:20", "14:10"),
        ("14:15", "15:05"),
        ("15:10", "16:00"),
        ("16:00", "16:50"),
    ]

    # finally render
    return render_template("new_plan.html",
                           groups=", ".join(groups),
                           groups_raw=request.args.get("groups"),
                           name=name,
                           plan=new_table,
                           plan_raw=request.args.get("plan"),
                           weekdays=weekdays,
                           periods=range(0, len(new_table[0]["table"])),
                           times=times)
