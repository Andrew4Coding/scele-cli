---
icon: lucide/messages-square
---

# `scele forum`

List discussions in a forum.

`forum` lists the discussions (threads) in one forum. It accepts either the forum's activity
cmid (what `forums` and `course` give you) or the raw forum instance id, and figures out
which one you handed it.

Each discussion carries a discussion id (`d`), the subject, who started it, when the last
reply landed, and how many replies there are. That `d` is what `thread` takes.

## Usage

``` bash
scele forum <forum_id> [--limit <limit>]
```

## Arguments

| Argument | Required |
| --- | --- |
| `forum_id` | yes |

## Options

| Flag | Type | Description |
| --- | --- | --- |
| `--limit` | value | Max discussions to return. |

## Example

``` bash
scele forum 17474
```

## Output

![Output of scele forum](../../assets/commands/forum.png){ .cmd-shot }

Returns:

``` text
Discussion[]
```

**`Discussion`**

| Field | Type |
| --- | --- |
| `id` | `string` |
| `name` | `string` |
| `url` | `string` |
| `author` | `string` |
| `replies` | `integer?` |
| `last_post` | `string` |
| `created` | `string` |
| `unread` | `integer?` |

## Notes

- `--limit N` caps how many discussions come back; the newest are returned first.
- An empty list is legitimate: many announcement forums genuinely have no discussions.

## See also

[`forums`](forums.md) · [`thread`](thread.md) · [`post`](post.md)
