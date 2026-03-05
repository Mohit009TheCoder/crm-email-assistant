from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Company(db.Model):
    __tablename__ = 'companies'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    domain = db.Column(db.String(200))
    industry = db.Column(db.String(100))
    phone = db.Column(db.String(50))
    address = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    contacts = db.relationship('Contact', backref='company', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'domain': self.domain,
            'industry': self.industry,
            'phone': self.phone,
            'address': self.address,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'contact_count': len(self.contacts)
        }

class Contact(db.Model):
    __tablename__ = 'contacts'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(200), nullable=False, unique=True)
    position = db.Column(db.String(100))
    phone = db.Column(db.String(50))
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    conversations = db.relationship('Conversation', backref='contact', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'position': self.position,
            'phone': self.phone,
            'company_id': self.company_id,
            'company_name': self.company.name if self.company else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'conversation_count': len(self.conversations)
        }

class Conversation(db.Model):
    __tablename__ = 'conversations'
    
    id = db.Column(db.Integer, primary_key=True)
    contact_id = db.Column(db.Integer, db.ForeignKey('contacts.id'), nullable=False)
    subject = db.Column(db.String(300))
    customer_message = db.Column(db.Text, nullable=False)
    ai_reply = db.Column(db.Text, nullable=False)
    email_type = db.Column(db.String(50))  # inquiry, support, pricing, follow-up, etc.
    sentiment = db.Column(db.String(20))  # positive, neutral, negative
    email_sent = db.Column(db.Boolean, default=False)
    sent_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'contact_id': self.contact_id,
            'contact_name': self.contact.name if self.contact else None,
            'contact_email': self.contact.email if self.contact else None,
            'company_name': self.contact.company.name if self.contact and self.contact.company else None,
            'subject': self.subject,
            'customer_message': self.customer_message,
            'ai_reply': self.ai_reply,
            'email_type': self.email_type,
            'sentiment': self.sentiment,
            'email_sent': self.email_sent,
            'sent_at': self.sent_at.isoformat() if self.sent_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
