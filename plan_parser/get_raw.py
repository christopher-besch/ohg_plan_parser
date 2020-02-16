import requests


def get_raw():
    # list with one entry (=list[day, text]) for each day
    days = []

    # getting vps and splitting at linebreaks
    vp_0 = requests.get("https://ohggf.de/idesk/plan/public.php/VP%20Heute/035f713a4c761e16/").text.split("\n")
    vp_1 = requests.get("https://ohggf.de/idesk/plan/public.php/VP%20Morgen/d56b8a9e33fd56ec/").text.split("\n")
    # deleting first linebreaks
    del vp_0[0]
    del vp_1[0]
    # combining those two lists
    vp = vp_0 + vp_1

    # cutting vp at day breaks into vp_cut
    day_start = 0
    day_end = 0
    # date of every day
    days_date = []
    for idx, line in enumerate(vp):
        # finding line with the day the vp is made for = start of new day
        if "Ausfertigung" in line:
            # the ending of the last day is the start of the current day
            day_start = day_end
            # noting index the end of the current day
            day_end = idx
            # append date of current day
            days_date.append(line)

            # cutting lists at day starts and ends if the day has some content
            if not day_end == day_start:
                days.append({
                    "text": vp[day_start:day_end],
                    "date": days_date[-2]
                })

    # adding the last day, which starts at the end of the second last day
    days.append({
        "text": vp[day_end:],
        "date": days_date[-1]
    })

    return days
