"""Plain dataclasses for parsed SCELE entities."""

from dataclasses import asdict, dataclass, field


@dataclass
class Course:
    id: str
    name: str
    url: str
    category: str = ""

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
class Discussion:
    id: str
    name: str
    url: str
    author: str = ""
    replies: int | None = None
    last_post: str = ""

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class Post:
    id: str
    author: str
    created: str
    subject: str
    body: str

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
class Announcement:
    subject: str
    author: str
    date: str
    body: str
    permalink: str = ""

    def to_dict(self) -> dict:
        return asdict(self)
