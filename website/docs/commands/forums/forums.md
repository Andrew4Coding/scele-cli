---
icon: lucide/messages-square
---

# `scele forums`

List the forums in a course.

`forums` lists the forums inside a course — the announcement forum, Q&A forums, discussion
boards, and so on — with the cmid you need to open each one.

Feed a cmid from here into `forum` to see the discussions inside it.

## Usage

``` bash
scele forums <course_id>
```

## Arguments

| Argument | Required |
| --- | --- |
| `course_id` | yes |

## Example

``` bash
scele forums 4234
```

## Output

![Output of scele forums](../../assets/commands/forums.png){ .cmd-shot }

Returns:

``` text
Activity[]
```

**`Activity`**

| Field | Type |
| --- | --- |
| `cmid` | `string` |
| `type` | `string` |
| `name` | `string` |
| `url` | `string` |
| `section` | `string` |

## Notes

- A course's "Class Announcements" / news forum appears here even when it has no posts.
- The cmid in this output is the same id `course` shows for the forum activity.

## See also

[`forum`](forum.md) · [course](../courses/course.md)
