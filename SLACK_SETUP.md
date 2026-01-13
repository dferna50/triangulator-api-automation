# Slack Notification Setup Guide

This guide will help you configure Slack notifications for your API automation test results.

## Prerequisites

- Admin access to your Slack workspace
- Admin access to your GitHub repository

## Step 1: Create Slack Incoming Webhook

1. **Go to Slack API Console**
   - Visit: https://api.slack.com/apps
   - Click **"Create New App"**
   - Choose **"From scratch"**
   - Enter App Name: `API Test Reporter` (or your preferred name)
   - Select your workspace

2. **Enable Incoming Webhooks**
   - In your app settings, click **"Incoming Webhooks"**
   - Toggle **"Activate Incoming Webhooks"** to ON
   - Scroll down and click **"Add New Webhook to Workspace"**
   - Select the channel where you want notifications (e.g., `#qa-automation`, `#test-results`)
   - Click **"Allow"**

3. **Copy the Webhook URL**
   - You'll see a webhook URL like: `https://hooks.slack.com/services/T00000000/B00000000/XXXXXXXXXXXXXXXXXXXX`
   - **IMPORTANT**: Keep this URL secret! Anyone with this URL can post to your Slack channel

## Step 2: Add Webhook URL to GitHub Secrets

1. **Navigate to your GitHub repository**
   - Go to: `https://github.com/dferna50/triangulator-api-automation`

2. **Access Repository Settings**
   - Click **"Settings"** tab (top right)
   - In the left sidebar, click **"Secrets and variables"** → **"Actions"**

3. **Add New Secret**
   - Click **"New repository secret"**
   - Name: `SLACK_WEBHOOK_URL`
   - Value: Paste your webhook URL from Step 1
   - Click **"Add secret"**

## Step 3: Test the Integration

### Option 1: Push a commit
```bash
git commit --allow-empty -m "Test Slack notification"
git push origin main
```

### Option 2: Manually trigger workflow
1. Go to **Actions** tab in GitHub
2. Select **"API Automation Tests"** workflow
3. Click **"Run workflow"** → **"Run workflow"**

## Expected Slack Message Format

You should receive a message in your Slack channel with:

- **Header**: Test status (✅ PASSED or ❌ FAILED)
- **Test Statistics**: Total, Passed, Failed, Skipped counts
- **Metadata**: Branch, Duration, Triggered by
- **Link**: Button to view full report on GitHub Actions

### Example Message:
```
✅ API Automation Test Results

Status: PASSED          Branch: main
Duration: 2m 34s        Triggered by: dferna50

Total Tests: 219        ✅ Passed: 219
❌ Failed: 0            ⏭️ Skipped: 2

Repository: dferna50/triangulator-api-automation
Run ID: 12345678

[🔗 View Full Report]
```

## Security Best Practices ✅

1. **Never commit webhook URLs to git**
   - Always use GitHub Secrets for sensitive data
   - The webhook URL is never exposed in logs or code

2. **Use environment variables**
   - The script reads `SLACK_WEBHOOK_URL` from environment only
   - No hardcoded credentials in the codebase

3. **Minimal permissions**
   - The webhook can only post to the channel you specified
   - It cannot read messages or access other channels

4. **Webhook rotation**
   - If compromised, delete the webhook in Slack app settings
   - Create a new webhook and update the GitHub secret

## Troubleshooting

### No notification received
1. Check GitHub Actions logs for errors
2. Verify `SLACK_WEBHOOK_URL` secret is set correctly
3. Ensure the Slack channel still exists
4. Check if the app was removed from the workspace

### "Missing SLACK_WEBHOOK_URL" error
- The secret is not set in GitHub
- Follow Step 2 to add the secret

### Webhook URL expired
- Webhooks can be revoked in Slack
- Create a new webhook and update the GitHub secret

## Customizing Notifications

To customize the Slack message, edit `sendReport.js`:

- **Change colors**: Modify `statusColor` variable
- **Add fields**: Add items to `slackMessage.blocks` array
- **Change channel**: Create a new webhook for different channel

## Additional Resources

- [Slack Incoming Webhooks Documentation](https://api.slack.com/messaging/webhooks)
- [GitHub Secrets Documentation](https://docs.github.com/en/actions/security-guides/encrypted-secrets)
- [Slack Block Kit Builder](https://app.slack.com/block-kit-builder) - Design custom messages
