/**
 * Main JavaScript file for Equipment Tracker
 */

document.addEventListener('DOMContentLoaded', function() {
    // Enable tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Enable popovers
    var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });
    
    // Set up search interactions
    setupSearch();
    
    // Set up data tables if the library is loaded
    setupDataTables();
    
    // Add fade-out to alerts after 3 seconds
    setTimeout(function() {
        document.querySelectorAll('.alert').forEach(function(alert) {
            alert.classList.add('fade');
            setTimeout(function() {
                alert.remove();
            }, 500);
        });
    }, 3000);
});

/**
 * Set up search functionality
 */
function setupSearch() {
    var searchInput = document.querySelector('input[type="search"]');
    if (!searchInput) return;
    
    // Clear search when 'x' is clicked
    searchInput.addEventListener('search', function(e) {
        if (this.value === '') {
            window.location.href = window.location.pathname;
        }
    });
}

/**
 * Set up DataTables if the library is loaded
 */
function setupDataTables() {
    if (typeof $.fn.DataTable !== 'undefined') {
        $('.data-table').DataTable({
            responsive: true,
            pageLength: 25,
            language: {
                search: "Filter:",
                lengthMenu: "Show _MENU_ entries per page",
                info: "Showing _START_ to _END_ of _TOTAL_ entries",
                infoEmpty: "Showing 0 to 0 of 0 entries",
                infoFiltered: "(filtered from _MAX_ total entries)"
            }
        });
    }
}

/**
 * Format a date string to a readable format
 * @param {string} dateString - Date string to format
 * @returns {string} Formatted date string
 */
function formatDate(dateString) {
    if (!dateString) return '';
    
    try {
        const date = new Date(dateString);
        return new Intl.DateTimeFormat('en-US', {
            year: 'numeric',
            month: 'short',
            day: 'numeric'
        }).format(date);
    } catch (e) {
        return dateString;
    }
}

/**
 * Fetch data from the API
 * @param {string} endpoint - API endpoint to fetch from
 * @param {Object} params - Query parameters
 * @returns {Promise} Promise resolving to the API response
 */
async function fetchFromApi(endpoint, params = {}) {
    const url = new URL(endpoint, window.location.origin);
    
    // Add query parameters
    Object.keys(params).forEach(key => {
        if (params[key] !== undefined && params[key] !== null) {
            url.searchParams.append(key, params[key]);
        }
    });
    
    try {
        const response = await fetch(url);
        if (!response.ok) {
            throw new Error(`API error: ${response.status}`);
        }
        return await response.json();
    } catch (error) {
        console.error('Error fetching from API:', error);
        throw error;
    }
}