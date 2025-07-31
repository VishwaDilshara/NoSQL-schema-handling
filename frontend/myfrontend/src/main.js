// src/main.js

async function fetchEmployees() {
  try {
    const response = await fetch('http://localhost:5000/api/employees'); // ✅ Your Flask/Node API
    if (!response.ok) throw new Error("Failed to fetch employees");
    const employees = await response.json();
    displayEmployees(employees);
  } catch (error) {
    document.getElementById('employeesList').innerHTML = `
      <div class="alert alert-danger">
        Failed to load employees. Please try again later.
        <div class="text-muted">${error.message}</div>
      </div>`;
    console.error('Error:', error);
  }
}

function displayEmployees(employees) {
  const container = document.getElementById('employeesList');
  if (!employees || employees.length === 0) {
    container.innerHTML = `
      <div class="no-employees">
        <h4>No employees found</h4>
        <p>Add your first employee to get started</p>
        <a href="test.html" class="btn btn-primary mt-2">Add Employee</a>
      </div>`;
    return;
  }

  container.innerHTML = employees.map(employee => `
    <div class="card employee-card mb-3">
      <div class="employee-header" onclick="toggleDetails('${employee._id}')">
        <div class="d-flex justify-content-between align-items-center">
          <h5 class="mb-0">${employee.name.firstName} ${employee.name.lastName}</h5>
          <span class="badge bg-primary">${employee.nic}</span>
        </div>
      </div>
      <div id="details-${employee._id}" class="employee-details">
        <div class="row">
          <div class="col-md-6">
            <p class="section-title">Personal Information</p>
            <p><strong>First Name:</strong> ${employee.name.firstName || '-'}</p>
            <p><strong>Last Name:</strong> ${employee.name.lastName || '-'}</p>
            <p><strong>NIC:</strong> ${employee.nic || '-'}</p>
          </div>
          <div class="col-md-6">
            <p class="section-title">Address</p>
            <p>${employee.address.street || ''}</p>
            <p>${employee.address.city || ''} ${employee.address.state ? ', ' + employee.address.state : ''}</p>
            <p>${employee.address.country || ''} ${employee.address.zipCode ? ', ' + employee.address.zipCode : ''}</p>
          </div>
        </div>
        ${displayQualifications(employee.educationalQualifications || {})}
      </div>
    </div>`).join('');
}

function displayQualifications(qualifications) {
  if (!qualifications || Object.keys(qualifications).length === 0) {
    return '<p class="text-muted mt-3">No qualifications added.</p>';
  }

  let html = '<div class="mt-4"><p class="section-title">Qualifications</p>';

  if (qualifications.education && qualifications.education.length > 0) {
    html += '<div class="mb-3"><h6>Education</h6>';
    html += qualifications.education.map(edu => 
      `<div class="card mb-2"><div class="card-body p-2">
        <h6 class="card-title mb-1">${edu.degree || 'No degree specified'}</h6>
        <p class="card-text mb-1 small">${edu.institution || ''} ${edu.year ? '(' + edu.year + ')' : ''}</p>
      </div></div>`).join('');
    html += '</div>';
  }

  if (qualifications.certification && qualifications.certification.length > 0) {
    html += '<div class="mb-3"><h6>Certifications</h6>';
    html += qualifications.certification.map(cert => 
      `<span class="badge bg-success qualification-badge">
        ${cert.degree || 'Certification'} ${cert.year ? '(' + cert.year + ')' : ''}
      </span>`).join('');
    html += '</div>';
  }

  if (qualifications.experience && qualifications.experience.length > 0) {
    html += '<div class="mb-3"><h6>Experience</h6>';
    html += qualifications.experience.map(exp => 
      `<div class="card mb-2"><div class="card-body p-2">
        <h6 class="card-title mb-1">${exp.degree || 'Experience'}</h6>
        <p class="card-text mb-1 small">${exp.institution || ''} ${exp.year ? '(' + exp.year + ')' : ''}</p>
      </div></div>`).join('');
    html += '</div>';
  }

  return html + '</div>';
}

window.toggleDetails = function(employeeId) {
  const details = document.getElementById(`details-${employeeId}`);
  if (details.style.display === 'block') {
    details.style.display = 'none';
  } else {
    document.querySelectorAll('.employee-details').forEach(el => {
      if (el.id !== `details-${employeeId}`) el.style.display = 'none';
    });
    details.style.display = 'block';
  }
};

document.addEventListener('DOMContentLoaded', fetchEmployees);
