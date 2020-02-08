import requests
import csv


# function to create a list (marks) with the content of every line, every item corresponds to a line with the same index
def scan(vp):
    marks = []
    for line in vp:
        # defining positions of last start and end of general information
        text_start = 0
        text_end = 0
        for idx, mark in enumerate(marks):
            if mark == "text_end":
                text_end = idx
            elif mark == "text_start":
                text_start = idx

        # finding line with the day the vp is made for
        if "Ausfertigung" in line:
            marks.append("new_day")
            continue

        # finding line with pressure on schedule
        if "      |   / " in line:
            marks.append("pressure")
            continue

        # finding blank lines with no information
        if line == "      |":
            # to prevent index errors this part will only run when there are already at least 3 lines marked
            if len(marks) > 2:
                # if there are two blank lines (the current and the last one),
                # the line before those two will contain the last line of the general information block
                # text_start > text_end is true when the current line is in the general information block or the end of
                # this block has not been found yet
                if line == "      |" and marks[-1] == "blank" and text_start > text_end:
                    marks[-2] = "text_end"
            marks.append("blank")
            continue

        # when there are at least 3 lines marked
        if len(marks) >= 3:
            # two lines after the "pressure"-line the general information block will start
            if marks[-2] == "pressure":
                marks.append("text_start")
                continue

            # when the current line is in between text_start and text_end,
            # (when text_end does not contain the right index of the end of the general information block,
            # it will be smaller then text_start)
            # the current line will contain general information
            if text_start > text_end:
                marks.append("text")
                continue

            # searching for single class information
            if "      |  " in line:
                # when the class name could not be found, the line takes its place
                group = str(line)
                for idx, mark in enumerate(marks):
                    if mark == "class_name":
                        # extracting class names
                        group = vp[idx][7:].replace(":", "")
                marks.append(group)
                continue

        if "      |" in line:
            marks.append("class_name")
            continue

        # default (something is not right)
        marks.append("undefined")

    # postprocessing
    for idx, mark in enumerate(marks):
        # replacing text_start and text_end marks with text marks
        # every possible class name at this point:
        # text; new_day; pressure; blank; undefined (only when something goes wrong); class_name; [class name]
        if mark == "text_start" or mark == "text_end":
            marks[idx] = "text"
    return marks


# getting vps and splitting at linebreaks
vp_0 = requests.get("https://ohggf.de/idesk/plan/public.php/VP%20Heute/035f713a4c761e16/").text.split("\n")
vp_1 = requests.get("https://ohggf.de/idesk/plan/public.php/VP%20Morgen/d56b8a9e33fd56ec/").text.split("\n")
# deleting first linebreaks
del vp_0[0]
del vp_1[0]
# combining those two list
vp = vp_0 + vp_1

vp_marks = scan(vp)

# list with one entry per day
vp_cut = []
vp_marks_cut = []

# cutting vp and vp_marks at new_days into vp_cut and vp_marks_cut
day_start = 0
day_end = 0
for idx, line in enumerate(vp):
    if vp_marks[idx] == "new_day":
        # the ending of the last day is the start of the current day
        day_start = day_end
        # noting index the end of the current day
        day_end = idx

        # cutting lists at day starts and ends if the day has some content
        if not day_end == day_start:
            vp_cut.append(vp[day_start:day_end])
            vp_marks_cut.append(vp_marks[day_start:day_end])

# adding the last day, which starts at the end of the second last day
vp_cut.append(vp[day_end:-1])
vp_marks_cut.append(vp_marks[day_end:-1])

for idx_0, i in enumerate(vp_cut):
    for idx, line in enumerate(i):
        print(vp_marks_cut[idx_0][idx] + "\t\t" + line)
    print("\n\n\n\n\n\n")

# make_csv(vp_cut, vp_marks_cut)
