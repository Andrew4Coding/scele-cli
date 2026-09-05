---
icon: lucide/bug
hide:
  - toc
---

# Report an issue

Found a bug, a command that returns the wrong shape, or something missing from these docs?

<div class="issue-form" markdown>

<div class="issue-field">
  <label for="issue-kind">What kind of issue is it?</label>
  <select id="issue-kind">
    <option value="bug">Bug: a command fails or returns the wrong thing</option>
    <option value="docs">Documentation Issue: something here is wrong or missing</option>
    <option value="feature">Feature request: something scele should be able to do</option>
    <option value="question">Question: how do I use a specific feature?</option>
  </select>
</div>

<div class="issue-field">
  <label for="issue-title">Title</label>
  <input id="issue-title" type="text" placeholder="scele deadlines returns an empty list after login" />
</div>

<div class="issue-field">
  <label for="issue-command">Command you ran <span>(optional)</span></label>
  <input id="issue-command" type="text" placeholder="scele deadlines --days 14" />
</div>

<div class="issue-field">
  <label for="issue-body">What happened?</label>
  <textarea id="issue-body" rows="7" placeholder="What you expected, what you got instead, and anything else that helps reproduce it."></textarea>
</div>

<div class="issue-field">
  <label for="issue-version">scele version <span>(run <code>scele --version</code>)</span></label>
  <input id="issue-version" type="text" placeholder="0.2.1" />
</div>

<div class="issue-actions">
  <button type="button" id="issue-open" class="md-button md-button--primary">Open Issue in GitHub</button>
</div>

</div>