import re
import datetime


class Change:
    def __init__(self, line, weekday, year, school=True, period=None, teacher=None, subject=None, room=None):
        self.line = line
        self.weekday = weekday % 7
        self.school = school
        self.year = year

        self.period = period
        self.teacher = teacher
        self.subject = subject
        self.room = room

        self.old = None

        # extract data from line if a line exists
        if line is not None:
            if self.get_vertr():
                pass
            elif self.get_room_change():
                pass
            elif self.get_arrow():
                pass
            elif self.get_statt():
                pass
            elif self.get_entf():
                pass
            else:
                self.get_normal()

    def get_normal(self):
        # normal line
        match = re.search(r"(\d+)\.? *Std\. *(\w+) +(\w+) +(\w+)", self.line)
        if match:
            self.period = match.group(1)
            self.teacher = match.group(2)
            self.subject = match.group(3)
            self.room = match.group(4)

    def get_vertr(self):
        # 3.Std. Ws F --> Vertretung: Dd [S1]
        match = re.search(r"(\d+)\.? *Std\. *(\w+) +(\w+) *-->.+Vertretung: +(\w+) *\[(\w+)\]", self.line)
        if match:
            # save old intel
            self.old = Change(None, self.weekday, self.year,
                              period=match.group(1),
                              teacher=match.group(2),
                              subject=match.group(3))

            # save new intel
            self.period = self.old.period
            self.teacher = match.group(4)
            self.subject = self.old.subject
            self.room = match.group(5)
            return True
        return False

    def get_room_change(self):
        # 1.Std. Dd Sp O2 - Raumplanänderung!
        match = re.search(r"(\d+)\.? *Std\. *(\w+) +(\w+) +(\w+) *- *Raumplanänderung", self.line)
        # when there is a "Raumplanänderung"
        if match:
            # since there is only a location change, every other intel always applies
            self.old = Change(None, self.weekday, self.year,
                              period=match.group(1),
                              teacher=match.group(2),
                              subject=match.group(3))

            # save new intel
            self.period = self.old.period
            self.teacher = self.old.teacher
            self.subject = self.old.subject
            self.room = match.group(4)
            return True
        return False

    def get_arrow(self):
        # 3.Std. He E --> Stillbeschäftigung in N13 / Aufs.: Mx
        match = re.search(r"(\d+)\.? *Std\. *(\w+) +(\w+).*--> *(.+)", self.line)
        # when there is a "Raumplanänderung"
        if match:
            # save old data
            self.old = Change(None, self.weekday, self.year,
                              period=match.group(1),
                              teacher=match.group(2),
                              subject=match.group(3))

            # new room?
            room_match = re.search(r"in +(\w+)", match.group(4))
            if room_match:
                self.room = room_match.group(1)

            # new teacher?
            teacher_match = re.search(r"Auf.* +(\w+)", match.group(4))
            if teacher_match:
                self.teacher = teacher_match.group(1)
            else:
                self.teacher = self.old.teacher

            # save other new intel
            self.period = self.old.period
            self.subject = self.old.subject
            return True
        return False

    def get_statt(self):
        # 3.Std. St E O3 statt 6.Std.
        match = re.search(r"(\d+)\.? *Std\. *(\w+) +(\w+) +(\w+) *statt *(.+)", self.line)
        # when there is a "statt"
        if match:
            # since there is only a location change, every other intel always applies
            self.old = Change(None, self.weekday, self.year,
                              teacher=match.group(2),
                              subject=match.group(3),
                              room=match.group(4))

            period_match = re.search(r"(\d+)\.? *Std\.", match.group(5))
            if period_match:
                self.old.period = period_match.group(1)

            weekday_match = re.search(r"(\d+)\.(\d+)", match.group(5))
            if weekday_match:
                date = datetime.date(self.year, int(weekday_match.group(2)), int(weekday_match.group(1)))
                self.old.weekday = date.weekday()

            # save new intel
            self.teacher = self.old.teacher
            self.subject = self.old.subject
            self.room = self.old.room
            self.period = match.group(1)
            return True
        return False

    def get_entf(self):
        # 6.Std. St E entfällt
        match = re.search(r"(\d+)\.? *Std\. *(\w+) +(\w+) +entf\w*", self.line)
        # when there is a "statt"
        if match:
            # since there is only a location change, every other intel always applies
            self.old = Change(None, self.weekday, self.year,
                              period=match.group(1),
                              teacher=match.group(2),
                              subject=match.group(3))

            # save new intel
            self.period = self.old.period
            self.school = False
            return True
        return False

    def __repr__(self):
        weekdays = {
            0: "Monday",
            1: "Tuesday",
            2: "Wednesday",
            3: "Thursday",
            4: "Friday",
            5: "Saturday",
            6: "Sunday"
        }
        if self.school:
            text = f"Change: On a {weekdays[self.weekday]}"
        else:
            text = f"Change: Nothing on a {weekdays[self.weekday]}"
        if self.period is not None:
            text += f" in period {self.period}"
        if self.subject is not None:
            text += f" {self.subject}"
        if self.teacher is not None:
            text += f" at {self.teacher}"
        if self.room is not None:
            text += f" in {self.room}"
        if self.old is not None:
            text += f"; instead of {self.old}"

        return f"<{text}>"


def get_new_table():
    pass


if __name__ == "__main__":
    test = Change("      |  1.Std. Ke D O7", 3, 2018)
    print(test.line, test)

    test = Change("      |  3.Std. Ws F --> Vertretung: Dd [S1]", 3, 2018)
    print(test.line, test)

    test = Change("      |  1.Std. Dd Sp O2 - Raumplanänderung!", 3, 2018)
    print(test.line, test)

    test = Change("      |  3.Std. He E --> Stillbeschäftigung in N13 / Aufs.: Mx", 3, 2018)
    print(test.line, test)

    test = Change("      |  3.Std. St E O3 statt 6.Std.", 3, 2018)
    print(test.line, test)

    test = Change("      |  6.Std. St E entfällt", 3, 2018)
    print(test.line, test)

    test = Change("      |  5.Std. De E N12 statt Di 14.8./6.Std.", 3, 2018)
    print(test.line, test)
