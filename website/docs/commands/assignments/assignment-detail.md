---
icon: lucide/file-check
---

# `scele assignment-detail`

Show an assignment's instructions, due dates and brief attachments (id or cmid).

`assignment-detail` shows the assignment brief: the full instructions the teacher wrote, the
due and cut-off dates, the grading setup, and the list of attached brief files with their
download URLs.

Use it before you write anything; use `assignment` after you submit.

## Usage

``` bash
scele assignment-detail <ref>
```

## Arguments

| Argument | Required |
| --- | --- |
| `ref` | yes |

## Example

``` bash
scele assignment-detail 222043
```

## Output

![Output of scele assignment-detail](../../assets/commands/assignment-detail.png){ .cmd-shot }

Returns:

``` text
AssignmentInfo
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

- Accepts either the assignment instance id or the activity cmid.
- Attachment URLs are pluginfile URLs — hand them straight to `download`.
- Instructions are Moodle HTML flattened to plain text, so formatting is lost but content is not.

## See also

[`assignment`](assignment.md) · [`submit`](submit.md) · [download](../files/download.md)
