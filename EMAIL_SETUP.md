# Email Integration Setup Guide

## Overview
Your CRM now supports real-time email sending and receiving using SMTP and IMAP protocols.

## Features
- ✅ Send AI-generated replies directly from the CRM
- ✅ Track sent emails in conversation history
- ✅ Check inbox for new customer emails
- ✅ Auto-extract contact information from emails
- ✅ Gmail, Outlook, and custom SMTP support

## Gmail Setup (Recommended)

### Step 1: Enable 2-Factor Authentication
1. Go to https://myaccount.google.com/security
2. Enable "2-Step Verification"

### Step 2: Create App Password
1. Go to https://myaccount.google.com/apppasswords
2. Select "Mail" and "Other (Custom name)"
3. Name it "CRM System"
4. Click "Generate"
5. Copy the 16-character password

### Step 3: Update .env File
```env
# Email Configuration
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-16-char-app-password
MAIL_DEFAULT_SENDER=your-email@gmail.com

# IMAP Configuration (for receiving emails)
IMAP_SERVER=imap.gmail.com
IMAP_PORT=993
IMAP_USERNAME=your-email@gmail.com
IMAP_PASSWORD=your-16-char-app-password
```

## Outlook/Office 365 Setup

```env
MAIL_SERVER=smtp.office365.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your-email@outlook.com
MAIL_PASSWORD=your-password
MAIL_DEFAULT_SENDER=your-email@outlook.com

IMAP_SERVER=outlook.office365.com
IMAP_PORT=993
IMAP_USERNAME=your-email@outlook.com
IMAP_PASSWORD=your-password
```

## Custom SMTP Server

```env
MAIL_SERVER=mail.yourdomain.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=sales@yourdomain.com
MAIL_PASSWORD=your-password
MAIL_DEFAULT_SENDER=sales@yourdomain.com

IMAP_SERVER=mail.yourdomain.com
IMAP_PORT=993
IMAP_USERNAME=sales@yourdomain.com
IMAP_PASSWORD=your-password
```

## Installation

1. Install new dependencies:
```bash
pip install -r requirements.txt
```

2. Update database schema:
```bash
rm -rf instance
python app.py
```

3. Restart the application

## How to Use

### Sending Emails
1. Generate an AI reply in the Email Assistant
2. Click "Edit Reply" to customize if needed
3. Click "📧 Send Email" button
4. Confirm the recipient and subject
5. Email will be sent immediately

### Checking Inbox
- Use the API endpoint: `GET /api/check-inbox`
- Returns last 10 unread emails
- Can be integrated into dashboard for auto-checking

### Email Tracking
- All sent emails are marked in the database
- View sent status in Conversations page
- Track when emails were sent

## Security Notes

⚠️ **Important Security Tips:**
1. Never commit `.env` file to git
2. Use app-specific passwords, not your main password
3. Enable 2FA on your email account
4. Rotate passwords regularly
5. Use environment variables in production

## Troubleshooting

### "Authentication failed"
- Check username and password are correct
- For Gmail, ensure you're using App Password, not regular password
- Verify 2FA is enabled

### "Connection refused"
- Check SMTP/IMAP server addresses
- Verify port numbers (587 for SMTP, 993 for IMAP)
- Check firewall settings

### "TLS/SSL error"
- Ensure MAIL_USE_TLS is set correctly
- Try port 465 with SSL instead of 587 with TLS

## Testing

Test email sending:
```bash
curl -X POST http://localhost:5000/api/send-email \
  -H "Content-Type: application/json" \
  -d '{
    "to_email": "test@example.com",
    "subject": "Test Email",
    "body": "This is a test email from CRM"
  }'
```

Test inbox checking:
```bash
curl http://localhost:5000/api/check-inbox
```

## Support

For issues or questions:
1. Check the error logs in terminal
2. Verify email credentials
3. Test with a simple email client first
4. Check your email provider's documentation
