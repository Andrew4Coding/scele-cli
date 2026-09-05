---
icon: lucide/file-check
---

# `scele submit`

Submit online text or a file to an assignment (id or cmid).

`submit` hands work in to an assignment. It takes either `--text` for an online-text
submission or `--file` to upload a local file, and it accepts the assignment instance id or
its cmid.

By default it submits **for grading**. Pass `--draft` to save without submitting, which
leaves you free to change it later.

This is the most consequential command in `scele-cli`. It requires `--yes` (or a terminal
confirmation), and once a submission is final your teacher sees it.

## Usage

``` bash
scele submit <ref> [--text <text>] [--file <file_path>] [--draft] [--yes]
```

## Arguments

| Argument | Required |
| --- | --- |
| `ref` | yes |

## Options

| Flag | Type | Description |
| --- | --- | --- |
| `--text` | value | Online-text submission body. |
| `--file` | value | Local file to upload as the submission. |
| `--draft` | flag | Save as a draft; do not submit for grading. |
| `--yes` | flag | Skip the confirmation prompt. |

## Example

``` bash
scele submit 55010 --text 'my answer' --yes
```

## Output

![Output of scele submit](../../assets/commands/submit.png){ .cmd-shot }

Returns:

``` text
ActionResult & {stage: string, warnings: object[]}
```

**`ActionResult`**

| Field | Type |
| --- | --- |
| `ok` | `boolean` |
| `action` | `string` |
| `...` | `command-specific fields` |

## Notes

- `--text` and `--file` match the assignment's configured submission types: an assignment that only accepts files will reject text.
- `--draft` is the safe way to test the pipeline end-to-end without committing.
- Verify afterwards with `assignment <cmid>`; do not assume success from exit code alone if the assignment has unusual settings.
- Late submissions are accepted or refused by SCELE according to the cut-off date, not by the CLI.

## See also

[`assignment`](assignment.md) · [`assignment-detail`](assignment-detail.md) · [`assignments`](assignments.md)
