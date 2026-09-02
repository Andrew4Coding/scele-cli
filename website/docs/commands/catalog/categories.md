---
icon: lucide/library
---

# `scele categories`

Browse the course category tree.

`categories` browses the SCELE course-category tree — the catalog of everything the faculty
offers, not just what you are enrolled in.

Called with no arguments it returns the top level. Pass `--id N` to descend into one
category and see its children.

## Usage

``` bash
scele categories [--id <category_id>]
```

## Options

| Flag | Type | Description |
| --- | --- | --- |
| `--id` | value | Parent category id to list children of. |

## Example

``` bash
scele categories --id 31
```

## Output

![Output of scele categories](../../assets/commands/categories.png){ .cmd-shot }

Returns:

``` text
Category[]
```

**`Category`**

| Field | Type |
| --- | --- |
| `id` | `string` |
| `name` | `string` |
| `url` | `string` |
| `course_count` | `integer?` |

## Notes

- Categories nest several levels deep; walk down with `--id` until the children list is empty.
- To see the courses (rather than sub-categories) inside a category, use `category <id>`.

## See also

[`category`](category.md) · [`enrol`](enrol.md)
