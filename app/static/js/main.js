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
    
    // Set up theme switcher
    setupThemeSwitcher();
    
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

/**
 * Set up theme switcher functionality
 */
function setupThemeSwitcher() {
    const themeBtn = document.getElementById('theme-btn');
    if (!themeBtn) {
        console.warn('Theme button element not found');
        return;
    }
    
    // Check for saved theme preference or default to light theme
    const currentTheme = localStorage.getItem('theme') || 'light';
    
    // Set initial button icon based on current theme
    if (currentTheme === 'dark') {
        themeBtn.innerHTML = '<i class="bi bi-sun-fill"></i>';
        // Update chart themes
        updateChartsForTheme('dark');
    } else {
        themeBtn.innerHTML = '<i class="bi bi-moon-stars-fill"></i>';
    }
    
    // Toggle theme when button is clicked
    themeBtn.addEventListener('click', function() {
        const isDarkMode = document.documentElement.classList.contains('dark-mode');
        
        if (isDarkMode) {
            // Switch to light mode
            document.documentElement.classList.remove('dark-mode');
            document.body.classList.remove('dark-mode');
            localStorage.setItem('theme', 'light');
            themeBtn.innerHTML = '<i class="bi bi-moon-stars-fill"></i>';
            updateChartsForTheme('light');
        } else {
            // Switch to dark mode
            document.documentElement.classList.add('dark-mode');
            document.body.classList.add('dark-mode');
            localStorage.setItem('theme', 'dark');
            themeBtn.innerHTML = '<i class="bi bi-sun-fill"></i>';
            updateChartsForTheme('dark');
        }
        
        // Add a highlight effect to show the button was clicked
        themeBtn.classList.add('btn-primary');
        setTimeout(() => {
            themeBtn.classList.remove('btn-primary');
        }, 300);
    });
}

/**
 * Update chart colors for the current theme
 * @param {string} theme - The current theme ('light' or 'dark')
 */
function updateChartsForTheme(theme) {
    // Update any Chart.js charts on the page
    if (typeof Chart !== 'undefined') {
        Chart.helpers.each(Chart.instances, function(chart) {
            // Only update if the chart has a config with options
            if (chart.config && chart.config.options) {
                
                // Update grid and text colors
                if (chart.config.options.scales) {
                    for (const axis in chart.config.options.scales) {
                        const scale = chart.config.options.scales[axis];
                        
                        if (scale.grid) {
                            scale.grid.color = theme === 'dark' ? 'rgba(255, 255, 255, 0.1)' : 'rgba(0, 0, 0, 0.1)';
                        }
                        
                        if (scale.ticks) {
                            scale.ticks.color = theme === 'dark' ? '#adb5bd' : '#666';
                        }
                    }
                }
                
                // Update title and legend colors
                if (chart.config.options.plugins && chart.config.options.plugins.title) {
                    chart.config.options.plugins.title.color = theme === 'dark' ? '#fff' : '#000';
                }
                
                if (chart.config.options.plugins && chart.config.options.plugins.legend) {
                    chart.config.options.plugins.legend.labels = chart.config.options.plugins.legend.labels || {};
                    chart.config.options.plugins.legend.labels.color = theme === 'dark' ? '#adb5bd' : '#666';
                }
                
                // Update the chart
                chart.update();
            }
        });
    }
}