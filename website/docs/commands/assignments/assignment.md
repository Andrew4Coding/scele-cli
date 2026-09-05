---
icon: lucide/file-check
---

# `scele assignment`

Show an assignment's submission status.

`assignment` reports **your** submission status for one assignment: whether you have
submitted, whether it is a draft or final, when it was submitted, what files or text it
contains, and the grade and feedback if it has been marked.

This is the "did I actually hand it in?" command.

## Usage

``` bash
scele assignment <cmid>
```

## Arguments

| Argument | Required |
| --- | --- |
| `cmid` | yes |

## Example

``` bash
scele assignment 222043
```

## Output

![Output of scele assignment](../../assets/commands/assignment.png){ .cmd-shot }

Returns:

``` text
AssignmentStatus
```

**`AssignmentStatus`**

| Field | Type |
| --- | --- |
| `cmid` | `string` |
| `name` | `string` |
| `fields` | `map<string, string>` |
| `files` | `{name: string, url: string}[]` |

## Notes

- Takes an activity cmid.
- A submission left in `draft` state has not been handed in: teachers do not see it until you submit it for grading.
- Under `watch`, this is how you get notified the moment a grade appears.

## See also

[`assignments`](assignments.md) · [`submit`](submit.md) · [watch](../tools/watch.md)
