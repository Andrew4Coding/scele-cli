---
icon: lucide/graduation-cap
---

# `scele course-updates`

Show what changed in a course recently.

`course-updates` asks SCELE what has changed in a course recently, such as new or modified
activities, new forum posts, or new files. It is the closest thing to a per-course changelog.

Pair it with `watch` and you have a working "tell me when something changes in this course"
monitor without writing any polling logic yourself.

## Usage

``` bash
scele course-updates <course_id> [--since-days <since_days>]
```

## Arguments

| Argument | Required |
| --- | --- |
| `course_id` | yes |

## Options

| Flag | Type | Description |
| --- | --- | --- |
| `--since-days` | value | Look back this many days. |

## Example

``` bash
scele course-updates 4234 --since-days 14
```

## Output

![Output of scele course-updates](../../assets/commands/course-updates.png){ .cmd-shot }

Returns:

``` text
{course_id, since_days, updated: {cmid, module, changed}[]}
```

## Notes

- "Recently" is defined by Moodle's own last-access bookkeeping, not by a window you pass.
- An empty result is normal and means nothing changed, not that the call failed.

## See also

[`course`](course.md) · [watch](../tools/watch.md) · [notifications](../planning/notifications.md)
