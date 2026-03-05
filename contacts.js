let contacts = [];
let companies = [];
let currentContactId = null;

async function loadContacts() {
    try {
        const response = await fetch('/api/contacts');
        contacts = await response.json();
        renderContacts(contacts);
    } catch (error) {
        console.error('Error loading contacts:', error);
    }
}

async function loadCompanies() {
    try {
        const response = await fetch('/api/companies');
        companies = await response.json();
        
        // Populate company dropdowns
        const companySelect = document.getElementById('contactCompany');
        const companyFilter = document.getElementById('companyFilter');
        
        companySelect.innerHTML = '<option value="">No Company</option>' + 
            companies.map(c => `<option value="${c.id}">${c.name}</option>`).join('');
        
        companyFilter.innerHTML = '<option value="">All Companies</option>' + 
            companies.map(c => `<option value="${c.id}">${c.name}</option>`).join('');
    } catch (error) {
        console.error('Error loading companies:', error);
    }
}

function renderContacts(data) {
    const tbody = document.getElementById('contactsBody');
    
    if (data.length === 0) {
        tbody.innerHTML = '<tr><td colspan="7" style="text-align: center; color: #999;">No contacts found</td></tr>';
        return;
    }
    
    tbody.innerHTML = data.map(contact => `
        <tr>
            <td><strong>${contact.name}</strong></td>
            <td>${contact.email}</td>
            <td>${contact.position || '-'}</td>
            <td>${contact.phone || '-'}</td>
            <td>${contact.company_name || '-'}</td>
            <td>${contact.conversation_count || 0}</td>
            <td>
                <button class="btn-primary btn-small" onclick="editContact(${contact.id})">Edit</button>
                <button class="btn-danger btn-small" onclick="deleteContact(${contact.id})">Delete</button>
            </td>
        </tr>
    `).join('');
}

function searchContacts() {
    const search = document.getElementById('searchInput').value.toLowerCase();
    const filtered = contacts.filter(c => 
        c.name.toLowerCase().includes(search) ||
        c.email.toLowerCase().includes(search) ||
        (c.position && c.position.toLowerCase().includes(search))
    );
    renderContacts(filtered);
}

function filterByCompany() {
    const companyId = document.getElementById('companyFilter').value;
    if (!companyId) {
        renderContacts(contacts);
        return;
    }
    
    const filtered = contacts.filter(c => c.company_id == companyId);
    renderContacts(filtered);
}

function showAddModal() {
    currentContactId = null;
    document.getElementById('modalTitle').textContent = 'Add Contact';
    document.getElementById('contactForm').reset();
    document.getElementById('contactId').value = '';
    document.getElementById('contactModal').style.display = 'block';
}

async function editContact(id) {
    try {
        const response = await fetch(`/api/contacts/${id}`);
        const contact = await response.json();
        
        currentContactId = id;
        document.getElementById('modalTitle').textContent = 'Edit Contact';
        document.getElementById('contactId').value = id;
        document.getElementById('contactName').value = contact.name;
        document.getElementById('contactEmail').value = contact.email;
        document.getElementById('contactPosition').value = contact.position || '';
        document.getElementById('contactPhone').value = contact.phone || '';
        document.getElementById('contactCompany').value = contact.company_id || '';
        document.getElementById('contactModal').style.display = 'block';
    } catch (error) {
        alert('Error loading contact: ' + error.message);
    }
}

async function saveContact(event) {
    event.preventDefault();
    
    const data = {
        name: document.getElementById('contactName').value,
        email: document.getElementById('contactEmail').value,
        position: document.getElementById('contactPosition').value,
        phone: document.getElementById('contactPhone').value,
        company_id: document.getElementById('contactCompany').value || null
    };
    
    try {
        const url = currentContactId ? `/api/contacts/${currentContactId}` : '/api/contacts';
        const method = currentContactId ? 'PUT' : 'POST';
        
        const response = await fetch(url, {
            method: method,
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || 'Failed to save contact');
        }
        
        closeModal();
        loadContacts();
    } catch (error) {
        alert('Error: ' + error.message);
    }
}

async function deleteContact(id) {
    if (!confirm('Are you sure you want to delete this contact? This will also delete all associated conversations.')) {
        return;
    }
    
    try {
        const response = await fetch(`/api/contacts/${id}`, { method: 'DELETE' });
        
        if (!response.ok) {
            throw new Error('Failed to delete contact');
        }
        
        loadContacts();
    } catch (error) {
        alert('Error: ' + error.message);
    }
}

function closeModal() {
    document.getElementById('contactModal').style.display = 'none';
}

// Close modal when clicking outside
window.onclick = function(event) {
    const modal = document.getElementById('contactModal');
    if (event.target == modal) {
        closeModal();
    }
}

loadContacts();
loadCompanies();
