---
icon: lucide/calendar-clock
---

# `scele notifications`

Show your recent SCELE notifications.

`notifications` prints your recent SCELE notifications (the bell-icon feed: forum replies,
course announcements, assignment reminders), and system messages.

Each entry carries its subject, the plain-text body, when it arrived, and whether you have
read it.

## Usage

``` bash
scele notifications [--limit <limit>]
```

## Options

| Flag | Type | Description |
| --- | --- | --- |
| `--limit` | value | Max notifications to return. |

## Example

``` bash
scele notifications --limit 20
```

## Output

![Output of scele notifications](../../assets/commands/notifications.png){ .cmd-shot }

Returns:

``` text
Notification[]
```

**`Notification`**

| Field | Type |
| --- | --- |
| `id` | `string` |
| `subject` | `string` |
| `sender` | `string` |
| `time` | `string` |
| `text` | `string` |
| `read` | `boolean` |

## Notes

- Reading notifications through the CLI does **not** mark them as read on SCELE.
- Bodies are Moodle HTML flattened to plain text, so links appear inline as text.

## See also

[announcements](../announcements/announcements.md) · [`deadlines`](deadlines.md)
