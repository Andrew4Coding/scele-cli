---
icon: lucide/folder-down
---

# `scele resources`

List downloadable file/folder resources in a course.

`resources` lists every downloadable file and folder resource in a course — lecture slides,
handouts, datasets — each with its filename, size, activity cmid, and direct `fileurl`.

Hand either the cmid or the `fileurl` to `download`.

## Usage

``` bash
scele resources <course_id>
```

## Arguments

| Argument | Required |
| --- | --- |
| `course_id` | yes |

## Example

``` bash
scele resources 4234
```

## Output

![Output of scele resources](../../assets/commands/resources.png){ .cmd-shot }

Returns:

``` text
Resource[]
```

**`Resource`**

| Field | Type |
| --- | --- |
| `cmid` | `string` |
| `name` | `string` |
| `type` | `string` |
| `fileurl` | `string` |
| `filename` | `string` |
| `filesize` | `integer?` |
| `section` | `string` |

## Notes

- Only file and folder resources appear; links, pages, and embedded media are activities, not files.
- A folder resource expands to its contained files.
- Bulk-download a course: `scele -c resources 4234 | jq -r '.[].fileurl' | xargs -n1 scele download -o ./slides`.

## See also

[`download`](download.md) · [course](../courses/course.md)
