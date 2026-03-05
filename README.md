# 📧 CRM Email Reply Assistant

AI-powered email response generator with automatic contact extraction and conversation tracking.

## ✨ Features

- **AI Email Generation** - Generate professional email replies using Groq AI (Llama 3.3 70B)
- **Automatic Contact Extraction** - Auto-fills email, name, and company from email text
- **Contact Management** - Manage contacts and companies with full CRUD operations
- **Conversation Tracking** - Track all email conversations with sentiment analysis
- **Email Classification** - Automatically categorizes emails (inquiry, support, pricing, etc.)
- **Dashboard Analytics** - View statistics and insights about your conversations
- **Email Sending** - Send emails directly from the application

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- Groq API key (get it from [console.groq.com](https://console.groq.com))

### Installation

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd Email
   ```

2. **Create virtual environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   
   Create a `.env` file in the root directory:
   ```env
   GROQ_API_KEY=your_groq_api_key_here
   
   # Optional: Email configuration (for sending emails)
   MAIL_SERVER=smtp.gmail.com
   MAIL_PORT=587
   MAIL_USE_TLS=True
   MAIL_USERNAME=your_email@gmail.com
   MAIL_PASSWORD=your_app_password
   MAIL_DEFAULT_SENDER=your_email@gmail.com
   ```

5. **Run the application**
   ```bash
   python app.py
   ```

6. **Open in browser**
   ```
   http://localhost:5000
   ```

## 📖 Usage

### Generate Email Reply

1. Paste an email conversation in the text area
2. Contact information will auto-fill automatically (wait 0.8 seconds)
3. Click "Generate Reply" to create an AI-powered response
4. Edit the reply if needed
5. Copy or send the email directly

### Example Email Format

```
From: john.doe@company.com
Subject: Question about pricing

Hi,

I'm interested in your Enterprise plan. Can you provide more details?

Thanks,
John Doe
Acme Corporation
```

### Automatic Extraction

The system automatically extracts:
- **Email address** - From any part of the email
- **Contact name** - From signatures (Thanks, Regards, etc.)
- **Company name** - From suffixes (Inc., LLC, etc.) or email domain

## 🗂️ Project Structure

```
Email/
├── app.py                 # Main Flask application
├── models.py              # Database models
├── requirements.txt       # Python dependencies
├── .env                   # Environment variables (create this)
├── .gitignore            # Git ignore rules
├── README.md             # This file
├── EMAIL_SETUP.md        # Email configuration guide
├── SYSTEM_REVIEW.md      # Comprehensive system review
├── instance/
│   └── crm.db           # SQLite database
├── templates/
│   ├── index.html       # Main email assistant page
│   ├── dashboard.html   # Analytics dashboard
│   ├── companies.html   # Company management
│   ├── contacts.html    # Contact management
│   └── conversations.html # Conversation history
└── static/
    ├── style.css        # Global styles
    ├── companies.js     # Company management logic
    ├── contacts.js      # Contact management logic
    └── conversations.js # Conversation management logic
```

## 🔧 Configuration

### Email Setup (Optional)

To enable email sending, configure SMTP settings in `.env`. See [EMAIL_SETUP.md](EMAIL_SETUP.md) for detailed instructions.

### Database

The application uses SQLite by default. The database is created automatically on first run at `instance/crm.db`.

## 📊 API Endpoints

### Email Generation
- `POST /generate-reply` - Generate AI email reply

### Contacts
- `GET /api/contacts` - List all contacts
- `POST /api/contacts` - Create new contact
- `GET /api/contacts/<id>` - Get contact details
- `PUT /api/contacts/<id>` - Update contact
- `DELETE /api/contacts/<id>` - Delete contact

### Companies
- `GET /api/companies` - List all companies
- `POST /api/companies` - Create new company
- `GET /api/companies/<id>` - Get company details
- `PUT /api/companies/<id>` - Update company
- `DELETE /api/companies/<id>` - Delete company

### Conversations
- `GET /api/conversations` - List all conversations
- `GET /api/conversations/<id>` - Get conversation details
- `GET /api/contact/<email>/history` - Get contact conversation history

### Email
- `POST /api/send-email` - Send email
- `GET /api/check-inbox` - Check for new emails (requires IMAP config)

### Stats
- `GET /api/stats` - Get dashboard statistics

## 🛠️ Tech Stack

- **Backend:** Flask (Python)
- **Database:** SQLite with SQLAlchemy ORM
- **AI:** Groq API (Llama 3.3 70B)
- **Frontend:** HTML, CSS, JavaScript (Vanilla)
- **Email:** Flask-Mail

## 🔒 Security Notes

⚠️ **Important:** This is a development version. Before deploying to production:

1. Add user authentication
2. Implement CSRF protection
3. Add rate limiting
4. Use PostgreSQL instead of SQLite
5. Enable HTTPS
6. Sanitize all user inputs
7. Add proper error logging
8. Implement backup system

See [SYSTEM_REVIEW.md](SYSTEM_REVIEW.md) for detailed security recommendations.

## 📝 Features in Detail

### AI Email Generation
- Uses Groq's Llama 3.3 70B model
- Context-aware responses
- Varies tone and style to avoid repetition
- Includes conversation history for better context
- Temperature: 0.9 for creative responses

### Contact Extraction
- Automatic extraction from email text
- Multiple pattern matching
- Triggers 0.8 seconds after typing stops
- Visual feedback with blue highlights
- Only fills empty fields (non-destructive)

### Conversation Tracking
- Stores all email conversations
- Links to contacts and companies
- Email type classification (inquiry, support, pricing, etc.)
- Sentiment analysis (positive, neutral, negative)
- Full conversation history per contact

## 🐛 Known Limitations

- SQLite not suitable for high concurrency
- No user authentication (single-user system)
- Contact extraction requires proper capitalization
- Company detection needs suffixes (Inc., LLC, etc.)
- No mobile app

## 🚀 Future Enhancements

- [ ] User authentication and multi-user support
- [ ] Email templates
- [ ] Bulk operations
- [ ] Advanced search and filters
- [ ] Email scheduling
- [ ] Integration with Gmail/Outlook
- [ ] Mobile app
- [ ] Team collaboration features
- [ ] Advanced analytics and reporting

## 📄 License

This project is for educational and personal use.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📞 Support

For issues and questions, please open an issue on GitHub.

---

**Made with ❤️ using Flask and Groq AI**
