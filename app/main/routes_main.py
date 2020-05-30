import datetime
from flask import render_template, redirect, url_for, jsonify, request
from flask_login import current_user, login_required
from app import db
from app.main import bp
from app.models import Visitors
import plan_parser
import json


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
    visitors = Visitors.query.filter_by(date=datetime.date.today()).first()
    return render_template("index.html", visitors_today=visitors)


# get intel for named groups
@bp.route("/get_intel")
def get_intel():
    # final object with requested data
    days = []

    groups = request.args.get("groups").split(";")
    name = request.args.get("name")

    if groups is None:
        return ""
    else:
        days_raw = plan_parser.get_raw()
        for day_raw in days_raw:
            lines_dict = plan_parser.get_intel(day_raw["text"], groups)
            date = datetime.date.fromisoformat(day_raw["date"])

            days.append({
                "date": date.isoformat(),
                "text": lines_dict["text"],
                "groups_intel": [],
                "groups_intel_raw": []
            })

            for line in lines_dict["groups_intel"]:
                days[-1]["groups_intel_raw"].append(line)

                line_obj = plan_parser.Change(line, date.weekday(), date.year)

                days[-1]["groups_intel"].append({
                    "period": line_obj.period,
                    "room": line_obj.room,
                    "teacher": line_obj.teacher,
                    "subject": line_obj.subject
                })

            days[-1]["groups_intel"] = sorted(days[-1]["groups_intel"], key=lambda entry: entry["period"])

        return render_template("get_intel.html", name=name, days=days)


# get new plan for named groups
@bp.route("/new_plan")
def new_plan():
    # get variables from request
    groups = request.args.get("groups").split(";")
    name = request.args.get("name")
    # this is json btw
    plan = request.args.get("plan")
    if groups is None or plan is None:
        return ""

    ##########################
    # get intel for each day #
    ##########################

    # get dict with text and date of each day
    days_raw = plan_parser.get_raw()

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
            "group_changes": period_changes
        })

    #####################
    # creating new plan #
    #####################

    # create Change objects representing the normal plan
    plan_old = plan_parser.create_change_objects(json.loads(plan))

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

        # stop when at least two days have been done and every day from the "Vertretungsplan" is done
        if current_day >= last_day:
            break

    # list of every german weekday (excluding weekends)
    weekdays = [
        "Montag",
        "Dienstag",
        "Mittwoch",
        "Donnerstag",
        "Freitag"
    ]

    # finally render
    return render_template("new_plan.html",
                           name=name,
                           plan=new_table,
                           weekdays=weekdays,
                           periods=range(0, len(new_table[0]["table"])))
