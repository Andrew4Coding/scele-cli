---
icon: lucide/graduation-cap
---

# `scele course-detail`

Show course metadata: category, dates, teachers, summary.

`course-detail` is the metadata sibling of `course`. Where `course` gives you the activity
outline, `course-detail` gives you the header: which category the course sits in, its start
and end dates, the teachers assigned to it, and the summary text the department wrote.

Useful when you are deciding whether a course in the catalog is the one you want, or when
you need a teacher's name to address a forum post.

## Usage

``` bash
scele course-detail <course_id>
```

## Arguments

| Argument | Required |
| --- | --- |
| `course_id` | yes |

## Example

``` bash
scele course-detail 4234
```

## Output

![Output of scele course-detail](../../assets/commands/course-detail.png){ .cmd-shot }

Returns:

``` text
CourseDetail
```

**`CourseDetail`**

| Field | Type |
| --- | --- |
| `id` | `string` |
| `shortname` | `string` |
| `fullname` | `string` |
| `category` | `string` |
| `summary` | `string` |
| `start` | `string` |
| `end` | `string` |
| `teachers` | `{id: string, name: string}[]` |

## Notes

- The summary is Moodle HTML flattened to plain text.
- Teachers come from the enrolled-users list filtered by role, so a course with no assigned teacher yet returns an empty list.

## See also

[`course`](course.md) · [`people`](people.md)
