# Slack Deploy Action Design (2026-01-14)

## Summary
Create a reusable composite GitHub Action that wraps `slackapi/slack-github-action@v2` to send deployment notifications with a compact attachment-style layout. The action supports multiple languages with English as default and optional Chinese via configuration.

## Goals
- Provide a compact deploy notification layout matching the attachment style reference.
- Support `en` (default) and `zh` labels via an input.
- Keep implementation lightweight by delegating delivery to `slackapi/slack-github-action@v2`.
- Make the action reusable across repositories.

## Non-goals
- Full Slack API client implementation.
- Advanced routing rules or per-channel logic.
- Rich interactive workflows beyond simple links.

## Proposed Interface
Inputs:
- `slack_bot_token` (required)
- `slack_channel_id` (required)
- `language` (optional, default `en`, supports `zh`)
- `service_name` (optional, default `Deploy`)
- `color` (optional, default `#2eb886`)
- `footer_text` (optional, default `Powered by GitHub Actions | Triggered on this workflow run`)
- `footer_icon` (optional, default GitHub Mark)

Outputs: none.

## Message Layout
Use Slack attachments:
- Green color bar.
- Author: actor name + avatar.
- Fields: Ref, Event, Actions URL, Commit (short SHA).
- Text: `Message` (commit message, fallback to `N/A`).
- Footer: branding text + icon.

## Data Sources
- Event payload: `$GITHUB_EVENT_PATH`.
- Ref: `$GITHUB_REF`.
- Event name: `$GITHUB_EVENT_NAME`.
- Actions URL: `${{ github.server_url }}/${{ github.repository }}/actions/runs/${{ github.run_id }}`.
- Commit URL: `${{ github.server_url }}/${{ github.repository }}/commit/${{ github.sha }}`.
- Short SHA: first 7 chars of `$GITHUB_SHA`.

## Implementation Notes
- Composite action calls a small Python script to build `payload.json` from env and event data.
- The script emits stable YAML/JSON to avoid quoting issues in commit messages.
- The composite action passes `payload.json` to `slackapi/slack-github-action@v2` with `method: chat.postMessage` and `token`.

## Verification
- Run the action in a sample workflow on a test repo.
- Confirm layout matches the reference and links work.
- Verify `language=zh` toggles labels.

## Rollback
- Replace the action with direct Slack API calls or the previous inline payload.
