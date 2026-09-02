"""api.py maps Moodle web-service payloads onto the CLI's dataclasses.

A FakeSession returns canned JSON per wsfunction — no network, no token.
"""


from scele import api
from scele.models import (
    AssignmentStatus, CalendarEvent, Deadline, Discussion, Grade, Notification, Person,
    Post, Quiz, QuizDetail, QuizReview,
)
from scele.session import RequestFailedError


class FakeSession:
    base = "https://scele.example"
    token = "T"

    def __init__(self, responses: dict):
        self.responses = responses
        self.calls = []

    def ws(self, wsfunction, **params):
        self.calls.append((wsfunction, params))
        if wsfunction not in self.responses:
            raise AssertionError(f"unexpected ws call: {wsfunction}")
        val = self.responses[wsfunction]
        return val(params) if callable(val) else val

    def userid(self):
        return 8830

    def pluginfile_url(self, url):
        return url + "?token=T"


def test_my_courses_sorts_and_maps():
    s = FakeSession({
        "core_enrol_get_users_courses": [
            {"id": 2, "shortname": "DDP2", "fullname": "Dasar Pemrograman 2", "progress": 40.2},
            {"id": 1, "shortname": "ALG", "fullname": "Algoritma", "hidden": True},
            {"id": 3, "shortname": "ANP", "fullname": "Analisis Numerik", "progress": None},
        ],
    })
    out = api.my_courses(s)
    assert [c.shortname for c in out] == ["ANP", "DDP2"]  # hidden dropped, sorted
    assert out[1].progress == 40.2
    assert out[1].url == "https://scele.example/course/view.php?id=2"


def test_thread_builds_parent_and_depth():
    s = FakeSession({
        "mod_forum_get_discussion_posts": {"posts": [
            {"id": 1, "parentid": 0, "subject": "D05", "message": "<p>root</p>",
             "timecreated": 0, "author": {"fullname": "Aimee"}},
            {"id": 2, "parentid": 1, "subject": "Re: D05", "message": "hi",
             "timecreated": 0, "author": {"fullname": "Naya"}},
            {"id": 3, "parentid": 2, "subject": "Re: D05", "message": "yo",
             "timecreated": 0, "author": {"fullname": "Marco"}},
        ]},
    })
    posts = api.thread(s, "62561")
    assert [p.depth for p in posts] == [0, 1, 2]
    assert posts[2].parent == "2"
    assert posts[0].body == "root"
    assert all(isinstance(p, Post) for p in posts)


def test_assignment_status_summarizes_submission():
    s = FakeSession({
        "core_course_get_course_module": {"cm": {"id": 55010, "instance": 900,
                                                 "course": 4234, "name": "HW1"}},
        "mod_assign_get_submission_status": {"lastattempt": {
            "gradingstatus": "graded",
            "submission": {"status": "submitted", "attemptnumber": 0,
                           "timemodified": 0, "plugins": [
                               {"type": "file", "fileareas": [{"files": [
                                   {"filename": "a.pdf", "fileurl": "https://x/a.pdf"}]}]},
                           ]},
        }},
    })
    st = api.assignment(s, "55010")
    assert isinstance(st, AssignmentStatus)
    assert st.name == "HW1"
    assert st.fields["Submission status"] == "SUBMITTED"
    assert st.fields["Grading status"] == "graded"
    assert st.files == [{"name": "a.pdf", "url": "https://x/a.pdf"}]


def test_grades_maps_items():
    s = FakeSession({
        "gradereport_user_get_grade_items": {"usergrades": [{"gradeitems": [
            {"itemname": "Quiz 1", "itemtype": "mod", "gradeformatted": "88.00",
             "grademin": 0, "grademax": 100, "percentageformatted": "88.00 %",
             "feedback": "<p>nice</p>", "gradedategraded": 0},
        ]}]},
    })
    out = api.grades(s, "4234")
    assert out == [Grade(item="Quiz 1", type="mod", grade="88.00", range="0–100",
                         percentage="88.00 %", feedback="nice",
                         graded=out[0].graded)]


def test_deadlines_and_calendar_and_notifications_shapes():
    s = FakeSession({
        "core_calendar_get_action_events_by_timesort": {"events": [
            {"name": "HW due", "timesort": 4102444800, "url": "https://x",
             "course": {"shortname": "DDP2", "id": 2},
             "normalisedeventtypetext": "Assignment"},
        ]},
        "core_calendar_get_calendar_events": {"events": [
            {"id": 7, "name": "Lecture", "timestart": 4102444800, "eventtype": "course",
             "course": {"id": 2}, "description": "<p>room A</p>"},
        ]},
        "core_message_get_notifications": {"notifications": [
            {"id": 5, "subject": "Graded", "from": {"fullname": "Grader"},
             "timecreated": 0, "fullmessagehtml": "<p>done</p>", "read": True},
        ]},
    })
    assert isinstance(api.deadlines(s)[0], Deadline)
    assert api.deadlines(s)[0].course == "DDP2"
    assert isinstance(api.calendar(s)[0], CalendarEvent)
    assert api.calendar(s)[0].description == "room A"
    n = api.notifications(s)[0]
    assert isinstance(n, Notification) and n.read is True and n.text == "done"


def test_people_maps_roles():
    s = FakeSession({
        "core_enrol_get_enrolled_users": [
            {"id": 1, "fullname": "Dr Yugo", "roles": [{"shortname": "editingteacher"}],
             "email": "y@x", "groups": [{"name": "A"}]},
        ],
    })
    p = api.people(s, "4234")[0]
    assert isinstance(p, Person)
    assert p.roles == ["editingteacher"] and p.groups == ["A"]


def test_forum_accepts_a_cmid_and_resolves_it_to_the_instance():
    def discussions(params):
        if params["forumid"] != 17474:
            raise RequestFailedError("Unable to find forum with id")
        return {"discussions": [
            {"discussion": 62561, "name": "D05", "userfullname": "Aimee",
             "numreplies": 25, "created": 0, "timemodified": 0},
        ]}

    s = FakeSession({
        "mod_forum_get_forum_discussions": discussions,
        "mod_forum_get_forum_discussions_paginated": discussions,
        "core_course_get_course_module": {"cm": {"id": 222560, "instance": 17474,
                                                 "modname": "forum"}},
    })
    out = api.forum(s, "222560")  # 222560 is the activity cmid, 17474 the instance id
    assert len(out) == 1 and isinstance(out[0], Discussion)
    assert out[0].id == "62561"


def test_forum_uses_instance_id_directly_without_extra_calls():
    s = FakeSession({
        "mod_forum_get_forum_discussions": {"discussions": [
            {"discussion": 62561, "name": "D05", "userfullname": "Aimee", "numreplies": 1},
        ]},
    })
    assert api.forum(s, "17474")[0].id == "62561"
    assert [c[0] for c in s.calls] == ["mod_forum_get_forum_discussions"]


_QUIZ = {"id": 8228, "coursemodule": 188689, "name": "Mini-quiz W5",
         "timeopen": 0, "timeclose": 4102444800, "timelimit": 600, "attempts": 1,
         "grade": 10, "grademethod": 1, "intro": "<p>hi</p>"}


def test_quizzes_lists_with_best_grade():
    s = FakeSession({
        "mod_quiz_get_quizzes_by_courses": {"quizzes": [_QUIZ]},
        "mod_quiz_get_user_best_grade": {"hasgrade": True, "grade": 9},
    })
    out = api.quizzes(s, "3937")
    assert len(out) == 1 and isinstance(out[0], Quiz)
    assert out[0].cmid == "188689" and out[0].best_grade == "9"
    assert out[0].time_limit == "10 mins" and out[0].is_open is True


def test_quiz_detail_resolves_cmid_and_merges_access():
    s = FakeSession({
        "core_course_get_course_module": {"cm": {"id": 188689, "instance": 8228,
                                                 "course": 3937, "name": "Mini-quiz W5"}},
        "mod_quiz_get_quizzes_by_courses": {"quizzes": [_QUIZ]},
        "mod_quiz_get_user_best_grade": {"hasgrade": True, "grade": 10},
        "mod_quiz_get_quiz_access_information": {
            "canattempt": False,
            "preventaccessreasons": ["This quiz is not currently available"],
            "accessrules": ["Attempts allowed: 1", "Time limit: 10 mins"]},
        "mod_quiz_get_user_attempts": {"attempts": [
            {"id": 459484, "attempt": 1, "state": "finished",
             "timestart": 0, "timefinish": 0, "sumgrades": 10}]},
    })
    d = api.quiz(s, "188689")
    assert isinstance(d, QuizDetail)
    assert d.id == "8228" and d.grade_method == "highest grade"
    assert d.can_attempt is False and d.prevented_reasons
    assert d.attempts[0].id == "459484"


def test_quiz_review_extracts_marks_and_submitted_answer():
    html = ('<div class="que numerical correct"><div class="qtext"><p>Compute F1</p></div>'
            '<input name="q1_answer" value="0.862" readonly>'
            '<div class="rightanswer">The correct answer is: 0.909</div></div>')
    s = FakeSession({"mod_quiz_get_attempt_review": {
        "grade": 10,
        "attempt": {"quiz": 8228, "state": "finished", "sumgrades": 10,
                    "timestart": 0, "timefinish": 0},
        "questions": [{"slot": 1, "number": 1, "type": "numerical", "status": "Correct",
                       "mark": "10.00", "maxmark": 10, "flagged": False, "html": html}],
    }})
    r = api.quiz_review(s, "459484")
    assert isinstance(r, QuizReview) and r.grade == "10"
    q = r.questions[0]
    assert q.status == "Correct" and q.mark == "10.00" and q.max_mark == "10"
    assert "Your answer: 0.862" in q.text
    assert "correct answer is: 0.909" in q.text


def test_forum_reply_passes_subject_when_given():
    s = FakeSession({"mod_forum_add_discussion_post": {"post": {"discussionid": 99}}})
    url = api.forum_reply(s, "553917", "thanks", subject="Custom")
    assert url == "https://scele.example/mod/forum/discuss.php?d=99"
    assert s.calls[0][1]["subject"] == "Custom"


def test_forum_reply_omits_subject_by_default():
    s = FakeSession({"mod_forum_add_discussion_post": {"post": {}}})
    api.forum_reply(s, "553917", "thanks")
    assert "subject" not in s.calls[0][1]
