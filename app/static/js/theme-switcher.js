/**
 * Theme Switcher for Equipment Tracker
 * Provides functionality to cycle between Light, Dark, and Dracula themes
 */

// This script is loaded in the <head> so it runs before page rendering
// Apply theme immediately to prevent flashing
(function() {
    // Apply theme based on localStorage immediately
    const savedTheme = localStorage.getItem('theme') || 'light';

    // Apply theme classes directly to <html> for immediate effect
    if (savedTheme === 'dark') {
        document.documentElement.classList.add('dark-mode');
    }
    else if (savedTheme === 'dracula') {
        document.documentElement.classList.add('dracula-mode');
    }

    // Then call the full function with proper body handling
    applyTheme(savedTheme);

    // Also run after DOM is fully loaded to update buttons and ensure everything is applied
    document.addEventListener('DOMContentLoaded', function() {
        // Re-apply theme to make sure it sticks
        applyTheme(savedTheme);
        updateThemeButton(savedTheme);
    });
})();

// Apply a specific theme
function applyTheme(theme) {
    // Reset all themes first from both html and body elements
    document.documentElement.classList.remove('dark-mode', 'dracula-mode');
    document.body.classList.remove('dark-mode', 'dracula-mode');

    // Apply theme-specific classes and styles
    if (theme === 'dark') {
        document.documentElement.classList.add('dark-mode');
        document.body.classList.add('dark-mode');
    }
    else if (theme === 'dracula') {
        document.documentElement.classList.add('dracula-mode');
        document.body.classList.add('dracula-mode');
    }

    // Store the theme preference to ensure it's saved
    localStorage.setItem('theme', theme);

    // Apply to any extra elements that might need the theme class
    if (theme !== 'light') {
        // Apply theme class to tables
        document.querySelectorAll('table').forEach(table => {
            table.classList.remove('dark-mode', 'dracula-mode');
            table.classList.add(`${theme}-mode`);
        });

        // Apply theme class to cards
        document.querySelectorAll('.card').forEach(card => {
            card.classList.remove('dark-mode', 'dracula-mode');
            card.classList.add(`${theme}-mode`);
        });
    }
}

// Update the theme toggle button based on current theme
function updateThemeButton(theme) {
    const themeBtn = document.getElementById('theme-btn');
    if (!themeBtn) return;

    if (theme === 'dark') {
        themeBtn.innerHTML = '<i class="bi bi-sun-fill"></i>';
    }
    else if (theme === 'dracula') {
        themeBtn.innerHTML = '<i class="bi bi-emoji-sunglasses-fill"></i>';
    }
    else {
        themeBtn.innerHTML = '<i class="bi bi-moon-stars-fill"></i>';
    }
}

// Function to cycle through themes: Light -> Dark -> Dracula -> Light
function cycleTheme(event) {
    if (event) event.preventDefault();

    // Get current theme from localStorage or default to light
    const currentTheme = localStorage.getItem('theme') || 'light';
    let newTheme;

    // Show debug notification
    const debugInfo = document.createElement('div');
    debugInfo.style.position = 'fixed';
    debugInfo.style.bottom = '10px';
    debugInfo.style.right = '10px';
    debugInfo.style.padding = '10px';
    debugInfo.style.backgroundColor = 'rgba(0,0,0,0.8)';
    debugInfo.style.color = 'white';
    debugInfo.style.zIndex = '9999';
    debugInfo.style.fontSize = '12px';
    debugInfo.style.borderRadius = '4px';

    // Determine the next theme in the cycle
    if (currentTheme === 'light') {
        newTheme = 'dark';
        debugInfo.textContent = "Switching to Dark mode";
    } else if (currentTheme === 'dark') {
        newTheme = 'dracula';
        debugInfo.textContent = "Switching to Dracula mode";
    } else {
        newTheme = 'light';
        debugInfo.textContent = "Switching to Light mode";
    }

    // Apply the new theme
    applyTheme(newTheme);

    // Force save theme to localStorage to ensure it persists across pages
    localStorage.setItem('theme', newTheme);

    // Log theme change to console to help with debugging
    console.log(`Theme changed to: ${newTheme} (saved to localStorage)`);

    // Update theme button
    updateThemeButton(newTheme);

    // Show debug message
    document.body.appendChild(debugInfo);

    // Remove debug info after 2 seconds
    setTimeout(() => {
        if (debugInfo.parentNode) {
            debugInfo.parentNode.removeChild(debugInfo);
        }
    }, 2000);

    return true;  // Allow default event behavior
}