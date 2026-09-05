---
icon: lucide/wrench
---

# `scele tui`

Launch the interactive TUI.

`tui` launches an interactive terminal UI over the same data the other commands return:
browse courses, drill into activities, read forums and deadlines without typing ids.

It needs the optional `textual` dependency, which is not installed by default:

```bash
pipx inject scele-cli textual
```

## Usage

``` bash
scele tui
```

## Example

``` bash
scele tui
```

## Output

![Output of scele tui](../../assets/commands/tui.png){ .cmd-shot }

Returns:

``` text
launches the interactive terminal UI (no stdout document)
```

## Notes

- `tui` is the one command that does **not** print a JSON document: it takes over the terminal instead.
- Everything the TUI shows is available from the scriptable commands; it is a convenience layer, not a separate feature set.

## See also

[courses](../courses/courses.md) · [deadlines](../planning/deadlines.md)
