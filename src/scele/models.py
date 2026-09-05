"""Plain dataclasses for SCELE entities returned by the web-service API."""

from dataclasses import asdict, dataclass, field


@dataclass
class Course:
    id: str
    name: str
    url: str
    category: str = ""
    shortname: str = ""
    progress: float | None = None

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class Category:
    id: str
    name: str
    url: str
    course_count: int | None = None

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class Activity:
    cmid: str
    type: str
    name: str
    url: str
    section: str = ""

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class Section:
    name: str
    summary: str
    activities: list[Activity] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {"name": self.name, "summary": self.summary,
                "activities": [a.to_dict() for a in self.activities]}


@dataclass
class Resource:
    cmid: str
    name: str
    type: str
    fileurl: str = ""
    filename: str = ""
    filesize: int | None = None
    section: str = ""

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class Discussion:
    id: str
    name: str
    url: str
    author: str = ""
    replies: int | None = None
    last_post: str = ""
    created: str = ""
    unread: int | None = None

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class Post:
    id: str
    author: str
    created: str
    subject: str
    body: str
    parent: str = ""
    depth: int = 0

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class AssignmentStatus:
    cmid: str
    name: str
    fields: dict[str, str] = field(default_factory=dict)
    files: list[dict] = field(default_factory=list)

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class AssignmentInfo:
    id: str
    cmid: str
    course_id: str
    name: str
    due: str = ""
    due_in: str = ""
    cutoff: str = ""
    allow_late: bool = False
    grade: str = ""
    instructions: str = ""
    team_submission: bool = False
    max_attempts: int | None = None
    attachments: list[dict] = field(default_factory=list)

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class Announcement:
    subject: str
    author: str
    date: str
    body: str
    permalink: str = ""

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class CourseDetail:
    id: str
    shortname: str
    fullname: str
    category: str = ""
    summary: str = ""
    start: str = ""
    end: str = ""
    teachers: list[dict] = field(default_factory=list)

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class Person:
    id: str
    name: str
    roles: list[str] = field(default_factory=list)
    email: str = ""
    groups: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class Grade:
    item: str
    type: str = ""
    grade: str = ""
    range: str = ""
    percentage: str = ""
    feedback: str = ""
    graded: str = ""

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class Deadline:
    name: str
    course: str = ""
    course_id: str = ""
    when: str = ""
    due_in: str = ""
    type: str = ""
    url: str = ""

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class CalendarEvent:
    id: str
    name: str
    when: str = ""
    type: str = ""
    course_id: str = ""
    description: str = ""

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class Notification:
    id: str
    subject: str
    sender: str = ""
    time: str = ""
    text: str = ""
    read: bool = False

    def to_dict(self) -> dict:
        return asdict(self)


