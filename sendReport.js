const fs = require('fs');
const path = require('path');
const nodemailer = require('nodemailer');

// Validate required environment variables for email-based Slack integration
if (!process.env.SLACK_EMAIL) {
  console.error('Error: Missing SLACK_EMAIL environment variable');
  console.error('Please set SLACK_EMAIL (your Slack channel email) in your GitHub secrets');
  process.exit(1);
}

if (!process.env.GMAIL_USER || !process.env.GMAIL_APP_PASSWORD) {
  console.error('Error: Missing email authentication credentials');
  console.error('Please set GMAIL_USER and GMAIL_APP_PASSWORD in your GitHub secrets');
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

// Build HTML email message for Slack
const htmlBody = `
<div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
  <h2 style="color: ${failed > 0 ? '#d32f2f' : '#2e7d32'};">
    ${statusEmoji} API Automation Test Results
  </h2>
  
  <table style="width: 100%; border-collapse: collapse; margin: 20px 0;">
    <tr style="background-color: #f5f5f5;">
      <td style="padding: 12px; border: 1px solid #ddd;"><strong>Status</strong></td>
      <td style="padding: 12px; border: 1px solid #ddd; color: ${failed > 0 ? '#d32f2f' : '#2e7d32'}; font-weight: bold;">
        ${testStatus}
      </td>
    </tr>
    <tr>
      <td style="padding: 12px; border: 1px solid #ddd;"><strong>Branch</strong></td>
      <td style="padding: 12px; border: 1px solid #ddd;">${branch}</td>
    </tr>
    <tr style="background-color: #f5f5f5;">
      <td style="padding: 12px; border: 1px solid #ddd;"><strong>Duration</strong></td>
      <td style="padding: 12px; border: 1px solid #ddd;">${formattedDuration}</td>
    </tr>
    <tr>
      <td style="padding: 12px; border: 1px solid #ddd;"><strong>Triggered by</strong></td>
      <td style="padding: 12px; border: 1px solid #ddd;">${actor}</td>
    </tr>
  </table>

  <h3 style="color: #424242; margin-top: 30px;">Test Summary</h3>
  <table style="width: 100%; border-collapse: collapse; margin: 20px 0;">
    <tr style="background-color: #f5f5f5;">
      <td style="padding: 12px; border: 1px solid #ddd;"><strong>Total Tests</strong></td>
      <td style="padding: 12px; border: 1px solid #ddd; text-align: center; font-weight: bold;">${total}</td>
    </tr>
    <tr>
      <td style="padding: 12px; border: 1px solid #ddd;">✅ <strong>Passed</strong></td>
      <td style="padding: 12px; border: 1px solid #ddd; text-align: center; color: #2e7d32; font-weight: bold;">${passed}</td>
    </tr>
    <tr style="background-color: #f5f5f5;">
      <td style="padding: 12px; border: 1px solid #ddd;">❌ <strong>Failed</strong></td>
      <td style="padding: 12px; border: 1px solid #ddd; text-align: center; color: #d32f2f; font-weight: bold;">${failed}</td>
    </tr>
    <tr>
      <td style="padding: 12px; border: 1px solid #ddd;">⏭️ <strong>Skipped</strong></td>
      <td style="padding: 12px; border: 1px solid #ddd; text-align: center; color: #757575; font-weight: bold;">${skipped}</td>
    </tr>
  </table>

  <div style="margin-top: 30px; padding: 15px; background-color: #e3f2fd; border-left: 4px solid #1976d2;">
    <p style="margin: 0; color: #424242;">
      <strong>Repository:</strong> ${repoName}<br>
      <strong>Run ID:</strong> ${runId}
    </p>
  </div>

  ${runUrl ? `
  <div style="margin-top: 20px; text-align: center;">
    <a href="${runUrl}" 
       style="display: inline-block; padding: 12px 24px; background-color: ${failed > 0 ? '#d32f2f' : '#1976d2'}; 
              color: white; text-decoration: none; border-radius: 4px; font-weight: bold;">
      🔗 View Full Report on GitHub Actions
    </a>
  </div>
  ` : ''}

  <div style="margin-top: 30px; padding-top: 20px; border-top: 1px solid #ddd; color: #757575; font-size: 12px;">
    <p>This is an automated message from the API Automation Test Suite.</p>
  </div>
</div>
`;

// Plain text version for email clients that don't support HTML
const textBody = `
${statusEmoji} API Automation Test Results

Status: ${testStatus}
Branch: ${branch}
Duration: ${formattedDuration}
Triggered by: ${actor}

Test Summary:
- Total Tests: ${total}
- ✅ Passed: ${passed}
- ❌ Failed: ${failed}
- ⏭️ Skipped: ${skipped}

Repository: ${repoName}
Run ID: ${runId}

${runUrl ? `View Full Report: ${runUrl}` : ''}
`;

// Configure email transporter with Gmail
const transporter = nodemailer.createTransport({
  service: 'gmail',
  auth: {
    user: process.env.GMAIL_USER,
    pass: process.env.GMAIL_APP_PASSWORD
  }
});

// Email options
const mailOptions = {
  from: `"API Test Reporter" <${process.env.GMAIL_USER}>`,
  to: process.env.SLACK_EMAIL,
  subject: `${statusEmoji} API Tests ${testStatus} - ${branch} - ${passed}/${total} passed`,
  text: textBody,
  html: htmlBody
};

// Send email to Slack channel
transporter.sendMail(mailOptions, (error, info) => {
  if (error) {
    console.error('❌ Error sending Slack notification via email:', error.message);
    process.exit(1);
  } else {
    console.log('✅ Slack notification sent successfully via email!');
    console.log(`Test Results: ${passed} passed, ${failed} failed, ${skipped} skipped`);
    console.log(`Message ID: ${info.messageId}`);
  }
});