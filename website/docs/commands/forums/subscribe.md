---
icon: lucide/messages-square
---

# `scele subscribe`

Subscribe to (or, with --off, unsubscribe from) a forum.

`subscribe` turns forum notifications on for a forum, or off with `--off`.

Subscribing means SCELE emails and notifies you about new posts; the setting is the same one
the web UI toggles.

## Usage

``` bash
scele subscribe <forum_id> [--off]
```

## Arguments

| Argument | Required |
| --- | --- |
| `forum_id` | yes |

## Options

| Flag | Type | Description |
| --- | --- | --- |
| `--off` | flag | Unsubscribe instead of subscribe. |

## Example

``` bash
scele subscribe 17474
```

## Output

![Output of scele subscribe](../../assets/commands/subscribe.png){ .cmd-shot }

Returns:

``` text
ActionResult & {subscribed: bool}
```

**`ActionResult`**

| Field | Type |
| --- | --- |
| `ok` | `boolean` |
| `action` | `string` |
| `...` | `command-specific fields` |

## Notes

- Some forums are force-subscribed by the teacher and cannot be turned off: SCELE will say so.
- Subscription state shows up in `notifications` once new posts arrive.

## See also

[`forums`](forums.md) · [notifications](../planning/notifications.md)
