/**
 * Unified Theme Switcher for Equipment Tracker
 * Complete solution for theme switching that properly persists across pages
 * Supports Light, Dark, and Dracula themes
 */

// This script is loaded in the <head> so it runs before page rendering
// Version 1.1 - May 2025 (added vampire icon and fixed persistence)
(function() {
    // Apply theme based on localStorage immediately to prevent flashing
    const savedTheme = localStorage.getItem('theme') || 'light';
    console.log('Initial theme from localStorage:', savedTheme);

    // Apply theme classes directly to <html> and <body> for immediate effect
    if (savedTheme === 'dark') {
        document.documentElement.classList.add('dark-mode');
        document.body.classList.add('dark-mode');
    }
    else if (savedTheme === 'dracula') {
        document.documentElement.classList.add('dracula-mode');
        document.body.classList.add('dracula-mode');
    }

    // Immediately save the theme to localStorage to ensure it persists
    // This helps when the page is reloaded or navigated to
    localStorage.setItem('theme', savedTheme);

    // Run the full theme setup after DOM is loaded
    document.addEventListener('DOMContentLoaded', function() {
        console.log('DOM loaded - setting up theme switcher');
        setupUnifiedThemeSwitcher();

        // Apply the theme again to make sure it's properly applied
        applyTheme(savedTheme);

        // Force update the theme icon immediately
        updateThemeButtonIcon(savedTheme);

        // Add window focus event to reapply theme when returning to the page
        window.addEventListener('focus', function() {
            const currentTheme = localStorage.getItem('theme') || 'light';
            console.log('Window focused - reapplying theme:', currentTheme);
            applyTheme(currentTheme);
        });

        // Log the current theme for debugging
        console.log('Theme setup complete. Current theme:', savedTheme);
    });
})();

/**
 * Set up the theme switcher with proper cycling through all themes
 */
function setupUnifiedThemeSwitcher() {
    console.log('Setting up unified theme switcher...');
    
    // Apply the currently saved theme
    const currentTheme = localStorage.getItem('theme') || 'light';
    applyTheme(currentTheme);
    updateThemeButtonIcon(currentTheme);
    
    // Get the theme button - the button already has an onclick handler in the HTML
    const themeBtn = document.getElementById('theme-btn');
    if (!themeBtn) {
        console.error('Theme button not found in the DOM');
        return;
    }
    
    // We don't need to add event listeners here since we're using the onclick attribute
    // But we ensure the button is styled correctly
    themeBtn.style.cursor = 'pointer';
    themeBtn.title = 'Toggle theme (Light/Dark/Dracula)';
    
    console.log('Unified theme switcher setup complete with theme:', currentTheme);
}

/**
 * Apply a specific theme
 * @param {string} theme - The theme to apply ('light', 'dark', or 'dracula')
 */
function applyTheme(theme) {
    console.log('Applying theme:', theme);
    
    // First ensure we have a valid theme
    if (!theme || !['light', 'dark', 'dracula'].includes(theme)) {
        console.warn('Invalid theme specified:', theme, 'defaulting to light');
        theme = 'light';
    }
    
    // Reset all themes first - important for a clean state
    document.documentElement.classList.remove('dark-mode', 'dracula-mode');
    document.body.classList.remove('dark-mode', 'dracula-mode');
    
    // Apply the specified theme
    if (theme === 'dark') {
        document.documentElement.classList.add('dark-mode');
        document.body.classList.add('dark-mode');
    }
    else if (theme === 'dracula') {
        document.documentElement.classList.add('dracula-mode');
        document.body.classList.add('dracula-mode');
    }
    
    // Always save the theme preference to localStorage - crucial for persistence
    localStorage.setItem('theme', theme);
    
    // Log what we're saving to localStorage
    console.log('Saving theme to localStorage:', theme);
    
    // Toggle logo visibility based on theme
    toggleLogosForTheme(theme);
    
    // Apply theme to additional elements
    applyThemeToElements(theme);
    
    // Update the button icon to match the current theme
    updateThemeButtonIcon(theme);
    
    console.log('Theme fully applied:', theme);
}

/**
 * Toggle logo visibility based on theme
 * @param {string} theme - The current theme
 */
function toggleLogosForTheme(theme) {
    const lightLogos = document.querySelectorAll('.light-mode-logo');
    const darkLogos = document.querySelectorAll('.dark-mode-logo');
    
    if (theme === 'light') {
        // Show transparent logos, hide non-transparent ones
        lightLogos.forEach(logo => logo.classList.remove('d-none'));
        darkLogos.forEach(logo => logo.classList.add('d-none'));
    } else {
        // Show non-transparent logos, hide transparent ones
        lightLogos.forEach(logo => logo.classList.add('d-none'));
        darkLogos.forEach(logo => logo.classList.remove('d-none'));
    }
}

/**
 * Apply theme-specific classes to additional elements
 * @param {string} theme - The current theme
 */
function applyThemeToElements(theme) {
    if (theme === 'light') {
        // Remove theme classes from all elements
        document.querySelectorAll('table, .card, .footer, footer').forEach(el => {
            el.classList.remove('dark-mode', 'dracula-mode');
        });
        return;
    }
    
    // Apply theme class to tables, cards, etc.
    document.querySelectorAll('table, .card, .footer, footer').forEach(el => {
        el.classList.remove('dark-mode', 'dracula-mode');
        el.classList.add(`${theme}-mode`);
    });
    
    // Update chart themes if Chart.js is available
    if (typeof Chart !== 'undefined' && typeof updateChartsForTheme === 'function') {
        updateChartsForTheme(theme);
    }
}

/**
 * Update the theme button icon based on the current theme
 * @param {string} theme - The current theme
 */
function updateThemeButtonIcon(theme) {
    // Get button container and clear current content
    const themeBtn = document.getElementById('theme-btn');
    if (!themeBtn) return;

    // Replace entire button content based on theme
    if (theme === 'dark') {
        themeBtn.innerHTML = '<i id="theme-icon" class="bi bi-moon-stars-fill"></i>';
    }
    else if (theme === 'dracula') {
        themeBtn.innerHTML = '<img id="theme-icon" src="/static/img/icons/dracula-icon.svg" style="width:38px;height:38px;margin-top:-10px;margin-bottom:-10px;margin-left:-8px;margin-right:-8px;" />';
    }
    else {
        themeBtn.innerHTML = '<i id="theme-icon" class="bi bi-sun-fill"></i>';
    }

    console.log('Updated theme icon for theme:', theme);
}

/**
 * Cycle through themes: Light -> Dark -> Dracula -> Light
 */
function cycleTheme(event) {
    if (event) event.preventDefault();
    
    console.log('Cycling theme...');
    
    // Get current theme
    const currentTheme = localStorage.getItem('theme') || 'light';
    console.log('Current theme before cycling:', currentTheme);
    
    // Determine the next theme in the cycle
    let newTheme;
    if (currentTheme === 'light') {
        newTheme = 'dark';
    } else if (currentTheme === 'dark') {
        newTheme = 'dracula';
    } else {
        newTheme = 'light';
    }
    
    console.log('Switching to new theme:', newTheme);
    
    // Apply the new theme
    applyTheme(newTheme);
    
    // Force save to localStorage
    localStorage.setItem('theme', newTheme);
    
    // Update the theme button icon
    updateThemeButtonIcon(newTheme);
    
    // Show a brief debug message
    showThemeChangeMessage(newTheme);
    
    console.log('Theme cycled to:', newTheme);
    
    return false; // Prevent default action
}

/**
 * Show a brief notification when the theme changes
 * @param {string} theme - The new theme
 */
function showThemeChangeMessage(theme) {
    // Create a floating notification element
    const notification = document.createElement('div');
    notification.style.position = 'fixed';
    notification.style.bottom = '20px';
    notification.style.right = '20px';
    notification.style.padding = '10px 20px';
    notification.style.backgroundColor = 'rgba(0, 0, 0, 0.8)';
    notification.style.color = 'white';
    notification.style.borderRadius = '5px';
    notification.style.zIndex = '9999';
    notification.style.fontWeight = 'bold';
    notification.style.boxShadow = '0 4px 8px rgba(0, 0, 0, 0.3)';
    notification.textContent = `Theme: ${theme.charAt(0).toUpperCase() + theme.slice(1)}`;
    
    // Add the notification to the document
    document.body.appendChild(notification);
    
    // Remove the notification after 2 seconds
    setTimeout(() => {
        notification.style.opacity = '0';
        notification.style.transition = 'opacity 0.5s ease-out';
        
        setTimeout(() => {
            document.body.removeChild(notification);
        }, 500);
    }, 2000);
}

// Function for backward compatibility with existing HTML onclick attributes
function toggleTheme(event) {
    // Forward to the new cycling function
    if (event) event.preventDefault();
    cycleTheme();
    return false;
}