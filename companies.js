let companies = [];
let currentCompanyId = null;

async function loadCompanies() {
    try {
        const response = await fetch('/api/companies');
        companies = await response.json();
        renderCompanies(companies);
    } catch (error) {
        console.error('Error loading companies:', error);
    }
}

function renderCompanies(data) {
    const tbody = document.getElementById('companiesBody');
    
    if (data.length === 0) {
        tbody.innerHTML = '<tr><td colspan="7" style="text-align: center; color: #999;">No companies found</td></tr>';
        return;
    }
    
    tbody.innerHTML = data.map(company => `
        <tr>
            <td><strong>${company.name}</strong></td>
            <td>${company.domain || '-'}</td>
            <td>${company.industry || '-'}</td>
            <td>${company.phone || '-'}</td>
            <td>${company.contact_count || 0}</td>
            <td>${new Date(company.created_at).toLocaleDateString()}</td>
            <td>
                <button class="btn-primary btn-small" onclick="editCompany(${company.id})">Edit</button>
                <button class="btn-danger btn-small" onclick="deleteCompany(${company.id})">Delete</button>
            </td>
        </tr>
    `).join('');
}

function searchCompanies() {
    const search = document.getElementById('searchInput').value.toLowerCase();
    const filtered = companies.filter(c => 
        c.name.toLowerCase().includes(search) ||
        (c.domain && c.domain.toLowerCase().includes(search)) ||
        (c.industry && c.industry.toLowerCase().includes(search))
    );
    renderCompanies(filtered);
}

function showAddModal() {
    currentCompanyId = null;
    document.getElementById('modalTitle').textContent = 'Add Company';
    document.getElementById('companyForm').reset();
    document.getElementById('companyId').value = '';
    document.getElementById('companyModal').style.display = 'block';
}

async function editCompany(id) {
    try {
        const response = await fetch(`/api/companies/${id}`);
        const company = await response.json();
        
        currentCompanyId = id;
        document.getElementById('modalTitle').textContent = 'Edit Company';
        document.getElementById('companyId').value = id;
        document.getElementById('companyName').value = company.name;
        document.getElementById('companyDomain').value = company.domain || '';
        document.getElementById('companyIndustry').value = company.industry || '';
        document.getElementById('companyPhone').value = company.phone || '';
        document.getElementById('companyAddress').value = company.address || '';
        document.getElementById('companyModal').style.display = 'block';
    } catch (error) {
        alert('Error loading company: ' + error.message);
    }
}

async function saveCompany(event) {
    event.preventDefault();
    
    const data = {
        name: document.getElementById('companyName').value,
        domain: document.getElementById('companyDomain').value,
        industry: document.getElementById('companyIndustry').value,
        phone: document.getElementById('companyPhone').value,
        address: document.getElementById('companyAddress').value
    };
    
    try {
        const url = currentCompanyId ? `/api/companies/${currentCompanyId}` : '/api/companies';
        const method = currentCompanyId ? 'PUT' : 'POST';
        
        const response = await fetch(url, {
            method: method,
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || 'Failed to save company');
        }
        
        closeModal();
        loadCompanies();
    } catch (error) {
        alert('Error: ' + error.message);
    }
}

async function deleteCompany(id) {
    if (!confirm('Are you sure you want to delete this company? This will also delete all associated contacts and conversations.')) {
        return;
    }
    
    try {
        const response = await fetch(`/api/companies/${id}`, { method: 'DELETE' });
        
        if (!response.ok) {
            throw new Error('Failed to delete company');
        }
        
        loadCompanies();
    } catch (error) {
        alert('Error: ' + error.message);
    }
}

function closeModal() {
    document.getElementById('companyModal').style.display = 'none';
}

// Close modal when clicking outside
window.onclick = function(event) {
    const modal = document.getElementById('companyModal');
    if (event.target == modal) {
        closeModal();
    }
}

loadCompanies();
