"""`scele` command-line entry point. Every command prints one JSON document to stdout."""

from pathlib import Path

import click

from . import __version__, api
from .auth import terminal_login
from .config import base_url, clear_cookies
from .output import emit, fail
from .session import NotAuthenticatedError, SceleSession


def _session(ctx) -> SceleSession:
    return ctx.obj["session"]


def _out(ctx, obj):
    emit(obj, fmt=ctx.obj["format"], compact=ctx.obj["compact"])


def _guard(fn):
    try:
        return fn()
    except NotAuthenticatedError as e:
        fail(str(e), code="not_authenticated")
    except Exception as e:  # noqa: BLE001 - surface any failure as JSON
        fail(f"{type(e).__name__}: {e}", code="request_failed")


@click.group(
    context_settings={"help_option_names": ["-h", "--help"]},
    epilog="Output format defaults to a table on a terminal, plain JSON when piped. "
           "Use `-f json`, `-f yaml`, or `-f table` to override. "
           "Run `scele schema` for a machine-readable manifest.",
)
@click.version_option(__version__, prog_name="scele", message="%(version)s")
@click.option("-c", "--compact", is_flag=True, help="Single-line JSON (implies -f json).")
@click.option("-f", "--format", "fmt",
              type=click.Choice(["auto", "json", "yaml", "table"]),
              default="auto", show_default=True,
              help="Output format. auto = table on terminal, JSON when piped.")
@click.pass_context
def main(ctx, compact, fmt):
    """Command-line client for SCELE (Moodle) at Fasilkom UI."""
    ctx.obj = {"compact": compact, "format": fmt, "session": SceleSession()}


@main.command()
@click.pass_context
def schema(ctx):
    """Print a machine-readable manifest of all commands and I/O shapes."""
    from .schema import build
    emit(build(main), fmt="json", compact=ctx.obj["compact"])


@main.command()
@click.option("-u", "--username", help="SCELE username (else prompted, or $SCELE_USERNAME).")
@click.option("-p", "--password", help="SCELE password (else prompted, or $SCELE_PASSWORD). "
                                       "Avoid on the command line; prefer the prompt or env var.")
@click.pass_context
def login(ctx, username, password):
    """Log in with your SCELE username and password and store the session cookie."""
    code = terminal_login(username, password)
    _out(ctx, {"ok": code == 0, "action": "login"})


@main.command()
@click.pass_context
def logout(ctx):
    """Delete the stored session cookie."""
    clear_cookies()
    _out(ctx, {"ok": True, "action": "logout"})


@main.command()
@click.pass_context
def whoami(ctx):
    """Report whether the stored session is valid."""
    s = _session(ctx)
    if s.is_authenticated():
        _out(ctx, {"ok": True, "authenticated": True,
                   "base_url": base_url(), "sesskey": s.sesskey()})
    else:
        fail("not authenticated; run `scele login`", code="not_authenticated")


@main.command()
@click.pass_context
def courses(ctx):
    """List the courses on your dashboard."""
    s = _session(ctx)
    _out(ctx, _guard(lambda: api.my_courses(s)))


@main.command()
@click.option("--id", "category_id", help="Parent category id to list children of.")
@click.pass_context
def categories(ctx, category_id):
    """Browse the course category tree."""
    s = _session(ctx)
    _out(ctx, _guard(lambda: api.categories(s, category_id)))


@main.command("category")
@click.argument("category_id")
@click.pass_context
def category_courses(ctx, category_id):
    """List courses inside a category."""
    s = _session(ctx)
    _out(ctx, _guard(lambda: api.courses_in_category(s, category_id)))


@main.command()
@click.argument("course_id")
@click.pass_context
def course(ctx, course_id):
    """Show a course outline (sections and activities)."""
    s = _session(ctx)
    _out(ctx, _guard(lambda: api.course(s, course_id)))


@main.command()
@click.argument("course_id")
@click.pass_context
def forums(ctx, course_id):
    """List the forums in a course."""
    s = _session(ctx)
    _out(ctx, _guard(lambda: api.forums(s, course_id)))


@main.command()
@click.argument("forum_id")
@click.pass_context
def forum(ctx, forum_id):
    """List discussions in a forum."""
    s = _session(ctx)
    _out(ctx, _guard(lambda: api.forum(s, forum_id)))


@main.command()
@click.argument("discussion_id")
@click.pass_context
def thread(ctx, discussion_id):
    """Show the posts in a discussion thread."""
    s = _session(ctx)
    _out(ctx, _guard(lambda: api.thread(s, discussion_id)))


@main.command()
@click.argument("course_id")
@click.pass_context
def assignments(ctx, course_id):
    """List assignments in a course."""
    s = _session(ctx)
    _out(ctx, _guard(lambda: api.assignments(s, course_id)))


@main.command()
@click.argument("cmid")
@click.pass_context
def assignment(ctx, cmid):
    """Show an assignment's submission status."""
    s = _session(ctx)
    _out(ctx, _guard(lambda: api.assignment(s, cmid)))


@main.command()
@click.argument("course_id")
@click.pass_context
def resources(ctx, course_id):
    """List downloadable file/folder resources in a course."""
    s = _session(ctx)
    _out(ctx, _guard(lambda: api.resources(s, course_id)))


@main.command()
@click.pass_context
def announcements(ctx):
    """Show front-page / dashboard announcements."""
    s = _session(ctx)
    _out(ctx, _guard(lambda: api.announcements(s)))


@main.command()
@click.argument("course_id")
@click.option("--instance", required=True, help="Self-enrol instance id (from the enrol page).")
@click.option("--key", default="", help="Enrolment key, if the course requires one.")
@click.pass_context
def enrol(ctx, course_id, instance, key):
    """Self-enrol into a course."""
    s = _session(ctx)
    ok = _guard(lambda: api.enrol(s, course_id, instance, key))
    _out(ctx, {"ok": bool(ok), "action": "enrol", "course_id": course_id, "verified": bool(ok)})


@main.command()
@click.argument("forum_id")
@click.option("--discussion", help="Subscribe to a single discussion id instead of the forum.")
@click.pass_context
def subscribe(ctx, forum_id, discussion):
    """Toggle subscription to a forum or discussion."""
    s = _session(ctx)
    ok = _guard(lambda: api.forum_subscribe(s, forum_id, discussion))
    _out(ctx, {"ok": bool(ok), "action": "subscribe",
               "forum_id": forum_id, "discussion_id": discussion})


@main.command()
@click.argument("forum_id")
@click.option("--subject", required=True)
@click.option("--message", required=True)
@click.option("--yes", is_flag=True, help="Skip the confirmation prompt.")
@click.pass_context
def post(ctx, forum_id, subject, message, yes):
    """Start a new discussion in a forum."""
    if not yes:
        click.confirm("Post this new discussion to the forum?", abort=True, err=True)
    s = _session(ctx)
    url = _guard(lambda: api.forum_post(s, forum_id, subject, message))
    _out(ctx, {"ok": True, "action": "post", "forum_id": forum_id, "url": url})


@main.command()
@click.argument("post_id")
@click.option("--message", required=True)
@click.option("--yes", is_flag=True, help="Skip the confirmation prompt.")
@click.pass_context
def reply(ctx, post_id, message, yes):
    """Reply to a forum post."""
    if not yes:
        click.confirm("Post this reply?", abort=True, err=True)
    s = _session(ctx)
    url = _guard(lambda: api.forum_reply(s, post_id, message))
    _out(ctx, {"ok": True, "action": "reply", "post_id": post_id, "url": url})


@main.command()
@click.argument("target")
@click.option("-o", "--out-dir", default=".", type=click.Path(file_okay=False), help="Output dir.")
@click.pass_context
def download(ctx, target, out_dir):
    """Download a resource cmid or a pluginfile URL."""
    s = _session(ctx)
    dest = _guard(lambda: api.download(s, target, Path(out_dir)))
    _out(ctx, {"ok": True, "action": "download", "path": str(dest)})


@main.command()
def tui():
    """Launch the interactive TUI.

    Requires the 'tui' extra: pip install scele-cli[tui]
    """
    try:
        from .tui.app import SceleApp
    except ImportError:
        raise click.ClickException(
            "The TUI requires the 'textual' package.\n"
            "Install it with:  pip install scele-cli[tui]\n"
            "Or with pipx:     pipx inject scele-cli textual"
        )
    app = SceleApp()
    app.run()


if __name__ == "__main__":
    main()
