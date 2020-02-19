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


def get_intel(day, groups):
    intel = {
        # new day info
        "new_day": "",
        # pressure on schedule
        "pressure": "",
        # info text
        "text": [],
        # list with important information for selected groups
        "groups_intel": []
    }

    # scan plan
    marks = scan(day)

    # going threw every day
    for idx, line in enumerate(day):
        # extract intel
        if marks[idx] == "new_day":
            intel["new_day"] = day[idx][8:]

        elif marks[idx] == "pressure":
            intel["pressure"] = day[idx][12:]

        elif marks[idx] == "text":
            intel["text"].append(day[idx][7:])

        elif marks[idx] in groups:
            intel["groups_intel"].append(day[idx][9:])

    return intel
