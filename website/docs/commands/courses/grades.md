---
icon: lucide/graduation-cap
---

# `scele grades`

Show your grade items for a course.

`grades` shows your grade items for one course: each item's name, the grade you were given,
the range it was graded against, the percentage, and any feedback the grader left.

It reads the user grade report, so it shows exactly what you would see on the course's
Grades page — nothing more, and nothing about anyone else.

## Usage

``` bash
scele grades <course_id>
```

## Arguments

| Argument | Required |
| --- | --- |
| `course_id` | yes |

## Example

``` bash
scele grades 4234
```

## Output

![Output of scele grades](../../assets/commands/grades.png){ .cmd-shot }

Returns:

``` text
Grade[]
```

**`Grade`**

| Field | Type |
| --- | --- |
| `item` | `string` |
| `type` | `string` |
| `grade` | `string` |
| `range` | `string` |
| `percentage` | `string` |
| `feedback` | `string` |
| `graded` | `string` |

## Notes

- Items that have not been graded yet come back with an empty grade rather than a zero.
- Feedback is Moodle HTML flattened to plain text.
- `grades` is per-course; loop over `scele courses` to build a full transcript.

## See also

[`courses`](courses.md) · [assignments](../assignments/assignments.md)
