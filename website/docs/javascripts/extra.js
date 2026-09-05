const REPO = "Andrew4Coding/scele-cli";

const INSTALL = {
  unix: {
    label: "Linux / macOS",
    code: "curl -fsSL https://raw.githubusercontent.com/Andrew4Coding/scele-cli/main/install-bin.sh | sh",
  },
  windows: {
    label: "Windows (PowerShell)",
    code: "irm https://raw.githubusercontent.com/Andrew4Coding/scele-cli/main/install-bin.ps1 | iex",
  },
};

function detectPlatform() {
  const s = `${navigator.platform || ""} ${navigator.userAgent || ""}`.toLowerCase();
  if (s.includes("win")) return "windows";
  return "unix";
}

// Hero install command, matched to the visitor's platform.
function initInstall() {
  const root = document.querySelector("[data-install-command]");
  if (!root) return;

  const osEl = root.querySelector("[data-install-os]");
  const codeEl = root.querySelector("[data-install-code]");
  const copyEl = root.querySelector("[data-install-copy]");

  const pick = INSTALL[detectPlatform()];
  osEl.textContent = pick.label;
  codeEl.textContent = pick.code;

  copyEl.addEventListener("click", async () => {
    try {
      await navigator.clipboard.writeText(codeEl.textContent);
      const prev = copyEl.textContent;
      copyEl.textContent = "Copied";
      setTimeout(() => { copyEl.textContent = prev; }, 1500);
    } catch (e) {
      /* clipboard blocked: no-op */
    }
  });
}

// Screenshots that have not been added yet stay hidden so no broken icons appear.
function initPlaceholders() {
  document.querySelectorAll(".feature-card__img, .cmd-shot").forEach((img) => {
    const mark = () => {
      img.classList.add("is-placeholder");
      img.style.display = "none";
    };
    if (img.complete && img.naturalWidth === 0) mark();
    img.addEventListener("error", mark);
  });
}

// Report form: builds a prefilled GitHub "new issue" URL and opens it.
function initIssueForm() {
  const btn = document.getElementById("issue-open");
  if (!btn) return;

  const val = (id) => (document.getElementById(id)?.value || "").trim();

  const LABELS = {
    bug: "bug",
    docs: "documentation",
    feature: "enhancement",
    question: "question",
  };
  const PREFIX = {
    bug: "bug",
    docs: "docs",
    feature: "feature",
    question: "question",
  };

  btn.addEventListener("click", () => {
    const kind = val("issue-kind") || "bug";
    const title = val("issue-title");

    if (!title) {
      document.getElementById("issue-title").focus();
      return;
    }

    const body = [
      "### What happened",
      "",
      val("issue-body") || "_(describe the problem)_",
      "",
      "### Command",
      "",
      "```bash",
      val("issue-command") || "scele …",
      "```",
      "",
      "### Environment",
      "",
      `- scele version: ${val("issue-version") || "_unknown_"}`,
      `- Platform: ${navigator.platform || "unknown"}`,
      "",
      "<!-- Please make sure no token, password or personal data is included above. -->",
    ].join("\n");

    const url = new URL(`https://github.com/${REPO}/issues/new`);
    url.searchParams.set("title", `${PREFIX[kind]}: ${title}`);
    url.searchParams.set("body", body);
    url.searchParams.set("labels", LABELS[kind]);

    window.open(url.toString(), "_blank", "noopener");
  });
}

// Credits: contributor list, read live from the GitHub API with local fallback.
async function initContributors() {
  const root = document.querySelector("[data-contributors]");
  if (!root) return;

  const renderContributors = (people) => {
    root.innerHTML = "";
    for (const p of people) {
      const a = document.createElement("a");
      a.className = "contributor";
      a.href = p.html_url || `https://github.com/${p.login}`;
      a.target = "_blank";
      a.rel = "noopener";

      const img = document.createElement("img");
      img.src = p.avatar_url ? `${p.avatar_url}&s=64` : `https://github.com/${p.login}.png?size=64`;
      img.alt = "";
      img.loading = "lazy";

      const meta = document.createElement("div");
      const name = document.createElement("div");
      name.className = "contributor__name";
      name.textContent = p.login;
      const count = document.createElement("div");
      count.className = "contributor__count";
      count.textContent = p.contributions ? `${p.contributions} commit${p.contributions === 1 ? "" : "s"}` : "Contributor";
      meta.append(name, count);

      a.append(img, meta);
      root.appendChild(a);
    }
  };

  const fallbacks = [
    { login: "Andrew4Coding", html_url: "https://github.com/Andrew4Coding", avatar_url: "https://github.com/Andrew4Coding.png", contributions: 50 },
    { login: "crlnravel", html_url: "https://github.com/crlnravel", avatar_url: "https://github.com/crlnravel.png", contributions: 12 }
  ];

  try {
    const res = await fetch(
      `https://api.github.com/repos/${REPO}/contributors?per_page=100`,
      { headers: { Accept: "application/vnd.github+json" } }
    );
    if (!res.ok) throw new Error(res.status);

    const people = (await res.json()).filter((p) => p.type === "User");
    if (!people.length) {
      renderContributors(fallbacks);
      return;
    }
    renderContributors(people);
  } catch (e) {
    // Graceful fallback showing core contributors
    renderContributors(fallbacks);
  }
}

function init() {
  initInstall();
  initPlaceholders();
  initIssueForm();
  initContributors();
}

if (window.document$ && typeof window.document$.subscribe === "function") {
  window.document$.subscribe(init);
} else {
  document.addEventListener("DOMContentLoaded", init);
}
