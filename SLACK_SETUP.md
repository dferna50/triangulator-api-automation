# Slack Notification Setup Guide (Email Integration)

This guide will help you configure Slack notifications for your API automation test results using **Email Integration** (no Slack app creation required).

## Prerequisites

- Access to your Slack workspace (no admin required)
- Admin access to your GitHub repository
- A Gmail account for sending emails

## Why Email Integration?

Since your Slack admin has blocked app creation, we're using Slack's built-in email integration feature. Each Slack channel can receive emails at a unique email address, and those emails appear as messages in the channel.

## Step 1: Get Your Slack Channel Email Address

1. **Open the Slack channel** where you want to receive test notifications (e.g., `#qa-automation`, `#test-results`)

2. **Access Channel Settings**
   - Click the channel name at the top
   - Select **"Integrations"** tab
   - Look for **"Send emails to this channel"** or **"Email"** section

3. **Get the Email Address**
   - You'll see an email address like: `your-workspace-abc123@slack-mail.com` or `channel-name.xyz@company.slack.com`
   - Copy this email address
   - **Note**: If you don't see this option, ask your Slack admin to enable email integration for the channel

## Step 2: Create Gmail App Password

For security, Gmail requires an "App Password" instead of your regular password when apps send emails.

1. **Enable 2-Factor Authentication** (if not already enabled)
   - Go to: https://myaccount.google.com/security
   - Enable "2-Step Verification"

2. **Create App Password**
   - Go to: https://myaccount.google.com/apppasswords
   - Select app: **"Mail"**
   - Select device: **"Other (Custom name)"**
   - Enter name: `GitHub Actions Test Reporter`
   - Click **"Generate"**
   - Copy the 16-character password (looks like: `abcd efgh ijkl mnop`)
   - **IMPORTANT**: Save this password - you won't be able to see it again!

## Step 3: Add Secrets to GitHub Repository

1. **Navigate to your GitHub repository**
   - Go to: `https://github.com/dferna50/triangulator-api-automation`

2. **Access Repository Settings**
   - Click **"Settings"** tab (top right)
   - In the left sidebar, click **"Secrets and variables"** → **"Actions"**

3. **Add Three Secrets** (click "New repository secret" for each):

   **Secret 1: Slack Channel Email**
   - Name: `SLACK_EMAIL`
   - Value: Your Slack channel email from Step 1
   - Example: `your-workspace-abc123@slack-mail.com`
   - Click **"Add secret"**

   **Secret 2: Gmail Username**
   - Name: `GMAIL_USER`
   - Value: Your Gmail address
   - Example: `your-email@gmail.com`
   - Click **"Add secret"**

   **Secret 3: Gmail App Password**
   - Name: `GMAIL_APP_PASSWORD`
   - Value: The 16-character app password from Step 2
   - Example: `abcdefghijklmnop` (without spaces)
   - Click **"Add secret"**

## Step 4: Test the Integration

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

1. **Use App Passwords, never regular passwords**
   - Gmail App Passwords are revocable and app-specific
   - If compromised, revoke and create a new one without changing your main password

2. **Never commit credentials to git**
   - Always use GitHub Secrets for sensitive data
   - Credentials are never exposed in logs or code

3. **Use environment variables**
   - The script reads credentials from environment only
   - No hardcoded passwords in the codebase

4. **Minimal Gmail permissions**
   - App Password only allows sending emails
   - It cannot read your emails or access other Google services

5. **Credential rotation**
   - Revoke App Password: https://myaccount.google.com/apppasswords
   - Create a new App Password and update GitHub secret
   - Consider rotating every 90 days

6. **Slack channel security**
   - Only people in the channel can see the messages
   - Use a dedicated channel for test results if needed

## Troubleshooting

### No notification received in Slack
1. **Check GitHub Actions logs** for error messages
2. **Verify all 3 secrets are set correctly**:
   - `SLACK_EMAIL` - Slack channel email address
   - `GMAIL_USER` - Your Gmail address
   - `GMAIL_APP_PASSWORD` - 16-character app password
3. **Check Gmail App Password**:
   - Make sure you copied it without spaces
   - Try creating a new App Password
4. **Verify Slack channel email**:
   - Make sure the channel's email integration is enabled
   - Try sending a test email manually to that address

### "Missing SLACK_EMAIL" or credential errors
- One or more secrets are not set in GitHub
- Follow Step 3 to add all three required secrets

### Gmail authentication failed
1. **Verify 2FA is enabled** on your Gmail account
2. **Recreate the App Password**:
   - Revoke old one at https://myaccount.google.com/apppasswords
   - Create new one and update `GMAIL_APP_PASSWORD` secret
3. **Check for typos** - App password should be 16 characters, no spaces

### Email sent but not appearing in Slack
1. **Check the Slack channel** - it might be there but not notifying
2. **Verify email integration is enabled** for that channel
3. **Ask Slack admin** to check if email integration is globally disabled
4. **Try a different channel** - some channels may have restrictions

## Customizing Notifications

To customize the email format, edit `sendReport.js`:

- **Change colors**: Modify the HTML styles in `htmlBody`
- **Add fields**: Add new rows to the HTML tables
- **Change subject**: Modify the `subject` field in `mailOptions`
- **Send to multiple channels**: Add multiple email addresses (comma-separated) to `SLACK_EMAIL` secret

## Alternative: Using a Different Email Provider

If you don't want to use Gmail, you can modify `sendReport.js` to use other providers:

**Outlook/Office 365:**
```javascript
const transporter = nodemailer.createTransport({
  host: 'smtp.office365.com',
  port: 587,
  secure: false,
  auth: {
    user: process.env.OUTLOOK_USER,
    pass: process.env.OUTLOOK_PASSWORD
  }
});
```

**Custom SMTP Server:**
```javascript
const transporter = nodemailer.createTransport({
  host: 'your-smtp-server.com',
  port: 587,
  secure: false,
  auth: {
    user: process.env.SMTP_USER,
    pass: process.env.SMTP_PASSWORD
  }
});
```

## Additional Resources

- [Slack Email Integration Guide](https://slack.com/help/articles/206819278-Send-emails-to-Slack)
- [Gmail App Passwords](https://support.google.com/accounts/answer/185833)
- [GitHub Secrets Documentation](https://docs.github.com/en/actions/security-guides/encrypted-secrets)
- [Nodemailer Documentation](https://nodemailer.com/)
