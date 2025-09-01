/**
 * Main JavaScript file for Quantum-Safe Cryptography Dashboard
 */

// Global variables
let loadingCount = 0;

// Utility functions
function showLoading() {
    loadingCount++;
    document.getElementById('loadingOverlay').classList.remove('d-none');
}

function hideLoading() {
    loadingCount = Math.max(0, loadingCount - 1);
    if (loadingCount === 0) {
        document.getElementById('loadingOverlay').classList.add('d-none');
    }
}

function formatBytes(bytes) {
    if (bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString() + ' ' + date.toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'});
}

function getAlgorithmType(algorithm) {
    const postQuantumAlgorithms = ['Dilithium', 'Falcon', 'SPHINCS'];
    return postQuantumAlgorithms.some(pq => algorithm.includes(pq)) ? 'post-quantum' : 'classical';
}

function getAlgorithmBadgeClass(algorithm) {
    return getAlgorithmType(algorithm) === 'post-quantum' ? 'bg-success' : 'bg-primary';
}

function copyToClipboard(text) {
    if (navigator.clipboard) {
        navigator.clipboard.writeText(text).then(() => {
            showToast('Copied to clipboard!', 'success');
        }).catch(err => {
            console.error('Failed to copy: ', err);
            showToast('Failed to copy to clipboard', 'danger');
        });
    } else {
        // Fallback for older browsers
        const textArea = document.createElement('textarea');
        textArea.value = text;
        document.body.appendChild(textArea);
        textArea.select();
        try {
            document.execCommand('copy');
            showToast('Copied to clipboard!', 'success');
        } catch (err) {
            console.error('Failed to copy: ', err);
            showToast('Failed to copy to clipboard', 'danger');
        }
        document.body.removeChild(textArea);
    }
}

function showToast(message, type = 'info') {
    const toastContainer = getToastContainer();
    
    const toast = document.createElement('div');
    toast.className = `toast align-items-center text-white bg-${type} border-0`;
    toast.setAttribute('role', 'alert');
    toast.innerHTML = `
        <div class="d-flex">
            <div class="toast-body">
                ${message}
            </div>
            <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
        </div>
    `;
    
    toastContainer.appendChild(toast);
    
    const bsToast = new bootstrap.Toast(toast);
    bsToast.show();
    
    // Remove toast element after it's hidden
    toast.addEventListener('hidden.bs.toast', () => {
        toast.remove();
    });
}

function getToastContainer() {
    let container = document.getElementById('toast-container');
    if (!container) {
        container = document.createElement('div');
        container.id = 'toast-container';
        container.className = 'position-fixed bottom-0 end-0 p-3';
        container.style.zIndex = '11';
        document.body.appendChild(container);
    }
    return container;
}

// API helper functions
async function apiRequest(url, options = {}) {
    try {
        const response = await fetch(url, {
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            },
            ...options
        });
        
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.error || `HTTP ${response.status}`);
        }
        
        return data;
    } catch (error) {
        console.error('API Request failed:', error);
        throw error;
    }
}

// Chart helper functions
function createPerformanceChart(containerId, data, title) {
    const ctx = document.getElementById(containerId).getContext('2d');
    
    return new Chart(ctx, {
        type: 'bar',
        data: {
            labels: Object.keys(data),
            datasets: [{
                label: title,
                data: Object.values(data),
                backgroundColor: Object.keys(data).map(alg => 
                    getAlgorithmType(alg) === 'post-quantum' ? '#198754' : '#0d6efd'
                ),
                borderColor: Object.keys(data).map(alg => 
                    getAlgorithmType(alg) === 'post-quantum' ? '#146c43' : '#0a58ca'
                ),
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                },
                title: {
                    display: true,
                    text: title
                }
            },
            scales: {
                y: {
                    beginAtZero: true
                }
            }
        }
    });
}

function createComparisonChart(containerId, algorithms, metrics) {
    const ctx = document.getElementById(containerId).getContext('2d');
    
    const datasets = Object.keys(metrics).map((metric, index) => {
        const colors = ['#0d6efd', '#198754', '#ffc107', '#dc3545', '#6f42c1'];
        return {
            label: metric,
            data: algorithms.map(alg => metrics[metric][alg] || 0),
            backgroundColor: colors[index % colors.length],
            borderColor: colors[index % colors.length],
            borderWidth: 2,
            fill: false
        };
    });
    
    return new Chart(ctx, {
        type: 'radar',
        data: {
            labels: algorithms,
            datasets: datasets
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'top'
                }
            },
            scales: {
                r: {
                    beginAtZero: true
                }
            }
        }
    });
}

// Table helper functions
function createDataTable(tableId, options = {}) {
    const table = document.getElementById(tableId);
    if (!table) return null;
    
    // Add Bootstrap classes
    table.classList.add('table', 'table-hover');
    
    // Add search functionality if requested
    if (options.search) {
        addTableSearch(table);
    }
    
    // Add sorting functionality if requested
    if (options.sort) {
        addTableSorting(table);
    }
    
    return table;
}

function addTableSearch(table) {
    const searchContainer = document.createElement('div');
    searchContainer.className = 'mb-3';
    searchContainer.innerHTML = `
        <div class="input-group">
            <span class="input-group-text">
                <i class="bi bi-search"></i>
            </span>
            <input type="text" class="form-control" placeholder="Search..." id="${table.id}-search">
        </div>
    `;
    
    table.parentNode.insertBefore(searchContainer, table);
    
    const searchInput = document.getElementById(`${table.id}-search`);
    searchInput.addEventListener('input', (e) => {
        const searchTerm = e.target.value.toLowerCase();
        const rows = table.querySelectorAll('tbody tr');
        
        rows.forEach(row => {
            const text = row.textContent.toLowerCase();
            row.style.display = text.includes(searchTerm) ? '' : 'none';
        });
    });
}

function addTableSorting(table) {
    const headers = table.querySelectorAll('th');
    headers.forEach((header, index) => {
        header.style.cursor = 'pointer';
        header.addEventListener('click', () => {
            sortTable(table, index);
        });
    });
}

function sortTable(table, columnIndex) {
    const tbody = table.querySelector('tbody');
    const rows = Array.from(tbody.querySelectorAll('tr'));
    
    const sorted = rows.sort((a, b) => {
        const aValue = a.children[columnIndex].textContent.trim();
        const bValue = b.children[columnIndex].textContent.trim();
        
        // Try to parse as numbers
        const aNum = parseFloat(aValue);
        const bNum = parseFloat(bValue);
        
        if (!isNaN(aNum) && !isNaN(bNum)) {
            return aNum - bNum;
        }
        
        return aValue.localeCompare(bValue);
    });
    
    // Clear tbody and append sorted rows
    tbody.innerHTML = '';
    sorted.forEach(row => tbody.appendChild(row));
}

// Form validation helpers
function validateForm(formId, rules) {
    const form = document.getElementById(formId);
    if (!form) return false;
    
    let isValid = true;
    
    Object.keys(rules).forEach(fieldName => {
        const field = form.querySelector(`[name="${fieldName}"]`);
        if (!field) return;
        
        const rule = rules[fieldName];
        const value = field.value.trim();
        
        // Clear previous validation
        field.classList.remove('is-invalid', 'is-valid');
        
        let fieldValid = true;
        
        // Required validation
        if (rule.required && !value) {
            fieldValid = false;
            showFieldError(field, 'This field is required');
        }
        
        // Min length validation
        if (rule.minLength && value.length < rule.minLength) {
            fieldValid = false;
            showFieldError(field, `Minimum length is ${rule.minLength} characters`);
        }
        
        // Custom validation function
        if (rule.validator && typeof rule.validator === 'function') {
            const customResult = rule.validator(value);
            if (customResult !== true) {
                fieldValid = false;
                showFieldError(field, customResult);
            }
        }
        
        if (fieldValid) {
            field.classList.add('is-valid');
        } else {
            field.classList.add('is-invalid');
            isValid = false;
        }
    });
    
    return isValid;
}

function showFieldError(field, message) {
    // Remove existing feedback
    const existingFeedback = field.parentNode.querySelector('.invalid-feedback');
    if (existingFeedback) {
        existingFeedback.remove();
    }
    
    // Add new feedback
    const feedback = document.createElement('div');
    feedback.className = 'invalid-feedback';
    feedback.textContent = message;
    field.parentNode.appendChild(feedback);
}

// Initialize tooltips and popovers
function initializeBootstrapComponents() {
    // Initialize tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Initialize popovers
    const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });
}

// Export/Import functionality
function exportData(data, filename, type = 'json') {
    let content, mimeType;
    
    switch (type) {
        case 'json':
            content = JSON.stringify(data, null, 2);
            mimeType = 'application/json';
            break;
        case 'csv':
            content = convertToCSV(data);
            mimeType = 'text/csv';
            break;
        default:
            throw new Error('Unsupported export type');
    }
    
    const blob = new Blob([content], { type: mimeType });
    const url = window.URL.createObjectURL(blob);
    
    const a = document.createElement('a');
    a.href = url;
    a.download = `${filename}.${type}`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    window.URL.revokeObjectURL(url);
}

function convertToCSV(data) {
    if (!Array.isArray(data) || data.length === 0) {
        return '';
    }
    
    const headers = Object.keys(data[0]);
    const csvRows = [headers.join(',')];
    
    data.forEach(row => {
        const values = headers.map(header => {
            const value = row[header];
            // Escape quotes and wrap in quotes if necessary
            return typeof value === 'string' && value.includes(',') 
                ? `"${value.replace(/"/g, '""')}"` 
                : value;
        });
        csvRows.push(values.join(','));
    });
    
    return csvRows.join('\n');
}

// Initialize everything when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    initializeBootstrapComponents();
    
    // Add global error handler
    window.addEventListener('unhandledrejection', function(event) {
        console.error('Unhandled promise rejection:', event.reason);
        showToast('An unexpected error occurred', 'danger');
    });
    
    // Auto-refresh data every 30 seconds on dashboard
    if (window.location.pathname === '/') {
        setInterval(() => {
            if (typeof refreshStats === 'function') {
                refreshStats();
            }
        }, 30000);
    }
});

// Make functions available globally
window.showLoading = showLoading;
window.hideLoading = hideLoading;
window.formatBytes = formatBytes;
window.formatDate = formatDate;
window.getAlgorithmType = getAlgorithmType;
window.getAlgorithmBadgeClass = getAlgorithmBadgeClass;
window.copyToClipboard = copyToClipboard;
window.showToast = showToast;
window.apiRequest = apiRequest;
window.createPerformanceChart = createPerformanceChart;
window.createComparisonChart = createComparisonChart;
window.createDataTable = createDataTable;
window.validateForm = validateForm;
window.exportData = exportData;
