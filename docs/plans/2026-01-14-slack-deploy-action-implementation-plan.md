# Slack Deploy Action Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build a reusable composite GitHub Action that generates a compact Slack deploy notification (attachment-style) with English default and optional Chinese labels.

**Architecture:** A composite action calls a small Python script to build a Slack payload JSON from GitHub event data and inputs. The payload is sent via `slackapi/slack-github-action@v2` using `method: chat.postMessage` and `payload-file-path`.

**Tech Stack:** GitHub Actions (composite), Python 3 standard library, Slack attachments payload format.

### Task 1: Add payload generator with tests (TDD)

**Files:**
- Create: `scripts/__init__.py`
- Create: `scripts/generate_payload.py`
- Create: `tests/test_generate_payload.py`

**Step 1: Write the failing test**

```python
import unittest
from scripts.generate_payload import build_payload, PayloadConfig

class TestGeneratePayload(unittest.TestCase):
    def setUp(self):
        self.event = {
            "head_commit": {"message": "feat: update deploy"},
            "sender": {"avatar_url": "https://example.com/avatar.png"},
        }
        self.common = {
            "ref": "refs/heads/main",
            "event_name": "push",
            "server_url": "https://github.com",
            "repository": "forecho/example",
            "run_id": "12345",
            "sha": "abcdef1234567890",
            "actor": "forecho",
            "channel_id": "C123",
        }

    def test_build_payload_en(self):
        config = PayloadConfig(language="en", service_name="Deploy", color="#2eb886")
        payload = build_payload(self.event, self.common, config)
        attachment = payload["attachments"][0]
        self.assertEqual(attachment["fields"][0]["title"], "Ref")
        self.assertIn("Deploy", attachment["fields"][2]["value"])
        self.assertIn("abcdef1", attachment["fields"][3]["value"])

    def test_build_payload_zh(self):
        config = PayloadConfig(language="zh", service_name="Deploy", color="#2eb886")
        payload = build_payload(self.event, self.common, config)
        attachment = payload["attachments"][0]
        self.assertEqual(attachment["fields"][1]["title"], "事件")
        self.assertTrue(attachment["text"].startswith("*消息*"))

if __name__ == "__main__":
    unittest.main()
```

**Step 2: Run test to verify it fails**

Run: `python3 -m unittest tests/test_generate_payload.py -v`

Expected: FAIL with `ModuleNotFoundError: No module named 'scripts'` or missing functions.

**Step 3: Write minimal implementation**

```python
import json
import os
from dataclasses import dataclass
from typing import Dict, Any

LABELS = {
    "en": {
        "ref": "Ref",
        "event": "Event",
        "actions_url": "Actions URL",
        "commit": "Commit",
        "message": "Message",
        "footer": "Powered by GitHub Actions | Triggered on this workflow run",
    },
    "zh": {
        "ref": "Ref",
        "event": "事件",
        "actions_url": "Actions URL",
        "commit": "提交",
        "message": "消息",
        "footer": "由 GitHub Actions 提供 | 由本次工作流触发",
    },
}

@dataclass
class PayloadConfig:
    language: str
    service_name: str
    color: str
    footer_text: str = ""
    footer_icon: str = ""


def build_payload(event: Dict[str, Any], common: Dict[str, str], config: PayloadConfig) -> Dict[str, Any]:
    lang = "zh" if config.language == "zh" else "en"
    labels = LABELS[lang]
    footer_text = config.footer_text or labels["footer"]
    footer_icon = config.footer_icon or "https://github.githubassets.com/assets/GitHub-Mark-ea2971cee799.png"
    short_sha = common["sha"][:7]
    message = event.get("head_commit", {}).get("message") or "N/A"

    actions_url = f"{common['server_url']}/{common['repository']}/actions/runs/{common['run_id']}"
    commit_url = f"{common['server_url']}/{common['repository']}/commit/{common['sha']}"

    payload = {
        "channel": common["channel_id"],
        "text": f"{config.service_name} notification for {common['repository']}",
        "attachments": [
            {
                "color": config.color,
                "author_name": common["actor"],
                "author_icon": event.get("sender", {}).get("avatar_url", ""),
                "fields": [
                    {"title": labels["ref"], "value": common["ref"], "short": True},
                    {"title": labels["event"], "value": common["event_name"], "short": True},
                    {
                        "title": labels["actions_url"],
                        "value": f"<{actions_url}|{config.service_name}>",
                        "short": True,
                    },
                    {
                        "title": labels["commit"],
                        "value": f"<{commit_url}|{short_sha}>",
                        "short": True,
                    },
                ],
                "text": f"*{labels['message']}*\n{message}",
                "footer": footer_text,
                "footer_icon": footer_icon,
                "mrkdwn_in": ["fields", "text"],
            }
        ],
    }
    return payload


def main() -> None:
    event_path = os.environ.get("GITHUB_EVENT_PATH", "")
    if not event_path:
        raise SystemExit("GITHUB_EVENT_PATH is required")
    with open(event_path, "r", encoding="utf-8") as handle:
        event = json.load(handle)

    common = {
        "ref": os.environ.get("GITHUB_REF", ""),
        "event_name": os.environ.get("GITHUB_EVENT_NAME", ""),
        "server_url": os.environ.get("GITHUB_SERVER_URL", ""),
        "repository": os.environ.get("GITHUB_REPOSITORY", ""),
        "run_id": os.environ.get("GITHUB_RUN_ID", ""),
        "sha": os.environ.get("GITHUB_SHA", ""),
        "actor": os.environ.get("GITHUB_ACTOR", ""),
        "channel_id": os.environ.get("SLACK_DEPLOY_CHANNEL_ID", ""),
    }

    config = PayloadConfig(
        language=os.environ.get("SLACK_DEPLOY_LANGUAGE", "en"),
        service_name=os.environ.get("SLACK_DEPLOY_SERVICE_NAME", "Deploy"),
        color=os.environ.get("SLACK_DEPLOY_COLOR", "#2eb886"),
        footer_text=os.environ.get("SLACK_DEPLOY_FOOTER_TEXT", ""),
        footer_icon=os.environ.get("SLACK_DEPLOY_FOOTER_ICON", ""),
    )

    output_path = os.environ.get("SLACK_DEPLOY_OUTPUT", "payload.json")
    payload = build_payload(event, common, config)
    with open(output_path, "w", encoding="utf-8") as handle:
        json.dump(payload, handle, ensure_ascii=True)


if __name__ == "__main__":
    main()
```

**Step 4: Run test to verify it passes**

Run: `python3 -m unittest tests/test_generate_payload.py -v`

Expected: PASS (2 tests).

**Step 5: Commit**

```bash
git add scripts/__init__.py scripts/generate_payload.py tests/test_generate_payload.py
git commit -m "Add Slack payload generator"
```

### Task 2: Add composite action definition

**Files:**
- Create: `action.yml`

**Step 1: Write the failing test**

No automated test for composite action YAML.

**Step 2: Write minimal implementation**

```yaml
name: "Slack Deploy Action"
description: "Send deploy notifications to Slack using attachment-style layout"
author: "forecho"
branding:
  icon: "bell"
  color: "green"
inputs:
  slack_bot_token:
    description: "Slack Bot Token"
    required: true
  slack_channel_id:
    description: "Slack channel ID"
    required: true
  language:
    description: "Language for labels: en or zh"
    required: false
    default: "en"
  service_name:
    description: "Label used in the Actions URL field"
    required: false
    default: "Deploy"
  color:
    description: "Attachment color"
    required: false
    default: "#2eb886"
  footer_text:
    description: "Footer text override"
    required: false
    default: ""
  footer_icon:
    description: "Footer icon URL"
    required: false
    default: ""

runs:
  using: "composite"
  steps:
    - name: Generate Slack payload
      shell: bash
      env:
        SLACK_DEPLOY_LANGUAGE: ${{ inputs.language }}
        SLACK_DEPLOY_SERVICE_NAME: ${{ inputs.service_name }}
        SLACK_DEPLOY_COLOR: ${{ inputs.color }}
        SLACK_DEPLOY_FOOTER_TEXT: ${{ inputs.footer_text }}
        SLACK_DEPLOY_FOOTER_ICON: ${{ inputs.footer_icon }}
        SLACK_DEPLOY_CHANNEL_ID: ${{ inputs.slack_channel_id }}
        SLACK_DEPLOY_OUTPUT: ${{ runner.temp }}/slack-payload.json
      run: python3 ${{ github.action_path }}/scripts/generate_payload.py

    - name: Send Slack notification
      uses: slackapi/slack-github-action@v2
      with:
        token: ${{ inputs.slack_bot_token }}
        method: chat.postMessage
        payload-file-path: ${{ runner.temp }}/slack-payload.json
```

**Step 3: Commit**

```bash
git add action.yml
git commit -m "Add composite action definition"
```

### Task 3: Add documentation and example

**Files:**
- Create: `README.md`
- Create: `examples/deploy-notify.yml`

**Step 1: Write README**

```markdown
# Slack Deploy Action

Reusable Slack deploy notification action with a compact attachment-style layout. Defaults to English, supports Chinese via `language: zh`.

## Usage

```yaml
- uses: forecho/slack-deploy-action@v1
  with:
    slack_bot_token: ${{ secrets.SLACK_BOT_TOKEN }}
    slack_channel_id: ${{ secrets.SLACK_CHANNEL_ID }}
    language: en
    service_name: Deploy
```

## Chinese

```yaml
- uses: forecho/slack-deploy-action@v1
  with:
    slack_bot_token: ${{ secrets.SLACK_BOT_TOKEN }}
    slack_channel_id: ${{ secrets.SLACK_CHANNEL_ID }}
    language: zh
    service_name: 部署
```

## Inputs
- `slack_bot_token` (required)
- `slack_channel_id` (required)
- `language` (optional, default `en`, supports `zh`)
- `service_name` (optional, default `Deploy`)
- `color` (optional, default `#2eb886`)
- `footer_text` (optional)
- `footer_icon` (optional)
```

**Step 2: Write example workflow**

```yaml
name: Deploy Notify
on:
  push:
    branches: [main]

jobs:
  notify:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: forecho/slack-deploy-action@v1
        with:
          slack_bot_token: ${{ secrets.SLACK_BOT_TOKEN }}
          slack_channel_id: ${{ secrets.SLACK_CHANNEL_ID }}
          language: en
          service_name: Deploy
```

**Step 3: Commit**

```bash
git add README.md examples/deploy-notify.yml
git commit -m "Add README and example workflow"
```

### Task 4: Final verification

**Files:**
- Test: `tests/test_generate_payload.py`

**Step 1: Run tests**

Run: `python3 -m unittest tests/test_generate_payload.py -v`

Expected: PASS (2 tests)

**Step 2: Commit (if needed)**

Only if any changes were required.
