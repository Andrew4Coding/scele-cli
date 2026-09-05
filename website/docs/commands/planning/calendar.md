---
icon: lucide/calendar-clock
---

# `scele calendar`

List calendar events (classes, custom events, deadlines).

`calendar` returns raw calendar events rather than just deadlines: scheduled classes, custom
events you created yourself, site-wide events, and course events.

Where `deadlines` answers *what do I owe*, `calendar` answers *what is on my schedule*.

## Usage

``` bash
scele calendar [--days-back <days_back>] [--days-ahead <days_ahead>]
```

## Options

| Flag | Type | Description |
| --- | --- | --- |
| `--days-back` | value | Number of days in the past to include. |
| `--days-ahead` | value | Number of days in the future to include. |

## Example

``` bash
scele calendar --days-ahead 30
```

## Output

![Output of scele calendar](../../assets/commands/calendar.png){ .cmd-shot }

Returns:

``` text
CalendarEvent[]
```

**`CalendarEvent`**

| Field | Type |
| --- | --- |
| `id` | `string` |
| `name` | `string` |
| `when` | `string` |
| `type` | `string` |
| `course_id` | `string` |
| `description` | `string` |

## Notes

- `--days-ahead N` sets the window.
- Events carry their type, so you can filter classes from assignment deadlines client-side.

## See also

[`deadlines`](deadlines.md) · [`notifications`](notifications.md)
