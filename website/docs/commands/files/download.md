---
icon: lucide/folder-down
---

# `scele download`

Download a resource cmid or a pluginfile URL.

`download` fetches a file to disk. It takes either a **resource cmid** (in which case it
resolves the activity's file for you) or a raw **pluginfile URL** copied from `resources`
or `assignment-detail`.

`-o DIR` chooses the destination directory; the file keeps its original name.

## Usage

``` bash
scele download <target> [-o <out_dir>]
```

## Arguments

| Argument | Required |
| --- | --- |
| `target` | yes |

## Options

| Flag | Type | Description |
| --- | --- | --- |
| `-o`, `--out-dir` | value | Output dir. |

## Example

``` bash
scele download 222038 -o ./dl
```

## Output

![Output of scele download](../../assets/commands/download.png){ .cmd-shot }

Returns:

``` text
ActionResult & {path: string}
```

**`ActionResult`**

| Field | Type |
| --- | --- |
| `ok` | `boolean` |
| `action` | `string` |
| `...` | `command-specific fields` |

## Notes

- The token is attached to the request automatically: a pluginfile URL pasted from a browser will not work without it, which is exactly why this command exists.
- An activity cmid that is not a file resource returns `request_failed`.
- Existing files in the destination are overwritten.

## See also

[`resources`](resources.md) · [assignment-detail](../assignments/assignment-detail.md)
