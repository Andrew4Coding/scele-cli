---
icon: lucide/key-round
---

# `scele whoami`

Report whether the stored token is valid and who it belongs to.

`whoami` answers one question: *is the stored token still good?* It loads the token from the
config directory and makes a single `core_webservice_get_site_info` call. If the call
succeeds it reports the account behind the token: user id, username, full name, and the
site it is bound to.

It is the cheapest health check available, so it is the right first call in any script
before you do real work, and the right thing to run when another command starts failing.

## Usage

``` bash
scele whoami
```

## Example

``` bash
scele whoami
```

## Output

![Output of scele whoami](../../assets/commands/whoami.png){ .cmd-shot }

Returns:

``` text
{ok: bool, authenticated: bool, base_url: string, user: string, userid: integer, username: string, token: object}
```

## Notes

- Prints `authenticated: false` rather than erroring when there is no token at all, so you can branch on it safely.
- Makes exactly one web-service call.

## See also

[`login`](login.md) · [`logout`](logout.md)
