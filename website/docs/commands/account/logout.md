---
icon: lucide/key-round
---

# `scele logout`

Delete the stored web-service token.

`logout` deletes the stored token file from your config directory. That is all it does:
it is a purely local operation and makes no network call.

The token is not invalidated on the SCELE server; it is simply forgotten by this machine.
To revoke it on the server side, use the security-keys page in your SCELE profile.

## Usage

``` bash
scele logout
```

## Example

``` bash
scele logout
```

## Output

![Output of scele logout](../../assets/commands/logout.png){ .cmd-shot }

Returns:

``` text
ActionResult
```

**`ActionResult`**

| Field | Type |
| --- | --- |
| `ok` | `boolean` |
| `action` | `string` |
| `...` | `command-specific fields` |

## Notes

- Safe to run when you are not logged in; it reports success either way.
- Does not touch anything else in the config directory, including running watches.

## See also

[`login`](login.md)
