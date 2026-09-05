---
icon: lucide/key-round
---

# `scele login`

Log in with your SCELE username and password and store a web-service token.

`login` is the only command that ever touches your password. It POSTs your SCELE username
and password to `/login/token.php` with `service=moodle_mobile_app`, receives a **Moodle
mobile web-service token**, verifies that token with a `core_webservice_get_site_info` call,
and only then writes it to disk.

The password is **never written anywhere** — not to the token file, not to a log, not to
your shell history if you use the prompt. Only the verified token is stored. If the login
fails, any token you already had is left untouched.

Run it with no arguments and it prompts for both fields (the password is hidden as you
type). For scripts and CI, set `SCELE_USERNAME` and `SCELE_PASSWORD` in the environment and
`login` will read them instead of prompting.

## Usage

``` bash
scele login [-u <username>] [-p <password>]
```

## Options

| Flag | Type | Description |
| --- | --- | --- |
| `-u`, `--username` | value | SCELE username (else prompted, or $SCELE_USERNAME). |
| `-p`, `--password` | value | SCELE password (else prompted, or $SCELE_PASSWORD). Avoid on the command line; prefer the prompt or env var. |

## Example

``` bash
SCELE_USERNAME=you SCELE_PASSWORD=secret scele login
```

## Output

![Output of scele login](../../assets/commands/login.png){ .cmd-shot }

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

- The prompt and all notices go to **stderr**, so `scele login > token-result.json` still gives you a clean JSON document.
- A wrong username or password returns the error code `login_failed`.
- An account that only signs in through an external SSO/CAS/SAML page cannot mint a token this way — `/login/token.php` never sees a password for it.
- Tokens do expire. When any command starts returning `not_authenticated`, run `login` again.

## See also

[`whoami`](whoami.md) · [`logout`](logout.md)
