---
icon: lucide/messages-square
---

# `scele thread`

Show the posts in a discussion thread.

`thread` returns every post in one discussion, in reading order, with the structure intact.
Each post carries a `parent` (the post it replies to) and a `depth` (0 for the discussion
starter, 1 for a direct reply, and so on).

Because the nesting is explicit, you can render the thread as a tree, and — more usefully —
you can reply to the *exact* post you mean rather than to the thread in general.

## Usage

``` bash
scele thread <discussion_id>
```

## Arguments

| Argument | Required |
| --- | --- |
| `discussion_id` | yes |

## Example

``` bash
scele thread 62493
```

## Output

![Output of scele thread](../../assets/commands/thread.png){ .cmd-shot }

Returns:

``` text
Post[]
```

**`Post`**

| Field | Type |
| --- | --- |
| `id` | `string` |
| `author` | `string` |
| `created` | `string` |
| `subject` | `string` |
| `body` | `string` |
| `parent` | `string` |
| `depth` | `integer` |

## Notes

- Indent a thread on the fly: `scele -c thread 62493 | jq -r '.[] | "\(.depth * "  ")\(.author): \(.body)"'`.
- Post bodies are Moodle HTML flattened to plain text; attachments are listed separately.
- The whole thread is returned — there is no limit flag, because splitting a conversation is rarely what you want.

## See also

[`forum`](forum.md) · [`reply`](reply.md)
