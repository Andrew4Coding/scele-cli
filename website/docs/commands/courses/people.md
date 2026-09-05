---
icon: lucide/graduation-cap
---

# `scele people`

List the people enrolled in a course.

`people` lists everyone enrolled in a course together with their roles (students,
teachers, non-editing teachers, and so on).

It is the command to reach for when you need a person's user id (to read their forum posts)
or simply want to know who is teaching a section.

## Usage

``` bash
scele people <course_id>
```

## Arguments

| Argument | Required |
| --- | --- |
| `course_id` | yes |

## Example

``` bash
scele people 4234
```

## Output

![Output of scele people](../../assets/commands/people.png){ .cmd-shot }

Returns:

``` text
Person[]
```

**`Person`**

| Field | Type |
| --- | --- |
| `id` | `string` |
| `name` | `string` |
| `roles` | `string[]` |
| `email` | `string` |
| `groups` | `string[]` |

## Notes

- Large courses return large lists; pipe through `jq 'map(select(.roles | index("Teacher")))'` to keep just the staff.
- Some courses restrict the participants list. If SCELE refuses, you get `request_failed` with Moodle's own message.

## See also

[`course-detail`](course-detail.md) · [`courses`](courses.md)
