/**
 * Main JavaScript file for Equipment Tracker
 */

document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM loaded - initializing app...');

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
    console.log('Setting up theme switcher...');
    setupThemeSwitcher();
    console.log('Theme switcher setup complete');
    
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
    // Ensure the button exists in the DOM
    const themeBtn = document.getElementById('theme-btn');
    console.log('Theme button found:', themeBtn);
    
    if (!themeBtn) {
        console.error('Theme button element not found');
        return;
    }
    
    // Check for saved theme preference or default to light theme
    const currentTheme = localStorage.getItem('theme') || 'light';
    console.log('Current theme from localStorage:', currentTheme);
    
    // Set initial button icon based on current theme
    if (currentTheme === 'dark') {
        themeBtn.innerHTML = '<i class="bi bi-sun-fill"></i>';
        console.log('Applying dark mode on page load');
        applyDarkMode(); // Apply dark mode on page load
    } else {
        themeBtn.innerHTML = '<i class="bi bi-moon-stars-fill"></i>';
        console.log('Ensuring light mode is applied');
        // Ensure light mode is properly applied
        removeDarkMode();
    }
    
    // Remove any existing click listeners to avoid duplicates
    const newThemeBtn = themeBtn.cloneNode(true);
    themeBtn.parentNode.replaceChild(newThemeBtn, themeBtn);
    
    // Toggle theme when button is clicked
    newThemeBtn.addEventListener('click', function(e) {
        console.log('Theme button clicked!');
        e.preventDefault();
        
        const isDarkMode = document.documentElement.classList.contains('dark-mode');
        console.log('Current dark mode state:', isDarkMode);
        
        if (isDarkMode) {
            // Switch to light mode
            console.log('Switching to light mode');
            removeDarkMode();
            localStorage.setItem('theme', 'light');
            this.innerHTML = '<i class="bi bi-moon-stars-fill"></i>';
        } else {
            // Switch to dark mode
            console.log('Switching to dark mode');
            applyDarkMode();
            localStorage.setItem('theme', 'dark');
            this.innerHTML = '<i class="bi bi-sun-fill"></i>';
        }
        
        // Add a highlight effect to show the button was clicked
        this.classList.add('btn-primary');
        setTimeout(() => {
            this.classList.remove('btn-primary');
        }, 300);
        
        console.log('Theme toggle complete');
    });
    
    // Explicitly make sure the button is clickable by adding this style
    newThemeBtn.style.cursor = 'pointer';
    newThemeBtn.title = 'Toggle dark/light mode';
    
    console.log('Theme switcher initialized successfully');
}

/**
 * Toggle theme function - can be called directly from HTML
 */
function toggleTheme(event) {
    if (event) {
        event.preventDefault();
    }
    
    console.log('toggleTheme called directly');
    
    const isDarkMode = document.documentElement.classList.contains('dark-mode');
    const themeBtn = document.getElementById('theme-btn');
    
    if (isDarkMode) {
        // Switch to light mode
        removeDarkMode();
        localStorage.setItem('theme', 'light');
        if (themeBtn) {
            themeBtn.innerHTML = '<i class="bi bi-moon-stars-fill"></i>';
        }
    } else {
        // Switch to dark mode
        applyDarkMode();
        localStorage.setItem('theme', 'dark');
        if (themeBtn) {
            themeBtn.innerHTML = '<i class="bi bi-sun-fill"></i>';
        }
    }
    
    // Add a highlight effect to show the button was clicked
    if (themeBtn) {
        themeBtn.classList.add('btn-primary');
        setTimeout(() => {
            themeBtn.classList.remove('btn-primary');
        }, 300);
    }
}

/**
 * Apply dark mode classes and styles to all elements
 */
function applyDarkMode() {
    document.documentElement.classList.add('dark-mode');
    document.body.classList.add('dark-mode');
    
    // Apply dark mode to SVGs and their containers
    const allSvgs = document.querySelectorAll('svg');
    allSvgs.forEach(svg => {
        if (svg.parentElement) {
            svg.parentElement.classList.add('dark-mode');
        }
        svg.classList.add('dark-mode');
    });
    
    // Apply dark mode to table elements
    const tables = document.querySelectorAll('table');
    tables.forEach(table => {
        table.classList.add('dark-mode');
    });
    
    // Update chart themes
    updateChartsForTheme('dark');
}

/**
 * Remove dark mode classes and restore light mode
 */
function removeDarkMode() {
    document.documentElement.classList.remove('dark-mode');
    document.body.classList.remove('dark-mode');
    
    // Remove dark mode from SVGs and their containers
    const allSvgs = document.querySelectorAll('svg');
    allSvgs.forEach(svg => {
        if (svg.parentElement) {
            svg.parentElement.classList.remove('dark-mode');
        }
        svg.classList.remove('dark-mode');
    });
    
    // Remove dark mode from table elements
    const tables = document.querySelectorAll('table');
    tables.forEach(table => {
        table.classList.remove('dark-mode');
    });
    
    // Update chart themes
    updateChartsForTheme('light');
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