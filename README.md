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
