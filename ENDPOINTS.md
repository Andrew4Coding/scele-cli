# SCELE endpoints & extractable CLI commands

Derived from `moodle_capture/clean/`. Base URL: `https://scele.cs.ui.ac.id`. Standard Moodle 4.x
(theme `classic`). All authenticated requests reuse the logged-in browser session; state-changing
requests carry `sesskey` (a per-session token, e.g. `btz3644rfg`, read once from any page's
`M.cfg.sesskey` or a form hidden field).

## Endpoint map

| Endpoint | Params | Purpose |
|---|---|---|
| `GET /login/index.php` | — | login form; needs `logintoken` (hidden, per-request) + `username` + `password`, POST back |
| `GET /course/index.php` | `categoryid` | list categories / courses in a category |
| `GET /course/view.php` | `id` | course page: sections, activities, resources |
| `GET /course/info.php` | `id` | course summary (pre-enrol) |
| `POST /enrol/index.php` | `id`, `instance`, `sesskey`, `enrolpassword` | self-enrol into a course |
| `GET /mod/forum/view.php` | `id`, `o` (sort), `forceview` | forum: list of discussions |
| `GET /mod/forum/discuss.php` | `d`, `parent`, `mode` (display) | one discussion thread + posts |
| `POST /mod/forum/post.php` | `forum`/`reply`, `subject`, `message[text]`, `sesskey`, `_qf__mod_forum_post_form` | new discussion / reply |
| `GET /mod/forum/subscribe.php` | `id`, `d`, `sesskey` | (un)subscribe forum or discussion |
| `GET /mod/assign/view.php` | `id`, `action` (`editsubmission`, `removesubmissionconfirm`) | assignment status / submission |
| `GET /mod/resource/view.php` | `id`, `forceview` | file resource (redirects to file) |
| `GET /mod/folder/view.php` | `id` | folder resource listing |
| `GET /user/view.php` | `id`, `course` | user profile |
| `GET /pluginfile.php/<ctx>/<component>/<area>/<itemid>/<name>` | `forcedownload=1` | download any attachment/submission file |
| `POST /course/jumpto.php` | `sesskey`, `jump` | activity "Jump to..." navigation (URL is in `jump`) |

### Course-page component structure (`/course/view.php`)
- `#region-main` → `h2 "Topic outline"` → `ul > li[id^="section-"]` (one per week/topic)
  - `h3` section title, then activity list: each activity link is
    `/mod/<type>/view.php?id=<cmid>` with visible label `"<name> <type>"` (e.g. `… Assignment`, `… Forum`, `… File`).

### Assignment status (`/mod/assign/view.php?id=`)
Table rows: `Submission status`, `Grading status`, `Time remaining`, `Last modified`,
`File submissions` (→ `pluginfile.php` links), plus `Edit submission` / `Remove submission` actions.

### Forum thread (`/mod/forum/discuss.php?d=`)
Each post: author (`name - <NPM>`), timestamp, `Number of replies`, body text, `Permalink`,
reply link `/mod/forum/post.php?reply=<postid>`.

### Dashboard (`/` when logged in)
Announcement blocks: `Pengumuman Akademis` — each item has author, date, body, `Permalink`,
`Discuss this topic`, reply count.

---

## CLI commands worth extracting

```
scele login                       # drive Playwright headed login, persist storage_state
scele whoami                      # confirm session, print user + sesskey

scele courses                     # list my courses (from dashboard / My courses)
scele categories [--id N]         # browse course catalog        -> /course/index.php?categoryid=
scele course <id>                 # course outline: sections + activities   -> /course/view.php?id=
scele course <id> --json          # structured {sections:[{name,activities:[{cmid,type,name,url}]}]}
scele enrol <courseid> [--key K]  # self-enrol                    -> POST /enrol/index.php

scele forums <courseid>           # all forums in a course
scele forum <id>                  # discussions in a forum        -> /mod/forum/view.php?id=
scele thread <d>                  # posts in a discussion         -> /mod/forum/discuss.php?d=
scele forum post <forumid> --subject S --message M               # POST /mod/forum/post.php
scele forum reply <postid> --message M
scele forum subscribe <forumid|--discussion d> [--off]

scele assignments <courseid>      # assignments + due dates + submission status
scele assignment <cmid>           # one assignment: status, deadline, files   -> /mod/assign/view.php?id=
scele submissions <cmid>          # my submission files (download links)

scele resources <courseid>        # all File/Folder resources with download URLs
scele download <cmid|url> [-o]    # fetch a resource / pluginfile      -> pluginfile.php?forcedownload=1

scele announcements               # dashboard academic announcements
scele user <id> [--course C]      # profile lookup               -> /user/view.php
```

Not safe to automate (keep manual): CAPTCHA/SSO in login, `logout`, `delete`, `unenrol`.
