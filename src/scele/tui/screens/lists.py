"""Read-only list screens backed by TableScreen: deadlines, calendar,
notifications, grades, people.
"""

from __future__ import annotations

from ... import api
from ..widgets.data_screen import TableScreen


class DeadlinesScreen(TableScreen):
    """Upcoming deadlines across every course."""

    heading = "DEADLINES"
    columns = ("When", "In", "Course", "Type", "Name")
    empty_message = "No upcoming deadlines"

    def fetch(self, session):
        return api.deadlines(session, days=30)

    def to_row(self, d):
        return (d.when, d.due_in, d.course, d.type, d.name)


class CalendarScreen(TableScreen):
    """Calendar events (classes, custom events, due dates)."""

    heading = "CALENDAR"
    columns = ("When", "Type", "Course", "Name")
    empty_message = "No calendar events in range"

    def fetch(self, session):
        return api.calendar(session, days_back=7, days_ahead=45)

    def to_row(self, e):
        return (e.when, e.type, e.course_id, e.name)

    def row_selected(self, key):
        e = self.current_item
        if e and e.description:
            self.notify(e.description, title=e.name, timeout=8)


class NotificationsScreen(TableScreen):
    """Your recent SCELE notifications."""

    heading = "NOTIFICATIONS"
    columns = ("Time", "From", "Subject", "Read")
    empty_message = "No notifications"

    def fetch(self, session):
        return api.notifications(session, limit=40)

    def to_row(self, n):
        return (n.time, n.sender, n.subject, "✓" if n.read else "•")

    def row_selected(self, key):
        n = self.current_item
        if n:
            self.notify(n.text or "(no body)", title=n.subject, timeout=10)


class GradesScreen(TableScreen):
    """Your grade items for one course."""

    columns = ("Item", "Grade", "Range", "%", "Graded")
    empty_message = "No grade items"

    def __init__(self, course_id: str):
        super().__init__()
        self.course_id = course_id
        self.heading = f"GRADES · course {course_id}"

    def fetch(self, session):
        return api.grades(session, self.course_id)

    def to_row(self, g):
        return (g.item, g.grade or "—", g.range, g.percentage or "—", g.graded)


class PeopleScreen(TableScreen):
    """People enrolled in one course."""

    columns = ("Name", "Roles", "Email")
    empty_message = "No people listed"

    def __init__(self, course_id: str):
        super().__init__()
        self.course_id = course_id
        self.heading = f"PEOPLE · course {course_id}"

    def fetch(self, session):
        return api.people(session, self.course_id)

    def to_row(self, p):
        return (p.name, ", ".join(p.roles), p.email)
