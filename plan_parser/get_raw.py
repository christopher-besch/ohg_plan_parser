import requests


# find location of the search phrase in the plan
def find_start(vp):
    match = None
    for idx, line in enumerate(vp):
        # skipp the first line as it it is obvious that it contains a start -> no infinite loop
        if idx <= 0:
            continue
        if "Ausfertigung" in line:
            match = idx
            # only catch first one
            break
    return match


def get_raw(vp_raw=None):
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
        match = find_start(vp)

        if match is not None:
            # save the last day, ends right before the current line
            days.append({
                "text": vp[:match],
                "date": last_date
                })
            # save date for the next day
            last_date = vp[match]
            # delete this day from the list
            vp = vp[match:]
        # nothing has been found
        else:
            days.append({
                "text": vp,
                "date": last_date
            })
            break

    return days
