from flask import Flask, render_template, request, jsonify
from flask_mail import Mail, Message
from groq import Groq
import os
from dotenv import load_dotenv
from models import db, Company, Contact, Conversation
from datetime import datetime, timedelta
from sqlalchemy import func, or_
import json
import imaplib
import email
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import re

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///crm.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Email configuration
app.config['MAIL_SERVER'] = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
app.config['MAIL_PORT'] = int(os.environ.get('MAIL_PORT', 587))
app.config['MAIL_USE_TLS'] = os.environ.get('MAIL_USE_TLS', 'True') == 'True'
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')
app.config['MAIL_DEFAULT_SENDER'] = os.environ.get('MAIL_DEFAULT_SENDER')

# Initialize extensions
db.init_app(app)
mail = Mail(app)

# Initialize Groq client
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

SYSTEM_PROMPT = """You are an AI assistant inside a CRM system helping a sales team reply to customer emails.

Your job is to analyze the email conversation between a customer and the sales team and generate a professional, personalized reply email to the customer.

CRITICAL GUIDELINES:
- Generate UNIQUE and VARIED responses - never use the same template or phrasing twice
- Adapt your tone and style based on the customer's communication style
- Reference specific details from the customer's message to show you read it carefully
- Vary your opening greetings (Dear, Hi, Hello, Good morning/afternoon, Greetings, etc.)
- Use different closing signatures (Best regards, Sincerely, Warm regards, Kind regards, Looking forward, etc.)
- Change sentence structure and vocabulary in each response
- Be conversational and natural, not robotic or templated
- Match the formality level of the customer's email
- If the customer is casual, be friendly; if formal, be professional
- Add personality while maintaining professionalism

CONTENT REQUIREMENTS:
- Write clear, polite, and professional emails
- Maintain a helpful and friendly sales tone
- Understand the context of the conversation before replying
- Answer the customer's latest question or concern directly
- If the customer asks about product details, respond clearly and concisely
- If information is missing, politely ask the customer for clarification
- Keep the email concise and business-appropriate
- Do NOT repeat the entire conversation
- Do NOT include unnecessary explanations
- Only generate the reply email

PERSONALIZATION:
- Use the customer's name if provided
- Reference their company if mentioned
- Acknowledge specific points they raised
- Show genuine interest in their needs
- Provide relevant examples or suggestions when appropriate

Output format:
Subject: <email subject>

Email:
<email body>"""

CLASSIFICATION_PROMPT = """Analyze this email and classify it accurately.

Email Types:
- inquiry: General questions about products/services, requests for information, exploring solutions
- pricing: Questions about costs, pricing plans, quotes, budget discussions
- demo_request: Requests for product demonstrations, trials, or presentations
- support: Technical issues, help requests, troubleshooting
- follow-up: Continuing previous conversations, checking status
- complaint: Negative feedback, issues, dissatisfaction
- partnership: Business collaboration, partnership proposals
- other: Anything that doesn't fit above categories

IMPORTANT: If an email asks about BOTH product details AND pricing (e.g., "tell me about your solution and pricing"), classify it as "inquiry_pricing" to capture both aspects.

Sentiment:
- positive: Enthusiastic, interested, satisfied tone
- neutral: Professional, matter-of-fact, informational
- negative: Frustrated, disappointed, angry tone

Email: {email}

Respond in JSON format:
{{"email_type": "type", "sentiment": "sentiment"}}"""

# ============= ROUTES =============

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@app.route('/companies')
def companies_page():
    return render_template('companies.html')

@app.route('/contacts')
def contacts_page():
    return render_template('contacts.html')

@app.route('/conversations')
def conversations_page():
    return render_template('conversations.html')

# ============= API STATS =============

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Get dashboard statistics"""
    total_companies = Company.query.count()
    total_contacts = Contact.query.count()
    total_conversations = Conversation.query.count()
    
    # Recent conversations (last 7 days)
    week_ago = datetime.utcnow() - timedelta(days=7)
    recent_conversations = Conversation.query.filter(
        Conversation.created_at >= week_ago
    ).count()
    
    # Email type distribution
    email_types = db.session.query(
        Conversation.email_type,
        func.count(Conversation.id)
    ).group_by(Conversation.email_type).all()
    
    email_type_stats = {et[0]: et[1] for et in email_types if et[0]}
    
    # Sentiment distribution
    sentiments = db.session.query(
        Conversation.sentiment,
        func.count(Conversation.id)
    ).group_by(Conversation.sentiment).all()
    
    sentiment_stats = {s[0]: s[1] for s in sentiments if s[0]}
    
    return jsonify({
        'total_companies': total_companies,
        'total_contacts': total_contacts,
        'total_conversations': total_conversations,
        'recent_conversations': recent_conversations,
        'email_types': email_type_stats,
        'sentiments': sentiment_stats
    })

# ============= COMPANY API =============

@app.route('/api/companies', methods=['GET', 'POST'])
def companies_api():
    if request.method == 'POST':
        data = request.json
        
        # Check if company exists
        existing = Company.query.filter_by(name=data['name']).first()
        if existing:
            return jsonify({'error': 'Company with this name already exists'}), 400
        
        company = Company(
            name=data['name'],
            domain=data.get('domain'),
            industry=data.get('industry'),
            phone=data.get('phone'),
            address=data.get('address')
        )
        db.session.add(company)
        db.session.commit()
        return jsonify(company.to_dict()), 201
    
    # GET with search
    search = request.args.get('search', '')
    query = Company.query
    
    if search:
        query = query.filter(
            or_(
                Company.name.ilike(f'%{search}%'),
                Company.domain.ilike(f'%{search}%'),
                Company.industry.ilike(f'%{search}%')
            )
        )
    
    companies = query.order_by(Company.created_at.desc()).all()
    return jsonify([c.to_dict() for c in companies])

@app.route('/api/companies/<int:id>', methods=['GET', 'PUT', 'DELETE'])
def company_detail(id):
    company = Company.query.get_or_404(id)
    
    if request.method == 'GET':
        data = company.to_dict()
        # Include contacts and conversation count
        data['contacts'] = [c.to_dict() for c in company.contacts]
        data['conversation_count'] = sum(len(c.conversations) for c in company.contacts)
        return jsonify(data)
    
    elif request.method == 'PUT':
        data = request.json
        company.name = data.get('name', company.name)
        company.domain = data.get('domain', company.domain)
        company.industry = data.get('industry', company.industry)
        company.phone = data.get('phone', company.phone)
        company.address = data.get('address', company.address)
        db.session.commit()
        return jsonify(company.to_dict())
    
    elif request.method == 'DELETE':
        db.session.delete(company)
        db.session.commit()
        return jsonify({'message': 'Company deleted successfully'})

# ============= CONTACT API =============

@app.route('/api/contacts', methods=['GET', 'POST'])
def contacts_api():
    if request.method == 'POST':
        data = request.json
        
        # Check if contact already exists
        existing = Contact.query.filter_by(email=data['email']).first()
        if existing:
            return jsonify({'error': 'Contact with this email already exists'}), 400
        
        contact = Contact(
            name=data['name'],
            email=data['email'],
            position=data.get('position'),
            phone=data.get('phone'),
            company_id=data.get('company_id')
        )
        db.session.add(contact)
        db.session.commit()
        return jsonify(contact.to_dict()), 201
    
    # GET with filters
    search = request.args.get('search', '')
    company_id = request.args.get('company_id')
    
    query = Contact.query
    
    if search:
        query = query.filter(
            or_(
                Contact.name.ilike(f'%{search}%'),
                Contact.email.ilike(f'%{search}%'),
                Contact.position.ilike(f'%{search}%')
            )
        )
    
    if company_id:
        query = query.filter_by(company_id=company_id)
    
    contacts = query.order_by(Contact.created_at.desc()).all()
    return jsonify([c.to_dict() for c in contacts])

@app.route('/api/contacts/<int:id>', methods=['GET', 'PUT', 'DELETE'])
def contact_detail(id):
    contact = Contact.query.get_or_404(id)
    
    if request.method == 'GET':
        data = contact.to_dict()
        # Include conversations
        data['conversations'] = [c.to_dict() for c in contact.conversations]
        return jsonify(data)
    
    elif request.method == 'PUT':
        data = request.json
        contact.name = data.get('name', contact.name)
        contact.email = data.get('email', contact.email)
        contact.position = data.get('position', contact.position)
        contact.phone = data.get('phone', contact.phone)
        contact.company_id = data.get('company_id', contact.company_id)
        db.session.commit()
        return jsonify(contact.to_dict())
    
    elif request.method == 'DELETE':
        db.session.delete(contact)
        db.session.commit()
        return jsonify({'message': 'Contact deleted successfully'})

# ============= CONVERSATION API =============

@app.route('/api/conversations', methods=['GET'])
def get_conversations():
    """Get all conversations with filters"""
    contact_id = request.args.get('contact_id')
    company_id = request.args.get('company_id')
    email_type = request.args.get('email_type')
    sentiment = request.args.get('sentiment')
    search = request.args.get('search', '')
    
    query = Conversation.query
    
    if contact_id:
        query = query.filter_by(contact_id=contact_id)
    
    if company_id:
        query = query.join(Contact).filter(Contact.company_id == company_id)
    
    if email_type:
        query = query.filter_by(email_type=email_type)
    
    if sentiment:
        query = query.filter_by(sentiment=sentiment)
    
    if search:
        query = query.filter(
            or_(
                Conversation.subject.ilike(f'%{search}%'),
                Conversation.customer_message.ilike(f'%{search}%'),
                Conversation.ai_reply.ilike(f'%{search}%')
            )
        )
    
    conversations = query.order_by(Conversation.created_at.desc()).limit(200).all()
    return jsonify([c.to_dict() for c in conversations])

@app.route('/api/conversations/<int:id>', methods=['GET', 'PUT', 'DELETE'])
def conversation_detail(id):
    conversation = Conversation.query.get_or_404(id)
    
    if request.method == 'GET':
        return jsonify(conversation.to_dict())
    
    elif request.method == 'PUT':
        data = request.json
        conversation.subject = data.get('subject', conversation.subject)
        conversation.customer_message = data.get('customer_message', conversation.customer_message)
        conversation.ai_reply = data.get('ai_reply', conversation.ai_reply)
        conversation.email_type = data.get('email_type', conversation.email_type)
        conversation.sentiment = data.get('sentiment', conversation.sentiment)
        db.session.commit()
        return jsonify(conversation.to_dict())
    
    elif request.method == 'DELETE':
        db.session.delete(conversation)
        db.session.commit()
        return jsonify({'message': 'Conversation deleted successfully'})

@app.route('/api/contact/<email>/history', methods=['GET'])
def get_contact_history(email):
    """Get conversation history for a specific contact"""
    contact = Contact.query.filter_by(email=email).first()
    if not contact:
        return jsonify({'history': [], 'contact': None})
    
    conversations = Conversation.query.filter_by(
        contact_id=contact.id
    ).order_by(Conversation.created_at.desc()).all()
    
    return jsonify({
        'contact': contact.to_dict(),
        'history': [c.to_dict() for c in conversations]
    })

# ============= EMAIL SENDING =============

@app.route('/api/send-email', methods=['POST'])
def send_email():
    """Send email to customer"""
    data = request.json
    
    to_email = data.get('to_email')
    subject = data.get('subject')
    body = data.get('body')
    conversation_id = data.get('conversation_id')
    
    if not all([to_email, subject, body]):
        return jsonify({'error': 'Missing required fields'}), 400
    
    try:
        # Create email message
        msg = Message(
            subject=subject,
            recipients=[to_email],
            body=body
        )
        
        # Send email
        mail.send(msg)
        
        # Update conversation if provided
        if conversation_id:
            conversation = Conversation.query.get(conversation_id)
            if conversation:
                conversation.email_sent = True
                conversation.sent_at = datetime.utcnow()
                db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'Email sent successfully to {to_email}'
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/check-inbox', methods=['GET'])
def check_inbox():
    """Check inbox for new emails"""
    try:
        imap_server = os.environ.get('IMAP_SERVER', 'imap.gmail.com')
        imap_port = int(os.environ.get('IMAP_PORT', 993))
        imap_username = os.environ.get('IMAP_USERNAME')
        imap_password = os.environ.get('IMAP_PASSWORD')
        
        if not all([imap_username, imap_password]):
            return jsonify({'error': 'Email credentials not configured'}), 400
        
        # Connect to IMAP server
        mail_conn = imaplib.IMAP4_SSL(imap_server, imap_port)
        mail_conn.login(imap_username, imap_password)
        mail_conn.select('INBOX')
        
        # Search for unread emails
        status, messages = mail_conn.search(None, 'UNSEEN')
        email_ids = messages[0].split()
        
        new_emails = []
        
        # Fetch last 10 unread emails
        for email_id in email_ids[-10:]:
            status, msg_data = mail_conn.fetch(email_id, '(RFC822)')
            
            for response_part in msg_data:
                if isinstance(response_part, tuple):
                    msg = email.message_from_bytes(response_part[1])
                    
                    # Extract email details
                    from_email = email.utils.parseaddr(msg['From'])[1]
                    subject = msg['Subject']
                    
                    # Get email body
                    body = ''
                    if msg.is_multipart():
                        for part in msg.walk():
                            if part.get_content_type() == 'text/plain':
                                body = part.get_payload(decode=True).decode()
                                break
                    else:
                        body = msg.get_payload(decode=True).decode()
                    
                    new_emails.append({
                        'from': from_email,
                        'subject': subject,
                        'body': body[:500],  # First 500 chars
                        'date': msg['Date']
                    })
        
        mail_conn.close()
        mail_conn.logout()
        
        return jsonify({
            'success': True,
            'count': len(new_emails),
            'emails': new_emails
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ============= AI REPLY GENERATION =============

@app.route('/generate-reply', methods=['POST'])
def generate_reply():
    data = request.json
    conversation = data.get('conversation', '')
    contact_email = data.get('contact_email', '')
    contact_name = data.get('contact_name', '')
    company_name = data.get('company_name', '')
    
    if not conversation:
        return jsonify({'error': 'Conversation is required'}), 400
    
    try:
        # Get or create contact
        contact = None
        if contact_email:
            contact = Contact.query.filter_by(email=contact_email).first()
            
            if not contact and contact_name:
                # Create company if provided
                company = None
                if company_name:
                    company = Company.query.filter_by(name=company_name).first()
                    if not company:
                        company = Company(name=company_name)
                        db.session.add(company)
                        db.session.flush()
                
                # Create contact
                contact = Contact(
                    name=contact_name,
                    email=contact_email,
                    company_id=company.id if company else None
                )
                db.session.add(contact)
                db.session.flush()
        
        # Get conversation history for context
        history_context = ""
        if contact:
            previous_convos = Conversation.query.filter_by(
                contact_id=contact.id
            ).order_by(Conversation.created_at.desc()).limit(5).all()
            
            if previous_convos:
                history_context = "\n\nPrevious conversation history with this contact:\n"
                for conv in reversed(previous_convos):
                    history_context += f"\n[{conv.created_at.strftime('%Y-%m-%d')}]\n"
                    history_context += f"Customer: {conv.customer_message[:200]}...\n"
                    history_context += f"Our reply: {conv.ai_reply[:200]}...\n"
        
        # Generate reply with context
        full_prompt = conversation + history_context
        
        chat_completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": full_prompt}
            ],
            max_tokens=1024,
            temperature=0.9,  # Higher temperature for more creative/varied responses
            top_p=0.95,  # Nucleus sampling for diversity
            frequency_penalty=0.7,  # Reduce repetition
            presence_penalty=0.6  # Encourage new topics/phrases
        )
        
        reply = chat_completion.choices[0].message.content
        
        # Classify email type and sentiment
        classification_response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "user", "content": CLASSIFICATION_PROMPT.format(email=conversation)}
            ],
            max_tokens=100,
            temperature=0.3
        )
        
        try:
            classification_text = classification_response.choices[0].message.content
            # Handle both JSON and plain text responses
            if '{' in classification_text:
                classification = json.loads(classification_text)
            else:
                # Fallback parsing
                classification = {'email_type': 'other', 'sentiment': 'neutral'}
            
            email_type = classification.get('email_type', 'other')
            sentiment = classification.get('sentiment', 'neutral')
            
            # Validate email_type
            valid_types = ['inquiry', 'pricing', 'inquiry_pricing', 'demo_request', 
                          'support', 'follow-up', 'complaint', 'partnership', 'other']
            if email_type not in valid_types:
                email_type = 'other'
                
        except Exception as e:
            print(f"Classification error: {e}")
            email_type = 'other'
            sentiment = 'neutral'
        
        # Extract subject if present (improved extraction)
        subject = None
        
        # Try multiple patterns for subject extraction
        if 'Subject:' in conversation or 'subject:' in conversation.lower():
            lines = conversation.split('\n')
            for line in lines:
                line_stripped = line.strip()
                # Case-insensitive subject detection
                if line_stripped.lower().startswith('subject:'):
                    subject = line_stripped[8:].strip()  # Remove "Subject:" prefix
                    if subject:
                        break
        
        # If no explicit subject, try to generate one from content
        if not subject:
            lines = [l.strip() for l in conversation.split('\n') if l.strip()]
            # Skip common headers
            skip_prefixes = ['from:', 'to:', 'date:', 'cc:', 'bcc:', 'reply-to:', 'email:', 'phone:', 'tel:']
            
            # Look for first meaningful sentence
            for line in lines:
                line_lower = line.lower()
                # Skip if it's a header line
                if any(line_lower.startswith(prefix) for prefix in skip_prefixes):
                    continue
                # Skip if it's just an email address or phone
                if '@' in line and len(line.split()) <= 2:
                    continue
                if line.startswith('+') and len(line.split()) == 1:
                    continue
                # Skip greetings
                if line_lower in ['hi,', 'hello,', 'dear sir,', 'dear madam,', 'greetings,']:
                    continue
                
                # Found a meaningful line
                if len(line) > 10:
                    # If line is too long, try to extract key phrase
                    if len(line) > 80:
                        # Look for key phrases about the purpose
                        purpose_keywords = [
                            'looking for', 'interested in', 'inquiring about', 'question about',
                            'exploring', 'seeking', 'need', 'require', 'would like to',
                            'requesting', 'asking about', 'regarding'
                        ]
                        
                        line_lower = line.lower()
                        for keyword in purpose_keywords:
                            if keyword in line_lower:
                                # Extract the part with the keyword
                                start_idx = line_lower.index(keyword)
                                # Get up to 60 chars from the keyword
                                subject_part = line[start_idx:start_idx + 60].strip()
                                # Clean up if it ends mid-word
                                if not subject_part.endswith(('.', ',', '!', '?')):
                                    words = subject_part.split()
                                    if len(words) > 1:
                                        subject_part = ' '.join(words[:-1]) + '...'
                                subject = subject_part
                                break
                        
                        # If no keyword found, use first 60 chars
                        if not subject:
                            subject = line[:60].strip()
                            if not subject.endswith(('.', ',', '!', '?')):
                                words = subject.split()
                                if len(words) > 1:
                                    subject = ' '.join(words[:-1]) + '...'
                    else:
                        subject = line
                    break
        
        # If still no subject, use email type-based default
        if not subject:
            subject_defaults = {
                'inquiry': 'General Inquiry',
                'support': 'Support Request',
                'pricing': 'Pricing Question',
                'follow-up': 'Follow-up',
                'complaint': 'Customer Feedback',
                'demo_request': 'Demo Request',
                'partnership': 'Partnership Inquiry'
            }
            subject = subject_defaults.get(email_type, 'Email Conversation')
        
        # Ensure subject is not too long (max 100 chars)
        if subject and len(subject) > 100:
            subject = subject[:97] + '...'
        
        # Save conversation
        if contact:
            convo = Conversation(
                contact_id=contact.id,
                subject=subject,
                customer_message=conversation,
                ai_reply=reply,
                email_type=email_type,
                sentiment=sentiment
            )
            db.session.add(convo)
            db.session.commit()
        
        return jsonify({
            'reply': reply,
            'email_type': email_type,
            'sentiment': sentiment,
            'contact_id': contact.id if contact else None
        })
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Create tables
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True, port=5001)
