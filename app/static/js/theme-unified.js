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
 * @param {string} theme - The theme to apply ('light', 'dark', 'dracula', 'sweet-dracula', or 'pastel')
 */
function applyTheme(theme) {
    console.log('Applying theme:', theme);

    // First ensure we have a valid theme
    if (!theme || !['light', 'dark', 'dracula', 'sweet-dracula', 'pastel'].includes(theme)) {
        console.warn('Invalid theme specified:', theme, 'defaulting to light');
        theme = 'light';
    }

    // Reset all themes first - important for a clean state
    document.documentElement.classList.remove('dark-mode', 'dracula-mode', 'sweet-dracula-mode', 'pastel-mode');
    document.body.classList.remove('dark-mode', 'dracula-mode', 'sweet-dracula-mode', 'pastel-mode');

    // Apply the specified theme
    if (theme === 'dark') {
        document.documentElement.classList.add('dark-mode');
        document.body.classList.add('dark-mode');
    }
    else if (theme === 'dracula') {
        document.documentElement.classList.add('dracula-mode');
        document.body.classList.add('dracula-mode');
    }
    else if (theme === 'sweet-dracula') {
        document.documentElement.classList.add('sweet-dracula-mode');
        document.body.classList.add('sweet-dracula-mode');
    }
    else if (theme === 'pastel') {
        document.documentElement.classList.add('pastel-mode');
        document.body.classList.add('pastel-mode');
    }

    // Always save the theme preference to localStorage - crucial for persistence
    localStorage.setItem('theme', theme);

    // Log what we're saving to localStorage
    console.log('Saving theme to localStorage:', theme);

    // Toggle logo visibility based on theme
    toggleLogosForTheme(theme);

    // Apply theme to additional elements
    applyThemeToElements(theme);

    // Apply theme to any open modals
    applyThemeToModals(theme);

    // Update the button icon to match the current theme
    updateThemeButtonIcon(theme);

    console.log('Theme fully applied:', theme);
}

/**
 * Apply custom styling to logos based on theme
 * @param {string} theme - The current theme
 */
function toggleLogosForTheme(theme) {
    // Find all logo containers
    const logoContainers = document.querySelectorAll('.navbar-logo-container, .footer-logo-container');

    logoContainers.forEach(container => {
        // Get the logo image
        const logoImg = container.querySelector('img');
        if (!logoImg) return;

        // Apply simplified theme-specific styling - minimal effects to avoid visual issues
        if (theme === 'dracula' || theme === 'sweet-dracula') {
            // For Dracula themes, very subtle treatment without glow or filtering
            logoImg.style.cssText = `
                opacity: 0.9 !important;
                transition: all 0.3s ease !important;
                filter: none !important;
            `;

            // Clean styling without backgrounds or shadows
            container.style.cssText = `
                background-color: transparent !important;
                box-shadow: none !important;
                padding: 2px !important;
                border-radius: 4px !important;
                transition: all 0.3s ease !important;
            `;
        } else if (theme === 'dark') {
            // For dark theme, subtle background without glow
            logoImg.style.cssText = `
                opacity: 0.95 !important;
                transition: all 0.3s ease !important;
                filter: none !important;
            `;

            // Light background for contrast
            container.style.cssText = `
                background-color: rgba(255, 255, 255, 0.1) !important;
                border-radius: 4px !important;
                padding: 2px !important;
                transition: all 0.3s ease !important;
                box-shadow: none !important;
            `;
        } else {
            // For light theme, clean styling
            logoImg.style.cssText = `
                filter: none !important;
                opacity: 1 !important;
                transition: all 0.3s ease !important;
            `;
            container.style.cssText = `
                background-color: transparent !important;
                padding: 2px !important;
                border-radius: 4px !important;
                transition: all 0.3s ease !important;
                box-shadow: none !important;
            `;
        }
    });
}

/**
 * Apply theme-specific classes to additional elements
 * @param {string} theme - The current theme
 */
function applyThemeToElements(theme) {
    if (theme === 'light') {
        // Remove theme classes from all elements
        document.querySelectorAll('table, .card, .footer, footer').forEach(el => {
            el.classList.remove('dark-mode', 'dracula-mode', 'sweet-dracula-mode', 'pastel-mode');
        });
        return;
    }

    // Apply theme class to tables, cards, etc.
    document.querySelectorAll('table, .card, .footer, footer').forEach(el => {
        el.classList.remove('dark-mode', 'dracula-mode', 'sweet-dracula-mode', 'pastel-mode');
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

    // Replace entire button content based on theme - now with standardized styling
    if (theme === 'dark') {
        themeBtn.innerHTML = '<i id="theme-icon" class="bi bi-moon-stars-fill"></i>';
    }
    else if (theme === 'dracula') {
        themeBtn.innerHTML = '<img id="theme-icon" src="/static/img/icons/dracula-icon.svg" alt="Dracula Theme" class="theme-icon-image" />';
    }
    else if (theme === 'sweet-dracula') {
        themeBtn.innerHTML = '<img id="theme-icon" src="/static/img/icons/sweet-dracula-icon.svg" alt="Sweet Dracula Theme" class="theme-icon-image" />';
    }
    else if (theme === 'pastel') {
        themeBtn.innerHTML = '<i id="theme-icon" class="bi bi-palette-fill"></i>';
    }
    else {
        themeBtn.innerHTML = '<i id="theme-icon" class="bi bi-sun-fill"></i>';
    }

    // Apply animation class for visual feedback
    themeBtn.classList.add('animate');
    setTimeout(() => {
        themeBtn.classList.remove('animate');
    }, 300);

    console.log('Updated theme icon for theme:', theme);
}

/**
 * Cycle through themes: Light -> Dark -> Dracula -> Sweet Dracula -> Pastel -> Light
 */
function cycleTheme(event) {
    if (event) event.preventDefault();

    console.log('Cycling theme...');

    // Get current theme
    const currentTheme = localStorage.getItem('theme') || 'light';
    console.log('Current theme before cycling:', currentTheme);

    // Determine the next theme in the cycle
    // Note: We're skipping pastel theme as it causes layout issues
    let newTheme;
    if (currentTheme === 'light') {
        newTheme = 'dark';
    } else if (currentTheme === 'dark') {
        newTheme = 'dracula';
    } else if (currentTheme === 'dracula') {
        newTheme = 'sweet-dracula';
    } else if (currentTheme === 'sweet-dracula') {
        newTheme = 'light'; // Skip pastel and go back to light
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
    notification.className = 'theme-change-notification';
    notification.style.position = 'fixed';
    notification.style.top = '60px';
    notification.style.left = '50%';
    notification.style.transform = 'translateX(-50%)';
    notification.style.padding = '8px 16px';
    notification.style.backgroundColor = 'rgba(0, 0, 0, 0.8)';
    notification.style.color = 'white';
    notification.style.borderRadius = '4px';
    notification.style.zIndex = '9999';
    notification.style.fontWeight = 'bold';
    notification.style.fontSize = '14px';
    notification.style.boxShadow = '0 2px 6px rgba(0, 0, 0, 0.3)';
    notification.style.opacity = '0';
    notification.style.transition = 'opacity 0.3s ease';

    // Adjust notification colors based on theme
    if (theme === 'light') {
        notification.style.backgroundColor = 'rgba(0, 0, 0, 0.8)';
        notification.style.color = 'white';
    } else if (theme === 'dark') {
        notification.style.backgroundColor = 'rgba(30, 30, 30, 0.9)';
        notification.style.boxShadow = '0 2px 8px rgba(0, 0, 0, 0.5)';
    } else if (theme === 'dracula') {
        notification.style.backgroundColor = 'rgba(40, 42, 54, 0.9)';
        notification.style.color = '#f8f8f2';
        notification.style.boxShadow = '0 2px 8px rgba(255, 121, 198, 0.3)';
    } else if (theme === 'sweet-dracula') {
        notification.style.backgroundColor = 'rgba(33, 34, 44, 0.9)';
        notification.style.color = '#f8f8f2';
        notification.style.boxShadow = '0 2px 8px rgba(189, 147, 249, 0.3)';
    }

    // Create icon based on theme
    let icon = '';
    if (theme === 'light') {
        icon = '<i class="bi bi-sun-fill me-2"></i>';
    } else if (theme === 'dark') {
        icon = '<i class="bi bi-moon-stars-fill me-2"></i>';
    } else if (theme === 'dracula') {
        icon = '<img src="/static/img/icons/dracula-icon.svg" class="me-2" style="width:16px;height:16px;" alt="Dracula" />';
    } else if (theme === 'sweet-dracula') {
        icon = '<img src="/static/img/icons/sweet-dracula-icon.svg" class="me-2" style="width:16px;height:16px;" alt="Sweet Dracula" />';
    } else {
        icon = '<i class="bi bi-palette-fill me-2"></i>';
    }

    notification.innerHTML = `${icon}Theme: ${theme.charAt(0).toUpperCase() + theme.slice(1)}`;

    // Add the notification to the document
    document.body.appendChild(notification);

    // Also apply theme to any open modals
    applyThemeToModals(theme);

    // Show notification with a slight delay
    setTimeout(() => {
        notification.style.opacity = '1';

        // Add animation to the theme button for visual feedback
        const themeBtn = document.getElementById('theme-btn');
        if (themeBtn) {
            themeBtn.classList.add('animate');
            setTimeout(() => {
                themeBtn.classList.remove('animate');
            }, 300);
        }

        // Remove the notification after 1.5 seconds
        setTimeout(() => {
            notification.style.opacity = '0';

            setTimeout(() => {
                if (notification.parentNode) {
                    document.body.removeChild(notification);
                }
            }, 300);
        }, 1500);
    }, 10);
}

/**
 * Apply theme to any open modals
 * @param {string} theme - The theme to apply
 */
function applyThemeToModals(theme) {
    // Find all open modals
    const modals = document.querySelectorAll('.modal, .modal-backdrop');
    if (modals.length === 0) return;

    // Remove all theme classes
    modals.forEach(modal => {
        modal.classList.remove('dark-mode', 'dracula-mode', 'sweet-dracula-mode', 'pastel-mode');

        // Add the appropriate theme class
        if (theme !== 'light') {
            modal.classList.add(`${theme}-mode`);
        }
    });

    console.log(`Applied ${theme} theme to ${modals.length} modal elements`);
}

// Function for backward compatibility with existing HTML onclick attributes
function toggleTheme(event) {
    // Forward to the new cycling function
    if (event) event.preventDefault();
    cycleTheme();
    return false;
}