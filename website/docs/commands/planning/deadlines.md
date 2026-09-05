---
icon: lucide/calendar-clock
---

# `scele deadlines`

List upcoming deadlines across all your courses.

`deadlines` is the command most people run most often. It sweeps **every course you are
enrolled in** and returns the upcoming action items — assignment due dates and
anything else Moodle treats as an activity deadline — sorted by when they land.

Each row carries the course it belongs to, the activity name, the absolute time in WIB, and
a human countdown (`in 2 days`, `in 4 hours`), so you can read it without doing arithmetic.

## Usage

``` bash
scele deadlines [--days <days>] [--limit <limit>]
```

## Options

| Flag | Type | Description |
| --- | --- | --- |
| `--days` | value | Look-ahead window in days. |
| `--limit` | value | Max events to return. |

## Example

``` bash
scele deadlines --days 14
```

## Output

![Output of scele deadlines](../../assets/commands/deadlines.png){ .cmd-shot }

Returns:

``` text
Deadline[]
```

**`Deadline`**

| Field | Type |
| --- | --- |
| `name` | `string` |
| `course` | `string` |
| `course_id` | `string` |
| `when` | `string` |
| `due_in` | `string` |
| `type` | `string` |
| `url` | `string` |

## Notes

- `--days N` sets how far ahead to look. The default window is short on purpose; widen it at the start of a term.
- Deadlines already past are not included — use `assignments <course>` to see a missed one.
- This is the single best command to put under `watch`: `scele watch deadlines --interval 3600 -d`.

## See also

[`calendar`](calendar.md) · [assignments](../assignments/assignments.md) · [watch](../tools/watch.md)
