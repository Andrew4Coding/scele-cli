# SCELE web-service map

`scele` talks to SCELE through the Moodle mobile web-service API. Every request is a
`POST https://scele.cs.ui.ac.id/webservice/rest/server.php` with `wstoken`,
`wsfunction`, `moodlewsrestformat=json`, and the function's parameters (nested values
flattened to `key[0][sub]` by `session._flatten`).

The token is minted once: `POST /login/token.php` with `username`, `password`,
`service=moodle_mobile_app` → `{ "token": "..." }`, verified with
`core_webservice_get_site_info`.

## Command → web-service function

| Command | Web-service function(s) |
|---|---|
| `login` | `POST /login/token.php`, then `core_webservice_get_site_info` |
| `whoami` | `core_webservice_get_site_info` |
| `courses` | `core_enrol_get_users_courses` |
| `course-detail` | `core_course_get_courses_by_field` + `core_enrol_get_enrolled_users` |
| `course` | `core_course_get_contents` |
| `people` | `core_enrol_get_enrolled_users` |
| `grades` | `gradereport_user_get_grade_items` |
| `course-updates` | `core_course_get_updates_since` |
| `deadlines` | `core_calendar_get_action_events_by_timesort` |
| `calendar` | `core_calendar_get_calendar_events` |
| `notifications` | `core_message_get_notifications` |
| `categories` | `core_course_get_categories` |
| `category` | `core_course_get_courses_by_field` (field `category`) |
| `forums` | `mod_forum_get_forums_by_courses` |
| `forum` | `mod_forum_get_forum_discussions` → `..._paginated`; a cmid is resolved to the forum instance id via `core_course_get_course_module` |
| `thread` | `mod_forum_get_discussion_posts` |
| `assignments` / `assignment-detail` | `mod_assign_get_assignments` |
| `assignment` | `core_course_get_course_module` + `mod_assign_get_submission_status` |
| `submit --text` | `mod_assign_save_submission` (+ `mod_assign_submit_for_grading`) |
| `submit --file` | `core_files_get_unused_draft_itemid` + `POST /webservice/upload.php` + `mod_assign_save_submission` (+ `mod_assign_submit_for_grading`) |
| `quizzes` | `mod_quiz_get_quizzes_by_courses` + `mod_quiz_get_user_best_grade` |
| `quiz` | `core_course_get_course_module` + `mod_quiz_get_quizzes_by_courses` + `mod_quiz_get_quiz_access_information` + `mod_quiz_get_user_attempts` |
| `quiz-review` | `mod_quiz_get_attempt_review` |
| `resources` | `core_course_get_contents` (modules `resource` / `folder` / `url`) |
| `announcements` | `mod_forum_get_forums_by_courses` (course 1, type `news`) + `mod_forum_get_forum_discussions` |
| `enrol` | `enrol_self_enrol_user` |
| `subscribe` | `mod_forum_set_subscription_state` |
| `post` | `mod_forum_add_discussion` |
| `reply` | `mod_forum_add_discussion_post` |
| `download` | file URLs from the calls above → `GET /webservice/pluginfile.php/<path>?token=…&forcedownload=1` |

## ID conventions

- **course id** — from `courses` / a `course/view.php?id=<course>` URL.
- **cmid** (activity/module id) — from `course`; used by `assignment`, `download`.
- **forum id** — the activity cmid from `forums <course>` or `course <course>`; `forum`
  also accepts the forum's own instance id.
- **discussion id (d)** — from `forum <id>` → `thread <d>`.
- **post id** — from `thread <d>` → `reply <post>`.
- **assignment ref** — instance id *or* cmid from `assignments <course>`; `assignment` takes the cmid.
- **quiz cmid** — from `quizzes <course>` / `course <course>` → `quiz <cmid>`.
- **quiz attempt id** — from `quiz <cmid>` → `quiz-review <attempt>`.

## Not implemented (deliberately)

`mod_quiz_start_attempt` / `save_attempt` / `process_attempt` — taking or submitting a
graded quiz attempt through the API is irreversible and affects real grades, so the CLI
only *reads* quizzes.

## Notes

- Timestamps arrive as epoch seconds (UTC) and are rendered `YYYY-MM-DD HH:MM WIB`.
- Message bodies / summaries / feedback arrive as HTML and are flattened to plain text.
- A `news` forum with no posts legitimately returns `[]`.
