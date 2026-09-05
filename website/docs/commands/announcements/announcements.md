---
icon: lucide/megaphone
---

# `scele announcements`

Show front-page / dashboard announcements.

`announcements` reads the front-page and dashboard announcements (the site-wide notices
from the faculty, separate from any individual course forum).

Each entry carries the subject, author, date, plain-text body, and a permalink back to
SCELE.

## Usage

``` bash
scele announcements
```

## Example

``` bash
scele announcements
```

## Output

![Output of scele announcements](../../assets/commands/announcements.png){ .cmd-shot }

Returns:

``` text
Announcement[]
```

**`Announcement`**

| Field | Type |
| --- | --- |
| `subject` | `string` |
| `author` | `string` |
| `date` | `string` |
| `body` | `string` |
| `permalink` | `string` |

## Notes

- `--limit N` caps how many come back.
- For course-specific announcements, open that course's announcement forum with `forums` → `forum`.

## See also

[notifications](../planning/notifications.md) · [forums](../forums/forums.md)
