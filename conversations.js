let conversations = [];
let companies = [];
let currentConversationId = null;

// Get URL parameters
function getUrlParameter(name) {
    const urlParams = new URLSearchParams(window.location.search);
    return urlParams.get(name);
}

async function loadConversations() {
    try {
        const response = await fetch('/api/conversations');
        conversations = await response.json();
        
        // Check if there's a company filter in URL
        const companyFilter = getUrlParameter('company');
        if (companyFilter) {
            // Find the company and set the filter
            const company = companies.find(c => c.name === companyFilter);
            if (company) {
                document.getElementById('companyFilter').value = company.id;
            }
        }
        
        renderConversations(conversations);
        
        // Apply filter if set
        if (companyFilter) {
            filterConversations();
        }
    } catch (error) {
        console.error('Error loading conversations:', error);
    }
}

async function loadCompanies() {
    try {
        const response = await fetch('/api/companies');
        companies = await response.json();
        
        const companyFilter = document.getElementById('companyFilter');
        companyFilter.innerHTML = '<option value="">All Companies</option>' + 
            companies.map(c => `<option value="${c.id}">${c.name}</option>`).join('');
        
        // Check if there's a company filter in URL and apply it
        const companyName = getUrlParameter('company');
        if (companyName) {
            const company = companies.find(c => c.name === companyName);
            if (company) {
                companyFilter.value = company.id;
            }
        }
    } catch (error) {
        console.error('Error loading companies:', error);
    }
}

function formatEmailType(type) {
    if (!type) return 'N/A';
    
    const typeLabels = {
        'inquiry': 'Inquiry',
        'inquiry_pricing': 'Inquiry & Pricing',
        'pricing': 'Pricing',
        'demo_request': 'Demo Request',
        'support': 'Support',
        'follow-up': 'Follow-up',
        'complaint': 'Complaint',
        'partnership': 'Partnership',
        'other': 'Other'
    };
    
    return typeLabels[type] || type;
}

function renderConversations(data) {
    const grid = document.getElementById('conversationsGrid');
    
    if (data.length === 0) {
        grid.innerHTML = '<div style="text-align: center; padding: 40px; color: #999;">No conversations found</div>';
        return;
    }
    
    grid.innerHTML = data.map(conv => `
        <div class="conversation-card" onclick="viewConversation(${conv.id})">
            <div class="header">
                <span class="name">${conv.contact_name || 'Unknown'} ${conv.company_name ? '(' + conv.company_name + ')' : ''}</span>
                <span class="date">${new Date(conv.created_at).toLocaleDateString()}</span>
            </div>
            <div class="subject">${conv.subject || 'No subject'}</div>
            <div class="preview">${conv.customer_message.substring(0, 150)}...</div>
            <div class="tags">
                ${conv.email_type ? `<span class="tag ${conv.email_type}">${formatEmailType(conv.email_type)}</span>` : ''}
                ${conv.sentiment ? `<span class="tag ${conv.sentiment}">${conv.sentiment}</span>` : ''}
            </div>
        </div>
    `).join('');
}

function searchConversations() {
    const search = document.getElementById('searchInput').value.toLowerCase();
    const filtered = conversations.filter(c => 
        (c.subject && c.subject.toLowerCase().includes(search)) ||
        c.customer_message.toLowerCase().includes(search) ||
        c.ai_reply.toLowerCase().includes(search) ||
        (c.contact_name && c.contact_name.toLowerCase().includes(search))
    );
    renderConversations(filtered);
}

function filterConversations() {
    const type = document.getElementById('typeFilter').value;
    const sentiment = document.getElementById('sentimentFilter').value;
    const companyId = document.getElementById('companyFilter').value;
    
    let filtered = conversations;
    
    if (type) {
        filtered = filtered.filter(c => c.email_type === type);
    }
    
    if (sentiment) {
        filtered = filtered.filter(c => c.sentiment === sentiment);
    }
    
    if (companyId) {
        filtered = filtered.filter(c => {
            const company = companies.find(comp => comp.id == companyId);
            return company && c.company_name === company.name;
        });
    }
    
    renderConversations(filtered);
}

async function viewConversation(id) {
    try {
        const response = await fetch(`/api/conversations/${id}`);
        const conv = await response.json();
        
        currentConversationId = id;
        
        const details = `
            <div class="conversation-detail">
                <div class="conversation-header">
                    <div class="header-row">
                        <div class="header-item">
                            <strong>Contact:</strong> ${conv.contact_name || 'Unknown'}
                        </div>
                        <div class="header-item">
                            <strong>Email:</strong> ${conv.contact_email || 'N/A'}
                        </div>
                    </div>
                    <div class="header-row">
                        <div class="header-item">
                            <strong>Company:</strong> ${conv.company_name || 'N/A'}
                        </div>
                        <div class="header-item">
                            <strong>Date:</strong> ${new Date(conv.created_at).toLocaleString()}
                        </div>
                    </div>
                    <div class="header-row">
                        <div class="header-item">
                            <strong>Type:</strong> <span class="tag ${conv.email_type}">${formatEmailType(conv.email_type)}</span>
                        </div>
                        <div class="header-item">
                            <strong>Sentiment:</strong> <span class="tag ${conv.sentiment}">${conv.sentiment || 'N/A'}</span>
                        </div>
                    </div>
                </div>
                
                ${conv.subject ? `
                <div class="conversation-subject">
                    <strong>Subject:</strong> ${conv.subject}
                </div>
                ` : ''}
                
                <div class="conversation-thread">
                    <div class="message-bubble customer-message">
                        <div class="message-header">
                            <span class="message-sender">👤 ${conv.contact_name || 'Customer'}</span>
                            <span class="message-label">Customer Message</span>
                        </div>
                        <div class="message-content">${conv.customer_message.replace(/\n/g, '<br>')}</div>
                    </div>
                    
                    <div class="message-bubble company-reply">
                        <div class="message-header">
                            <span class="message-sender">🏢 Your Company</span>
                            <span class="message-label">AI Generated Reply</span>
                        </div>
                        <div class="message-content">${conv.ai_reply.replace(/\n/g, '<br>')}</div>
                    </div>
                </div>
            </div>
        `;
        
        document.getElementById('conversationDetails').innerHTML = details;
        document.getElementById('conversationModal').style.display = 'block';
    } catch (error) {
        alert('Error loading conversation: ' + error.message);
    }
}

async function deleteConversation() {
    if (!confirm('Are you sure you want to delete this conversation?')) {
        return;
    }
    
    try {
        const response = await fetch(`/api/conversations/${currentConversationId}`, { 
            method: 'DELETE' 
        });
        
        if (!response.ok) {
            throw new Error('Failed to delete conversation');
        }
        
        closeModal();
        loadConversations();
    } catch (error) {
        alert('Error: ' + error.message);
    }
}

function closeModal() {
    document.getElementById('conversationModal').style.display = 'none';
}

// Close modal when clicking outside
window.onclick = function(event) {
    const modal = document.getElementById('conversationModal');
    if (event.target == modal) {
        closeModal();
    }
}

// Load companies first, then conversations
loadCompanies().then(() => {
    loadConversations();
});
