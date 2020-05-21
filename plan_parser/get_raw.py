import requests


def get_raw(vp_raw=""):
    # list with one entry (=list[day, text]) for each day
    days = []

    # either use given text or download the current one
    if vp_raw == "":
        # getting vps and splitting at linebreaks
        vp_0 = requests.get("https://ohggf.de/idesk/plan/public.php/VP%20Heute/035f713a4c761e16/").text.split("\n")
        vp_1 = requests.get("https://ohggf.de/idesk/plan/public.php/VP%20Morgen/d56b8a9e33fd56ec/").text.split("\n")
        # deleting first linebreaks
        del vp_0[0]
        del vp_1[0]
        # combining those two lists
        vp = vp_0 + vp_1
    else:
        vp = vp_raw.split("\n")

    # cutting vp at day breaks into vp_cut
    day_start = None
    # date of every day
    days_date = []
    for idx, line in enumerate(vp):
        # finding line with the day the vp is made for = start of new day
        if "Ausfertigung" in line:
            # save last day
            if day_start is not None:
                days.append({
                    "text": vp[day_start:idx],
                    "date": days_date[-1]
                })

            # current position is start of the next day
            day_start = idx
            days_date.append(line)

    # adding the last day, which starts at the end of the second last day
    days.append({
        "text": vp[day_start:],
        "date": days_date[-1]
    })

    return days
