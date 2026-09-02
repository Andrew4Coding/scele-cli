---
icon: lucide/graduation-cap
---

# `scele course`

Show a course outline (sections and activities).

`course` prints the outline of a single course: every section, and inside each section every
activity — assignments, forums, files, URLs, pages, and so on.

This is where **cmids** come from. A cmid (course-module id) identifies one activity inside
one course, and it is what `assignment`, `download`, and `forum` expect. If you know
a course id and want to act on something inside it, this is the command that gets you there.

## Usage

``` bash
scele course <course_id>
```

## Arguments

| Argument | Required |
| --- | --- |
| `course_id` | yes |

## Example

``` bash
scele course 4234
```

## Output

![Output of scele course](../../assets/commands/course.png){ .cmd-shot }

Returns:

``` text
Section[]
```

**`Section`**

| Field | Type |
| --- | --- |
| `name` | `string` |
| `summary` | `string` |
| `activities` | `Activity[]` |

## Notes

- Sections appear in the order SCELE renders them, so section names double as a rough syllabus.
- An activity's `type` tells you which command handles it: `assign` → `assignment`, `forum` → `forum`, `resource`/`folder` → `download`.
- Hidden or restricted activities are simply absent — the web-service API applies your own permissions.

## See also

[`courses`](courses.md) · [`course-detail`](course-detail.md)
