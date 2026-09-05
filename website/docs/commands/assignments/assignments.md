---
icon: lucide/file-check
---

# `scele assignments`

List assignments in a course.

`assignments` lists every assignment in a course with the information you actually need to
plan: the due date, the cut-off date, whether late submissions are allowed, the maximum
grade, and the ids you need for the other assignment commands.

Note the two ids: `id` is the assignment instance id and `cmid` is the activity id. Both are
accepted wherever a "ref" is asked for, so you can use whichever you have.

## Usage

``` bash
scele assignments <course_id>
```

## Arguments

| Argument | Required |
| --- | --- |
| `course_id` | yes |

## Example

``` bash
scele assignments 4234
```

## Output

![Output of scele assignments](../../assets/commands/assignments.png){ .cmd-shot }

Returns:

``` text
AssignmentInfo[]
```

**`AssignmentInfo`**

| Field | Type |
| --- | --- |
| `id` | `string` |
| `cmid` | `string` |
| `course_id` | `string` |
| `name` | `string` |
| `due` | `string` |
| `due_in` | `string` |
| `cutoff` | `string` |
| `allow_late` | `boolean` |
| `grade` | `string` |
| `instructions` | `string` |
| `team_submission` | `boolean` |
| `max_attempts` | `integer?` |
| `attachments` | `{filename: string, filesize: integer, fileurl: string}[]` |

## Notes

- This does not tell you whether *you* submitted — that is `assignment <cmid>`.
- For a cross-course view of what is due next, use `deadlines` instead.

## See also

[`assignment`](assignment.md) · [`assignment-detail`](assignment-detail.md) · [deadlines](../planning/deadlines.md)
