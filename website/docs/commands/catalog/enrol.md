---
icon: lucide/library
---

# `scele enrol`

Self-enrol into a course.

`enrol` self-enrols you into a course that has self-enrolment turned on. Pass the course id;
if the course is protected by an enrolment key, pass it with `--key`.

This is a **write operation**: it changes your enrolment on SCELE. After it succeeds the
course shows up in `scele courses`.

## Usage

``` bash
scele enrol <course_id> [--instance <instance>] [--key <key>]
```

## Arguments

| Argument | Required |
| --- | --- |
| `course_id` | yes |

## Options

| Flag | Type | Description |
| --- | --- | --- |
| `--instance` | value | Self-enrol instance id (optional). |
| `--key` | value | Enrolment key, if the course requires one. |

## Example

``` bash
scele enrol 4128 --key secret
```

## Output

![Output of scele enrol](../../assets/commands/enrol.png){ .cmd-shot }

Returns:

``` text
ActionResult
```

**`ActionResult`**

| Field | Type |
| --- | --- |
| `ok` | `boolean` |
| `action` | `string` |
| `...` | `command-specific fields` |

## Notes

- Courses without self-enrolment enabled will refuse; you get `request_failed` carrying Moodle's reason.
- A wrong or missing `--key` is reported the same way.

## See also

[`category`](category.md) · [courses](../courses/courses.md)
