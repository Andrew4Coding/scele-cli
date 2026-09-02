---
icon: lucide/wrench
---

# `scele watch`

Re-run a command on an interval and report exact line-level output changes.

`watch` re-runs any other `scele-cli` subcommand on an interval, compares each run's JSON output
against the previous one, and reports **exactly which lines changed** as a git-style unified
diff. Volatile keys such as `token` are stripped before comparison so they never register as
a change.

Run it in the foreground and it streams newline-delimited JSON events, one per line — the
only command that does not print a single document. Run it with `-d` and it detaches into
the background, writing events to `~/.config/scele/watches/<name>/events.jsonl` and POSTing
each change to any webhooks you configured.

A watch exists only while it is running. When its loop ends it deletes its own directory,
and `watch ls` prunes any watch whose process has gone.

## Usage

``` bash
scele watch
```

## Example

``` bash
scele watch deadlines --interval 600 --webhook https://hooks.example/x -d
```

## Output

![Output of scele watch](../../assets/commands/watch.png){ .cmd-shot }

Returns:

``` text
subcommands: start -> ActionResult & {name, detached, pid?}; ls -> {name, command, interval, status, last_change, tick_count}[] (running only; stopped watches are pruned); run -> WatchEvent; rm/rename -> ActionResult; clear -> ActionResult & {removed: string[]}; logs -> WatchEvent[]. A stopped watch is deleted, not kept. A foreground `watch <cmd>` streams newline-delimited WatchEvent docs.
```

**`ActionResult`**

| Field | Type |
| --- | --- |
| `ok` | `boolean` |
| `action` | `string` |
| `...` | `command-specific fields` |

## Notes

- Background watches are **POSIX-only** and do **not** survive a reboot.
- `--on change` (the default) reports only differences; `--on start` also emits the first snapshot.
- `--webhook URL` can be repeated; add auth with `--webhook-header 'X-Token: abc'`.
- Change events carry both the `diff` and the full new `snapshot`, so a webhook receiver needs no state of its own.
- The management subcommands — `ls`, `run`, `rm`, `clear`, `rename`, `logs` — each print a single document as usual.

## See also

[deadlines](../planning/deadlines.md) · [assignment](../assignments/assignment.md) · [`schema`](schema.md)
