---
hide:
  - toc
  - navigation
  - footer
---

<div class="hero" markdown>

# scele-cli { .hero__title }

A command-line client for **SCELE**, the Moodle of Fakultas Ilmu Komputer,
Universitas Indonesia. Authenticate once, then drive your courses, forums,
and assignments straight from the terminal.
{ .hero__tagline }

<div class="hero__install" data-install-command>
  <span class="hero__install-os" data-install-os>Detecting your platform…</span>
  <div class="hero__install-row">
    <code data-install-code>curl -fsSL https://raw.githubusercontent.com/Andrew4Coding/scele-cli/main/install-bin.sh | sh</code>
    <button class="hero__copy" data-install-copy type="button" aria-label="Copy install command">Copy</button>
  </div>
</div>

<div class="hero__cta" markdown>
[Get started](commands/index.md){ .md-button .md-button--primary }
[View on GitHub](https://github.com/Andrew4Coding/scele-cli){ .md-button }
</div>

</div>

## Features { .feature-heading }

<div class="feature-grid" markdown>

<div class="feature-card" markdown>
<div class="feature-card__badge"><span class="feature-card__prompt">$</span> <code>scele login</code></div>
### Login
Exchange your username and password for a Moodle web-service token. Only the
token is stored, never the password. No browser, no CAPTCHA.
</div>

<div class="feature-card" markdown>
<div class="feature-card__badge"><span class="feature-card__prompt">$</span> <code>scele courses</code></div>
### Courses & grades
List the courses you are enrolled in, read a section-by-section outline, see
enrolled people, and pull your grade items for any course.
</div>

<div class="feature-card" markdown>
<div class="feature-card__badge"><span class="feature-card__prompt">$</span> <code>scele deadlines</code></div>
### Deadlines & calendar
Upcoming deadlines across every course, calendar events, and your SCELE
notifications, each rendered in `YYYY-MM-DD HH:MM WIB`.
</div>

<div class="feature-card" markdown>
<div class="feature-card__badge"><span class="feature-card__prompt">$</span> <code>scele forum</code></div>
### Forums
Browse forums in a course, list discussions, and read whole threads with
nesting (parent + depth). Post a new topic or reply to an exact post.
</div>

<div class="feature-card" markdown>
<div class="feature-card__badge"><span class="feature-card__prompt">$</span> <code>scele assignments</code></div>
### Assignments
Check submission status and due dates, read the instructions and attachments,
and submit text or a file with an explicit confirmation step.
</div>

<div class="feature-card" markdown>
<div class="feature-card__badge"><span class="feature-card__prompt">$</span> <code>scele download</code></div>
### Resources
List every downloadable file in a course with its `fileurl`, then download by
pluginfile URL or by resource `cmid`.
</div>

<div class="feature-card" markdown>
<div class="feature-card__badge"><span class="feature-card__prompt">$</span> <code>scele watch</code></div>
### Watch
Re-run any `scele-cli` subcommand on an interval, diff its JSON output, log events,
and POST changes to a webhook: foreground stream or background daemon.
</div>

</div>

## Install { .feature-heading }

=== "Linux / macOS"

    Prebuilt binary (no Python required):

    ``` bash
    curl -fsSL https://raw.githubusercontent.com/Andrew4Coding/scele-cli/main/install-bin.sh | sh
    ```

    Then open a new terminal:

    ``` bash
    scele login
    scele courses
    ```

=== "Windows (PowerShell)"

    Prebuilt binary (no Python required):

    ``` powershell
    irm https://raw.githubusercontent.com/Andrew4Coding/scele-cli/main/install-bin.ps1 | iex
    ```

    Then open a new terminal:

    ``` powershell
    scele login
    scele courses
    ```

=== "pipx (any OS with Python)"

    ``` bash
    pipx install git+https://github.com/Andrew4Coding/scele-cli.git
    ```

=== "Agent skill"

    ``` bash
    npx skills add Andrew4Coding/scele-cli
    ```

The binary installer fetches the latest release bundle for your OS/arch, verifies its
SHA-256, unpacks it to `~/.local/lib/scele-app`, and links `scele` onto your `PATH`.
Pin a version with `SCELE_VERSION=v0.2.0`.

<footer class="site-foot" markdown>
[GitHub](https://github.com/Andrew4Coding/scele-cli) &middot;
[Docs](commands/index.md) &middot;
[Report an issue](report.md) &middot;
[Credits](credits.md) &middot;
[Releases](https://github.com/Andrew4Coding/scele-cli/releases) &middot;
[MIT License](https://github.com/Andrew4Coding/scele-cli/blob/main/LICENSE.md)
</footer>
