import json
import os
from dataclasses import dataclass
from typing import Any, Dict

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

DEFAULT_FOOTER_ICON = "https://github.githubassets.com/assets/GitHub-Mark-ea2971cee799.png"


@dataclass
class PayloadConfig:
    language: str
    service_name: str
    color: str
    footer_text: str = ""
    footer_icon: str = ""


def build_payload(event: Dict[str, Any], common: Dict[str, str], config: PayloadConfig) -> Dict[str, Any]:
    language = "zh" if config.language == "zh" else "en"
    labels = LABELS[language]
    footer_text = config.footer_text or labels["footer"]
    footer_icon = config.footer_icon or DEFAULT_FOOTER_ICON
    short_sha = common["sha"][:7]
    message = event.get("head_commit", {}).get("message") or "N/A"

    actions_url = f"{common['server_url']}/{common['repository']}/actions/runs/{common['run_id']}"
    commit_url = f"{common['server_url']}/{common['repository']}/commit/{common['sha']}"

    return {
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
