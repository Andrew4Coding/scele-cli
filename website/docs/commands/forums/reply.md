---
icon: lucide/messages-square
---

# `scele reply`

Reply to a forum post.

`reply` posts a reply to one specific forum post. The argument is a **post id**, which you
get from `thread` — not a discussion id.

Because you address a post rather than a thread, your reply lands in the right place in the
conversation tree. Pass `--subject` to override the default `Re: …`.

## Usage

``` bash
scele reply <post_id> [--message <message>] [--subject <subject>] [--yes]
```

## Arguments

| Argument | Required |
| --- | --- |
| `post_id` | yes |

## Options

| Flag | Type | Description |
| --- | --- | --- |
| `--message` | value | — |
| `--subject` | value | Override the auto 'Re:' subject. |
| `--yes` | flag | Skip the confirmation prompt. |

## Example

``` bash
scele reply 553756 --message 'Thanks' --yes
```

## Output

![Output of scele reply](../../assets/commands/reply.png){ .cmd-shot }

Returns:

``` text
ActionResult & {url: string}
```

**`ActionResult`**

| Field | Type |
| --- | --- |
| `ok` | `boolean` |
| `action` | `string` |
| `...` | `command-specific fields` |

## Notes

- Requires `--yes` (or a terminal confirmation) — it is public and irreversible.
- Replying to the depth-0 post is the same as replying to the discussion as a whole.

## See also

[`thread`](thread.md) · [`post`](post.md)
