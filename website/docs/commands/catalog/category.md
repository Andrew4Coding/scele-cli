---
icon: lucide/library
---

# `scele category`

List courses inside a category.

`category` lists the **courses** inside one category id, as opposed to `categories`, which
lists sub-categories.

This is how you find a course you are not enrolled in yet: get its id here, then hand that
id to `enrol`.

## Usage

``` bash
scele category <category_id>
```

## Arguments

| Argument | Required |
| --- | --- |
| `category_id` | yes |

## Example

``` bash
scele category 176
```

## Output

![Output of scele category](../../assets/commands/category.png){ .cmd-shot }

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

- Only courses visible to you are returned.
- A course id from here works with `course-detail` even before you enrol, so you can preview it.

## See also

[`categories`](categories.md) · [`enrol`](enrol.md) · [course-detail](../courses/course-detail.md)
