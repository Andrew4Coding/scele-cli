---
icon: lucide/graduation-cap
---

# `scele courses`

List the courses on your dashboard.

`courses` lists every course you are currently enrolled in — the same set that fills your
SCELE dashboard. This is the entry point for almost everything else: the `id` in each row is
the **course id** that `course`, `assignments`, `forums`, `grades`, `people`, and
`resources` all take as their argument.

Each row carries the short name (the code you actually recognise, like `CSGE602022`), the
full name, and the course URL.

## Usage

``` bash
scele courses
```

## Example

``` bash
scele courses
```

## Output

![Output of scele courses](../../assets/commands/courses.png){ .cmd-shot }

Returns:

``` text
Course[]
```

**`Course`**

| Field | Type |
| --- | --- |
| `id` | `string` |
| `name` | `string` |
| `url` | `string` |
| `category` | `string` |
| `shortname` | `string` |
| `progress` | `number?` |

## Notes

- Enrolment is what determines this list — a course you can see in the catalog but are not enrolled in will not appear here. Use `categories` / `category` to browse those.
- Pipe it through `jq` to build an id lookup: `scele -c courses | jq -r '.[] | "\(.id)\t\(.shortname)"'`.

## See also

[`course`](course.md) · [`course-detail`](course-detail.md) · [categories](../catalog/categories.md)
