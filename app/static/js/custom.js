// Custom JavaScript functions

// Initialize Bootstrap components
document.addEventListener('DOMContentLoaded', function() {
    // Initialize all tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Initialize all popovers
    var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    var popoverList = popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });

    // Initialize all modals
    var modalTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="modal"]'));
    modalTriggerList.forEach(function(modalTriggerEl) {
        modalTriggerEl.addEventListener('click', function(event) {
            event.preventDefault();
            var targetModal = document.querySelector(this.getAttribute('data-bs-target'));
            var modal = new bootstrap.Modal(targetModal);
            modal.show();
        });
    });

    // Handle button actions
    document.querySelectorAll('[data-action]').forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            const action = this.dataset.action;
            const indicatorId = this.dataset.indicatorId;
            const indicatorName = this.dataset.indicatorName;

            switch(action) {
                case 'add-measurement':
                    document.getElementById('measurementIndicatorId').value = indicatorId;
                    document.getElementById('measurementIndicatorName').textContent = indicatorName;
                    break;
                case 'view-measurements':
                    loadMeasurements(indicatorId, indicatorName);
                    break;
                case 'edit-indicator':
                    loadIndicatorData(indicatorId);
                    break;
                case 'delete-indicator':
                    if (confirm('Are you sure you want to delete this indicator?')) {
                        deleteIndicator(indicatorId);
                    }
                    break;
            }
        });
    });

    // Add handlers for preview buttons
    document.querySelectorAll('[data-action="preview-report"]').forEach(button => {
        button.addEventListener('click', function() {
            const reportId = this.getAttribute('data-report-id');
            previewReport(reportId);
        });
    });

    // Add handlers for download buttons
    document.querySelectorAll('[data-action="download-report"]').forEach(button => {
        button.addEventListener('click', function() {
            const reportId = this.getAttribute('data-report-id');
            const format = this.getAttribute('data-format') || 'pdf';
            downloadReport(reportId, format);
        });
    });
});

// Load measurements for an indicator
function loadMeasurements(indicatorId, indicatorName) {
    fetch(`/api/indicator/${indicatorId}/measurements`)
        .then(response => response.json())
        .then(data => {
            const tbody = document.querySelector('#measurementsTable tbody');
            tbody.innerHTML = '';
            data.forEach(m => {
                const row = document.createElement('tr');
                row.innerHTML = `
                    <td>${new Date(m.date).toLocaleDateString()}</td>
                    <td>${m.value}</td>
                    <td>${m.notes || ''}</td>
                `;
                tbody.appendChild(row);
            });
            document.getElementById('measurementsIndicatorName').textContent = indicatorName;
        })
        .catch(error => console.error('Error loading measurements:', error));
}

// Load indicator data for editing
function loadIndicatorData(indicatorId) {
    fetch(`/api/indicator/${indicatorId}`)
        .then(response => response.json())
        .then(data => {
            document.getElementById('editIndicatorId').value = data.id;
            document.getElementById('editName').value = data.name;
            document.getElementById('editDescription').value = data.description;
            document.getElementById('editBaseline').value = data.baseline;
            document.getElementById('editCurrentValue').value = data.current_value;
            document.getElementById('editTargetValue').value = data.target_value;
            document.getElementById('editUnit').value = data.unit;
            document.getElementById('editFrequency').value = data.frequency;
        })
        .catch(error => console.error('Error loading indicator data:', error));
}

// Delete an indicator
function deleteIndicator(indicatorId) {
    const form = document.createElement('form');
    form.method = 'POST';
    form.action = `/projects/${projectId}/delete_indicator`;
    
    const csrfInput = document.createElement('input');
    csrfInput.type = 'hidden';
    csrfInput.name = 'csrf_token';
    csrfInput.value = document.querySelector('meta[name="csrf-token"]').content;
    
    const indicatorInput = document.createElement('input');
    indicatorInput.type = 'hidden';
    indicatorInput.name = 'indicator_id';
    indicatorInput.value = indicatorId;
    
    form.appendChild(csrfInput);
    form.appendChild(indicatorInput);
    document.body.appendChild(form);
    form.submit();
}

// Export table to CSV
function exportTableToCSV(tableId, filename = 'data.csv') {
    const table = document.getElementById(tableId);
    const rows = table.querySelectorAll('tr');
    
    let csv = [];
    for (const row of rows) {
        const cells = row.querySelectorAll('td, th');
        const rowData = Array.from(cells).map(cell => {
            let text = cell.textContent.trim();
            // Escape quotes and wrap in quotes if contains comma
            if (text.includes(',') || text.includes('"')) {
                text = `"${text.replace(/"/g, '""')}"`;
            }
            return text;
        });
        csv.push(rowData.join(','));
    }
    
    downloadCSV(csv.join('\n'), filename);
}

// Download CSV file
function downloadCSV(csv, filename) {
    const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    const url = URL.createObjectURL(blob);
    
    link.setAttribute('href', url);
    link.setAttribute('download', filename);
    link.style.visibility = 'hidden';
    
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
}

// Function to preview a report
function previewReport(reportId) {
    fetch(`/api/report/${reportId}/preview`)
        .then(response => response.json())
        .then(data => {
            // Create a modal to show the preview
            const modal = new bootstrap.Modal(document.getElementById('previewModal'));
            const previewContent = document.getElementById('previewContent');
            
            // Format the preview content based on report type
            let content = '';
            if (data.type === 'pdf') {
                content = `<iframe src="${data.preview_url}" width="100%" height="600px" frameborder="0"></iframe>`;
            } else if (data.type === 'excel') {
                content = `<div class="alert alert-info">
                    <i class="fas fa-info-circle me-2"></i>
                    Excel files cannot be previewed directly. Please download the file to view its contents.
                </div>`;
            } else {
                content = `<div class="table-responsive">
                    <table class="table table-bordered">
                        <thead>
                            <tr>
                                ${data.headers.map(header => `<th>${header}</th>`).join('')}
                            </tr>
                        </thead>
                        <tbody>
                            ${data.rows.map(row => `
                                <tr>
                                    ${row.map(cell => `<td>${cell}</td>`).join('')}
                                </tr>
                            `).join('')}
                        </tbody>
                    </table>
                </div>`;
            }
            
            previewContent.innerHTML = content;
            modal.show();
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Failed to load report preview. Please try again.');
        });
}

// Function to download a report
function downloadReport(reportId, format = 'pdf') {
    fetch(`/api/report/${reportId}/download?format=${format}`)
        .then(response => {
            if (!response.ok) throw new Error('Download failed');
            return response.blob();
        })
        .then(blob => {
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `report_${reportId}.${format}`;
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            a.remove();
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Failed to download report. Please try again.');
        });
} 