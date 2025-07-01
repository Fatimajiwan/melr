// Offline data storage using IndexedDB
const dbName = 'meDashboardDB';
const dbVersion = 1;

// Initialize IndexedDB
const initDB = () => {
    return new Promise((resolve, reject) => {
        const request = indexedDB.open(dbName, dbVersion);

        request.onerror = (event) => {
            reject('Error opening database');
        };

        request.onsuccess = (event) => {
            resolve(event.target.result);
        };

        request.onupgradeneeded = (event) => {
            const db = event.target.result;

            // Create object stores
            if (!db.objectStoreNames.contains('measurements')) {
                db.createObjectStore('measurements', { keyPath: 'id', autoIncrement: true });
            }
            if (!db.objectStoreNames.contains('indicators')) {
                db.createObjectStore('indicators', { keyPath: 'id', autoIncrement: true });
            }
            if (!db.objectStoreNames.contains('projects')) {
                db.createObjectStore('projects', { keyPath: 'id', autoIncrement: true });
            }
        };
    });
};

// Store data offline
const storeOfflineData = async (storeName, data) => {
    const db = await initDB();
    return new Promise((resolve, reject) => {
        const transaction = db.transaction(storeName, 'readwrite');
        const store = transaction.objectStore(storeName);
        const request = store.add(data);

        request.onsuccess = () => resolve(request.result);
        request.onerror = () => reject(request.error);
    });
};

// Sync offline data when online
const syncOfflineData = async () => {
    const db = await initDB();
    const stores = ['measurements', 'indicators', 'projects'];

    for (const storeName of stores) {
        const transaction = db.transaction(storeName, 'readonly');
        const store = transaction.objectStore(storeName);
        const request = store.getAll();

        request.onsuccess = async () => {
            const offlineData = request.result;
            for (const data of offlineData) {
                try {
                    // Sync with server
                    await fetch(`/api/${storeName}`, {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify(data),
                    });
                    // Remove from offline storage after successful sync
                    const deleteTransaction = db.transaction(storeName, 'readwrite');
                    const deleteStore = deleteTransaction.objectStore(storeName);
                    deleteStore.delete(data.id);
                } catch (error) {
                    console.error(`Error syncing ${storeName}:`, error);
                }
            }
        };
    }
};

// Check online status and sync data
window.addEventListener('online', () => {
    syncOfflineData();
});

// Initialize offline storage
initDB().catch(console.error);

// Chart initialization
const initCharts = () => {
    const chartElements = document.querySelectorAll('[data-chart]');
    chartElements.forEach(element => {
        const chartType = element.dataset.chart;
        const data = JSON.parse(element.dataset.chartData);
        
        switch (chartType) {
            case 'line':
                Plotly.newPlot(element, [{
                    x: data.x,
                    y: data.y,
                    type: 'scatter',
                    mode: 'lines+markers',
                    name: data.name
                }], {
                    title: data.title,
                    xaxis: { title: data.xaxis },
                    yaxis: { title: data.yaxis }
                });
                break;
            case 'bar':
                Plotly.newPlot(element, [{
                    x: data.x,
                    y: data.y,
                    type: 'bar',
                    name: data.name
                }], {
                    title: data.title,
                    xaxis: { title: data.xaxis },
                    yaxis: { title: data.yaxis }
                });
                break;
            // Add more chart types as needed
        }
    });
};

// Initialize tooltips
document.addEventListener('DOMContentLoaded', function() {
    // Initialize Bootstrap tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Initialize popovers
    var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    var popoverList = popoverTriggerList.map(function(popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });
    
    // Add active class to current nav item
    const currentPath = window.location.pathname;
    const navLinks = document.querySelectorAll('.navbar-nav .nav-link');
    
    navLinks.forEach(link => {
        const linkPath = link.getAttribute('href');
        if (currentPath === linkPath || (linkPath !== '/' && currentPath.startsWith(linkPath))) {
            link.classList.add('active');
        }
    });
    
    // Add fade-in animation to cards
    const cards = document.querySelectorAll('.card');
    cards.forEach((card, index) => {
        setTimeout(() => {
            card.style.opacity = '1';
            card.style.transform = 'translateY(0)';
        }, 100 * index);
    });
});

// Display offline status
window.addEventListener('online', updateOnlineStatus);
window.addEventListener('offline', updateOnlineStatus);

function updateOnlineStatus() {
    const offlineIndicator = document.getElementById('offlineIndicator');
    if (offlineIndicator) {
        if (navigator.onLine) {
            offlineIndicator.style.display = 'none';
        } else {
            offlineIndicator.style.display = 'block';
        }
    }
}

// Add confirmation for delete actions
document.addEventListener('click', function(e) {
    if (e.target && e.target.classList.contains('btn-delete')) {
        if (!confirm('Are you sure you want to delete this item? This action cannot be undone.')) {
            e.preventDefault();
        }
    }
});

// Initialize data export functionality
function exportTableToCSV(tableId, filename = 'data.csv') {
    const table = document.getElementById(tableId);
    if (!table) return;
    
    const rows = table.querySelectorAll('tr');
    const csv = [];
    
    for (const row of rows) {
        const rowData = [];
        const cols = row.querySelectorAll('td, th');
        
        for (const col of cols) {
            // Remove HTML and clean up data
            let data = col.innerText.replace(/(\r\n|\n|\r)/gm, ' ').replace(/,/g, ';');
            rowData.push('"' + data + '"');
        }
        
        csv.push(rowData.join(','));
    }
    
    const csvContent = csv.join('\n');
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    const url = URL.createObjectURL(blob);
    
    link.setAttribute('href', url);
    link.setAttribute('download', filename);
    link.style.visibility = 'hidden';
    
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
}

// Add CSS styles programmatically
document.addEventListener('DOMContentLoaded', function() {
    // Add transitions to cards
    const style = document.createElement('style');
    style.textContent = `
        .card {
            transition: all 0.3s ease;
            opacity: 0;
            transform: translateY(20px);
        }
        
        .offlineIndicator {
            position: fixed;
            bottom: 20px;
            right: 20px;
            background-color: #dc3545;
            color: white;
            padding: 10px 15px;
            border-radius: 5px;
            display: none;
            z-index: 1000;
            box-shadow: 0 2px 10px rgba(0,0,0,0.2);
        }
    `;
    document.head.appendChild(style);
    
    // Create offline indicator
    const offlineIndicator = document.createElement('div');
    offlineIndicator.id = 'offlineIndicator';
    offlineIndicator.className = 'offlineIndicator';
    offlineIndicator.innerHTML = '<i class="fas fa-wifi-slash"></i> You are currently offline';
    document.body.appendChild(offlineIndicator);
    
    // Check initial status
    updateOnlineStatus();
});

// Document ready
document.addEventListener('DOMContentLoaded', () => {
    initCharts();
    initTooltips();

    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(function(alert) {
        setTimeout(function() {
            alert.style.opacity = '0';
            setTimeout(function() {
                alert.remove();
            }, 300);
        }, 3000);
    });
}); 