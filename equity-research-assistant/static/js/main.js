// Main JavaScript for Equity Research Assistant

document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // File upload validation
    setupFileUploadValidation();
    
    // Auto-save functionality for forms
    setupAutoSave();
    
    // Form submission loading states
    setupFormLoadingStates();
    
    // Progress tracking
    updateProgressIndicators();
});

/**
 * Setup file upload validation
 */
function setupFileUploadValidation() {
    const excelInput = document.getElementById('excel_file');
    const pdfInput = document.getElementById('pdf_file');
    
    if (excelInput) {
        excelInput.addEventListener('change', function(e) {
            validateFileUpload(e.target, ['xlsx', 'xls'], 50);
        });
    }
    
    if (pdfInput) {
        pdfInput.addEventListener('change', function(e) {
            validateFileUpload(e.target, ['pdf'], 50);
        });
    }
}

/**
 * Validate file upload
 */
function validateFileUpload(input, allowedExtensions, maxSizeMB) {
    const file = input.files[0];
    if (!file) return;
    
    const fileName = file.name.toLowerCase();
    const fileExtension = fileName.split('.').pop();
    const fileSizeMB = file.size / (1024 * 1024);
    
    // Check file extension
    if (!allowedExtensions.includes(fileExtension)) {
        showAlert('danger', `Invalid file type. Please upload a ${allowedExtensions.join(' or ')} file.`);
        input.value = '';
        return false;
    }
    
    // Check file size
    if (fileSizeMB > maxSizeMB) {
        showAlert('danger', `File size too large. Maximum size is ${maxSizeMB}MB.`);
        input.value = '';
        return false;
    }
    
    // Show success message
    showAlert('success', `File "${file.name}" selected successfully.`, 3000);
    return true;
}

/**
 * Setup auto-save functionality
 */
function setupAutoSave() {
    const textareas = document.querySelectorAll('textarea[name]');
    let autoSaveTimeout;
    
    textareas.forEach(textarea => {
        textarea.addEventListener('input', function() {
            clearTimeout(autoSaveTimeout);
            
            // Show auto-save indicator
            showAutoSaveIndicator();
            
            autoSaveTimeout = setTimeout(() => {
                saveFormData();
            }, 2000); // Save after 2 seconds of inactivity
        });
    });
}

/**
 * Setup form loading states
 */
function setupFormLoadingStates() {
    const forms = document.querySelectorAll('form');
    
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            const submitBtn = form.querySelector('button[type="submit"]');
            if (submitBtn) {
                setButtonLoading(submitBtn, true);
                
                // Prevent double submission
                setTimeout(() => {
                    submitBtn.disabled = true;
                }, 100);
            }
        });
    });
}

/**
 * Update progress indicators
 */
function updateProgressIndicators() {
    const progressBar = document.querySelector('.progress-bar');
    if (progressBar) {
        const currentStep = parseInt(progressBar.getAttribute('aria-valuenow'));
        const maxSteps = parseInt(progressBar.getAttribute('aria-valuemax'));
        const percentage = (currentStep / maxSteps) * 100;
        
        // Animate progress bar
        setTimeout(() => {
            progressBar.style.width = percentage + '%';
        }, 300);
    }
}

/**
 * Show alert message
 */
function showAlert(type, message, duration = 5000) {
    const alertContainer = document.querySelector('.container');
    if (!alertContainer) return;
    
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
    alertDiv.innerHTML = `
        <i class="fas fa-${getAlertIcon(type)} me-2"></i>
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    // Insert after the first child (usually the progress bar)
    alertContainer.insertBefore(alertDiv, alertContainer.children[1]);
    
    // Auto-dismiss
    if (duration > 0) {
        setTimeout(() => {
            if (alertDiv.parentNode) {
                alertDiv.remove();
            }
        }, duration);
    }
}

/**
 * Get appropriate icon for alert type
 */
function getAlertIcon(type) {
    const icons = {
        'success': 'check-circle',
        'danger': 'exclamation-triangle',
        'warning': 'exclamation-circle',
        'info': 'info-circle'
    };
    return icons[type] || 'info-circle';
}

/**
 * Show auto-save indicator
 */
function showAutoSaveIndicator() {
    let indicator = document.getElementById('autoSaveIndicator');
    
    if (!indicator) {
        indicator = document.createElement('div');
        indicator.id = 'autoSaveIndicator';
        indicator.className = 'position-fixed top-0 end-0 p-3';
        indicator.style.zIndex = '1050';
        document.body.appendChild(indicator);
    }
    
    indicator.innerHTML = `
        <div class="toast show" role="alert">
            <div class="toast-body">
                <i class="fas fa-spinner fa-spin me-2"></i>
                Auto-saving...
            </div>
        </div>
    `;
    
    // Hide after 2 seconds
    setTimeout(() => {
        indicator.innerHTML = `
            <div class="toast show" role="alert">
                <div class="toast-body text-success">
                    <i class="fas fa-check me-2"></i>
                    Saved
                </div>
            </div>
        `;
        
        setTimeout(() => {
            indicator.innerHTML = '';
        }, 1000);
    }, 2000);
}

/**
 * Save form data via AJAX
 */
function saveFormData() {
    const form = document.getElementById('analysisForm');
    if (!form) return;
    
    const formData = new FormData(form);
    
    fetch(form.action, {
        method: 'POST',
        body: formData
    })
    .then(response => {
        if (response.redirected) {
            // If redirected, it means there was an error or success message
            // Let the page handle the redirect naturally
            return;
        }
        return response.json();
    })
    .catch(error => {
        console.error('Auto-save error:', error);
    });
}

/**
 * Set button loading state
 */
function setButtonLoading(button, isLoading) {
    if (isLoading) {
        button.setAttribute('data-original-text', button.innerHTML);
        button.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Loading...';
        button.disabled = true;
    } else {
        const originalText = button.getAttribute('data-original-text');
        if (originalText) {
            button.innerHTML = originalText;
        }
        button.disabled = false;
    }
}

/**
 * Format numbers for display
 */
function formatNumber(num) {
    if (num === null || num === undefined) return 'N/A';
    
    if (Math.abs(num) >= 1e9) {
        return (num / 1e9).toFixed(1) + 'B';
    } else if (Math.abs(num) >= 1e6) {
        return (num / 1e6).toFixed(1) + 'M';
    } else if (Math.abs(num) >= 1e3) {
        return (num / 1e3).toFixed(1) + 'K';
    }
    
    return num.toLocaleString();
}

/**
 * Copy text to clipboard
 */
function copyToClipboard(text) {
    if (navigator.clipboard) {
        navigator.clipboard.writeText(text).then(() => {
            showAlert('success', 'Copied to clipboard!', 2000);
        });
    } else {
        // Fallback for older browsers
        const textArea = document.createElement('textarea');
        textArea.value = text;
        document.body.appendChild(textArea);
        textArea.select();
        document.execCommand('copy');
        document.body.removeChild(textArea);
        showAlert('success', 'Copied to clipboard!', 2000);
    }
}

/**
 * Smooth scroll to element
 */
function scrollToElement(elementId) {
    const element = document.getElementById(elementId);
    if (element) {
        element.scrollIntoView({
            behavior: 'smooth',
            block: 'start'
        });
    }
}

/**
 * Initialize data tables if present
 */
function initializeDataTables() {
    const tables = document.querySelectorAll('.data-table');
    
    tables.forEach(table => {
        // Add sorting functionality
        const headers = table.querySelectorAll('th[data-sortable="true"]');
        headers.forEach(header => {
            header.style.cursor = 'pointer';
            header.addEventListener('click', () => {
                sortTable(table, header);
            });
        });
    });
}

/**
 * Sort table by column
 */
function sortTable(table, header) {
    const columnIndex = Array.from(header.parentNode.children).indexOf(header);
    const rows = Array.from(table.querySelectorAll('tbody tr'));
    const isNumeric = header.getAttribute('data-type') === 'numeric';
    const isAscending = header.getAttribute('data-sort') !== 'asc';
    
    rows.sort((a, b) => {
        const aValue = a.cells[columnIndex].textContent.trim();
        const bValue = b.cells[columnIndex].textContent.trim();
        
        if (isNumeric) {
            const aNum = parseFloat(aValue.replace(/[^\d.-]/g, ''));
            const bNum = parseFloat(bValue.replace(/[^\d.-]/g, ''));
            return isAscending ? aNum - bNum : bNum - aNum;
        } else {
            return isAscending ? 
                aValue.localeCompare(bValue) : 
                bValue.localeCompare(aValue);
        }
    });
    
    // Update table
    const tbody = table.querySelector('tbody');
    rows.forEach(row => tbody.appendChild(row));
    
    // Update sort indicator
    header.setAttribute('data-sort', isAscending ? 'asc' : 'desc');
    
    // Clear other sort indicators
    header.parentNode.querySelectorAll('th').forEach(th => {
        if (th !== header) {
            th.removeAttribute('data-sort');
        }
    });
}

// Initialize data tables when DOM is loaded
document.addEventListener('DOMContentLoaded', initializeDataTables);
