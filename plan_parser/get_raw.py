import requests
import re
import datetime


# find location of the search phrase in the plan
def find_start(vp, ignored_lines=None):
    if ignored_lines is None:
        ignored_lines = set()

    match = None
    for idx, line in enumerate(vp):
        if idx in ignored_lines:
            continue
        if "Ausfertigung" in line:
            match = idx
            # only catch first one
            break
    return match


def get_raw(vp_raw=None, year=None):
    # either use given text or download the current one
    if vp_raw is None:
        # getting vps and splitting at linebreaks
        vp_0 = requests.get("https://ohggf.de/idesk/plan/public.php/VP%20Heute/035f713a4c761e16/").text.split("\n")
        vp_1 = requests.get("https://ohggf.de/idesk/plan/public.php/VP%20Morgen/d56b8a9e33fd56ec/").text.split("\n")
        # combining those two lists
        vp = vp_0 + vp_1
    else:
        vp = vp_raw.split("\n")

    # cut stuff before first start off
    match = find_start(vp)
    if match is not None:
        vp = vp[find_start(vp):]
    # when there is no start, there is not recognisable plan
    else:
        return []

    # list with one entry for each day
    days = []
    # last found search phrase, first line contains it already
    last_date = vp[0]
    while True:
        # skip the first line as it it is obvious that it contains a start -> no infinite loop
        match = find_start(vp, ignored_lines={0})

        if match is not None:
            # save the last day, ends right before the current line
            days.append({
                "text": vp[:match],
                "date": get_date(last_date, year)
                })
            # save date for the next day
            last_date = vp[match]
            # delete this day from the list
            vp = vp[match:]
        # nothing has been found
        else:
            days.append({
                "text": vp,
                "date": get_date(last_date, year)
            })
            break

    return days


# extract the day form the line
def get_date(date_line, year):
    if year is None:
        year = datetime.datetime.now().year

    match = re.search(r"\| *\w+ *(\d+)\. *(\d+)", date_line)
    date = datetime.date(year, int(match.group(2)), int(match.group(1)))

    # return converted to string
    return str(date)
