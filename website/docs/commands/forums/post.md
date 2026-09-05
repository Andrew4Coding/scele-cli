---
icon: lucide/messages-square
---

# `scele post`

Start a new discussion in a forum.

`post` starts a **new discussion** in a forum. It takes the forum id plus `--subject` and
`--message`.

This writes to SCELE and is visible to everyone in the course, so it requires explicit
confirmation: either `--yes` on the command line, or answering the prompt when you are on a
terminal.

## Usage

``` bash
scele post <forum_id> [--subject <subject>] [--message <message>] [--yes]
```

## Arguments

| Argument | Required |
| --- | --- |
| `forum_id` | yes |

## Options

| Flag | Type | Description |
| --- | --- | --- |
| `--subject` | value | — |
| `--message` | value | — |
| `--yes` | flag | Skip the confirmation prompt. |

## Example

``` bash
scele post 17474 --subject 'Hi' --message 'Hello' --yes
```

## Output

![Output of scele post](../../assets/commands/post.png){ .cmd-shot }

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

- To reply inside an existing discussion, use `reply` instead — `post` always creates a new thread.
- The message is sent as-is; SCELE renders it with its own formatting rules.
- There is no un-post. Check the subject and message before you pass `--yes`.

## See also

[`reply`](reply.md) · [`forum`](forum.md) · [`subscribe`](subscribe.md)
