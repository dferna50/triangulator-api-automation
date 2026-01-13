const fs = require('fs');
const path = require('path');
const https = require('https');

// Validate required environment variables
if (!process.env.SLACK_WEBHOOK_URL) {
  console.error('Error: Missing SLACK_WEBHOOK_URL environment variable');
  console.error('Please set SLACK_WEBHOOK_URL in your GitHub secrets');
  process.exit(1);
}

// Load pytest JSON report
const reportPath = path.join(__dirname, 'reports', 'report.json');
if (!fs.existsSync(reportPath)) {
  console.error(`Error: Report file not found at ${reportPath}`);
  process.exit(1);
}

const reportData = JSON.parse(fs.readFileSync(reportPath, 'utf-8'));

// Extract test statistics
const summary = reportData.summary || {};
const passed = summary.passed || 0;
const failed = summary.failed || 0;
const skipped = summary.skipped || 0;
const total = summary.total || 0;

// Calculate duration
const durationSeconds = reportData.duration || 0;
const minutes = Math.floor(durationSeconds / 60);
const seconds = Math.floor(durationSeconds % 60);
const formattedDuration = `${minutes}m ${seconds}s`;

// Determine test status and color
const testStatus = failed > 0 ? 'FAILED' : 'PASSED';
const statusColor = failed > 0 ? '#FF0000' : '#36A64F';
const statusEmoji = failed > 0 ? '❌' : '✅';

// Get GitHub context if available (for CI/CD)
const repoName = process.env.GITHUB_REPOSITORY || 'triangulator-api-automation';
const runId = process.env.GITHUB_RUN_ID || 'local';
const runUrl = process.env.GITHUB_SERVER_URL && process.env.GITHUB_REPOSITORY && process.env.GITHUB_RUN_ID
  ? `${process.env.GITHUB_SERVER_URL}/${process.env.GITHUB_REPOSITORY}/actions/runs/${process.env.GITHUB_RUN_ID}`
  : null;
const branch = process.env.GITHUB_REF_NAME || 'unknown';
const actor = process.env.GITHUB_ACTOR || 'unknown';

// Build Slack message with rich formatting
const slackMessage = {
  text: `${statusEmoji} API Test Report: ${testStatus}`,
  blocks: [
    {
      type: 'header',
      text: {
        type: 'plain_text',
        text: `${statusEmoji} API Automation Test Results`,
        emoji: true
      }
    },
    {
      type: 'section',
      fields: [
        {
          type: 'mrkdwn',
          text: `*Status:*\n${testStatus}`
        },
        {
          type: 'mrkdwn',
          text: `*Branch:*\n${branch}`
        },
        {
          type: 'mrkdwn',
          text: `*Duration:*\n${formattedDuration}`
        },
        {
          type: 'mrkdwn',
          text: `*Triggered by:*\n${actor}`
        }
      ]
    },
    {
      type: 'section',
      fields: [
        {
          type: 'mrkdwn',
          text: `*Total Tests:*\n${total}`
        },
        {
          type: 'mrkdwn',
          text: `*✅ Passed:*\n${passed}`
        },
        {
          type: 'mrkdwn',
          text: `*❌ Failed:*\n${failed}`
        },
        {
          type: 'mrkdwn',
          text: `*⏭️ Skipped:*\n${skipped}`
        }
      ]
    }
  ],
  attachments: [
    {
      color: statusColor,
      fields: [
        {
          title: 'Repository',
          value: repoName,
          short: true
        },
        {
          title: 'Run ID',
          value: runId,
          short: true
        }
      ]
    }
  ]
};

// Add link to GitHub Actions run if available
if (runUrl) {
  slackMessage.blocks.push({
    type: 'actions',
    elements: [
      {
        type: 'button',
        text: {
          type: 'plain_text',
          text: '🔗 View Full Report',
          emoji: true
        },
        url: runUrl,
        style: failed > 0 ? 'danger' : 'primary'
      }
    ]
  });
}

// Send to Slack using webhook
const webhookUrl = new URL(process.env.SLACK_WEBHOOK_URL);
const postData = JSON.stringify(slackMessage);

const options = {
  hostname: webhookUrl.hostname,
  path: webhookUrl.pathname,
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Content-Length': Buffer.byteLength(postData)
  }
};

const req = https.request(options, (res) => {
  let data = '';
  
  res.on('data', (chunk) => {
    data += chunk;
  });
  
  res.on('end', () => {
    if (res.statusCode === 200) {
      console.log('✅ Slack notification sent successfully!');
      console.log(`Test Results: ${passed} passed, ${failed} failed, ${skipped} skipped`);
    } else {
      console.error(`❌ Failed to send Slack notification. Status: ${res.statusCode}`);
      console.error(`Response: ${data}`);
      process.exit(1);
    }
  });
});

req.on('error', (error) => {
  console.error('❌ Error sending Slack notification:', error.message);
  process.exit(1);
});

req.write(postData);
req.end();