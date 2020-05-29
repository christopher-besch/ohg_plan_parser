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
