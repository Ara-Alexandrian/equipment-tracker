/**
 * Layout Controls Fixed - Improved version with mobile toggle and centering
 * Fixes the black bar issue and adds proper mobile toggling
 */

// Class names for different layout options
const LAYOUT_CLASSES = {
    width: {
        small: 'container-width-small',    // For smaller screens (~1200px)
        standard: 'container-width-standard', // For 1600x1200 screens (~1550px)
        wide: 'container-width-wide',      // For larger screens (~1800px)
        full: 'container-width-full'       // For ultrawide screens (~2100px)
    },
    fontSize: {
        normal: 'table-font-normal',
        larger: 'table-font-larger',
        largest: 'table-font-largest'
    }
};

// Width descriptions for UI
const WIDTH_DESCRIPTIONS = {
    small: 'Small (Laptop, 1200px)',
    standard: 'Medium (1600×1200)',
    wide: 'Large (Wide, 1800px)',
    full: 'Extra Large (Ultrawide, 2100px)'
};

// Default settings - Optimized for 1600x1200 displays
const DEFAULT_SETTINGS = {
    width: 'standard',  // Set to standard (1550px width) for 1600x1200 displays
    fontSize: 'normal',
    mobileMode: false   // Mobile mode toggle (false by default)
};

// Local storage key
const STORAGE_KEY = 'gearVueLayoutSettings';

// Initialize layout controls
function initLayoutControls() {
    console.log('Initializing layout controls (fixed version)');

    // Load saved settings
    const settings = loadLayoutSettings();
    
    // Apply current settings
    applyLayoutSettings(settings);
    
    // Convert divs to use centered-content class for proper centering
    fixContentCentering();
    
    // Apply mobile optimizations
    applyMobileOptimizations();
    
    // Create layout settings button in navbar
    createLayoutSettingsButton();
    
    // Create mobile toggle button
    createMobileToggleButton();
    
    // Create settings modal
    createLayoutSettingsModal();
    
    // Fix black bar issue
    fixBlackBarIssue();
}

// Add mobile toggle button to navbar
function createMobileToggleButton() {
    // Find the navbar theme button
    const themeBtn = document.getElementById('theme-btn');
    if (!themeBtn) return;
    
    // Create mobile toggle button
    const mobileBtn = document.createElement('button');
    mobileBtn.className = 'mobile-mode-toggle';
    mobileBtn.id = 'mobile-mode-toggle';
    mobileBtn.innerHTML = '<i class="bi bi-phone"></i>';
    mobileBtn.setAttribute('title', 'Toggle Mobile Mode');
    
    // If mobile mode is active, add active class
    if (document.body.classList.contains('force-mobile-optimization')) {
        mobileBtn.classList.add('active');
    }
    
    // Add event listener to toggle mobile mode
    mobileBtn.addEventListener('click', function() {
        toggleMobileMode();
    });
    
    // Insert after theme button
    themeBtn.parentNode.insertBefore(mobileBtn, themeBtn.nextSibling);
}

// Toggle mobile mode
function toggleMobileMode() {
    const mobileBtn = document.getElementById('mobile-mode-toggle');
    const isMobileActive = document.body.classList.contains('force-mobile-optimization');
    
    if (isMobileActive) {
        // Turn off mobile mode
        document.body.classList.remove('force-mobile-optimization');
        if (mobileBtn) mobileBtn.classList.remove('active');
        
        // Update settings
        const settings = loadLayoutSettings();
        settings.mobileMode = false;
        saveLayoutSettings(settings);
        
        console.log('Mobile mode disabled');
    } else {
        // Turn on mobile mode
        document.body.classList.add('force-mobile-optimization');
        if (mobileBtn) mobileBtn.classList.add('active');
        
        // Update settings
        const settings = loadLayoutSettings();
        settings.mobileMode = true;
        saveLayoutSettings(settings);
        
        console.log('Mobile mode enabled');
    }
}

// Fix content centering
function fixContentCentering() {
    // Add centered-content class to all main containers
    const containers = document.querySelectorAll('.container-fluid');
    
    containers.forEach(container => {
        // Skip navbar and footer containers
        if (container.closest('nav') || container.closest('footer')) {
            return;
        }
        
        // Add centered-content class
        container.classList.add('centered-content');
    });
}

// Fix notorious black bar issue
function fixBlackBarIssue() {
    // Ensure body doesn't overflow
    document.body.style.overflowX = 'hidden';
    document.documentElement.style.overflowX = 'hidden';
    
    // Make sure main containers are properly limited
    document.querySelectorAll('.container, .container-fluid').forEach(container => {
        container.style.maxWidth = '100%';
    });
    
    // Fix the width of the HTML element to prevent overflow
    document.documentElement.style.width = '100%';
}

// Apply mobile-specific optimizations
function applyMobileOptimizations() {
    // Auto-detect mobile devices and apply force-mobile-optimization class
    detectMobileDevice();
    
    // Add short-text spans to any table headers that don't have them
    const tableHeaders = document.querySelectorAll('.equipment-table th, #equipmentTable th');
    tableHeaders.forEach(header => {
        // Skip if it already has short/full text spans
        if (header.querySelector('.short-text') || header.querySelector('.full-text')) {
            return;
        }

        // Get the current text
        const originalText = header.textContent.trim();

        // Create abbreviated version - first 3 chars or whole word if shorter
        let shortText = originalText;
        if (originalText.length > 3) {
            shortText = originalText.substring(0, 3);
        }

        // Clear original content and add spans
        header.innerHTML = `
            <span class="full-text">${originalText}</span>
            <span class="short-text d-none">${shortText}</span>
        `;
    });

    // Ensure all action buttons have proper button-text wrapping
    const actionButtons = document.querySelectorAll('.action-button');
    actionButtons.forEach(button => {
        // Skip if button already has proper structure
        if (button.querySelector('.button-text') || !button.textContent.trim()) {
            return;
        }

        // Find the icon
        const icon = button.querySelector('i');
        if (!icon) {
            return;
        }

        // Get text content excluding the icon
        const buttonText = button.textContent.trim();

        // Remove text nodes
        Array.from(button.childNodes)
            .filter(node => node.nodeType === Node.TEXT_NODE)
            .forEach(node => node.remove());

        // Add wrapped text
        const textSpan = document.createElement('span');
        textSpan.className = 'button-text';
        textSpan.textContent = buttonText;
        button.appendChild(textSpan);
    });

    // Find all table cells that contain action buttons (typically last column)
    const actionCells = document.querySelectorAll('.equipment-table td:last-child, #equipmentTable td:last-child');
    actionCells.forEach(cell => {
        // Skip if already wrapped
        if (cell.querySelector('.action-button-container')) {
            return;
        }
        
        // Check if it contains action buttons
        const buttons = cell.querySelectorAll('.action-button, .btn');
        if (buttons.length === 0) {
            return;
        }
        
        // Create container if cell contains at least one button
        const container = document.createElement('div');
        container.className = 'action-button-container';
        
        // Move all children to container
        while (cell.firstChild) {
            container.appendChild(cell.firstChild);
        }
        
        // Add container to cell
        cell.appendChild(container);
    });
}

// Create layout settings button in navbar
function createLayoutSettingsButton() {
    // Find the navbar theme button
    const themeBtn = document.getElementById('theme-btn');
    if (!themeBtn) return;
    
    // Create settings button
    const settingsBtn = document.createElement('button');
    settingsBtn.className = 'layout-settings-btn';
    settingsBtn.innerHTML = '<i class="bi bi-grid-3x3-gap-fill"></i>';
    settingsBtn.setAttribute('title', 'Table Layout Settings');
    settingsBtn.setAttribute('data-bs-toggle', 'modal');
    settingsBtn.setAttribute('data-bs-target', '#layoutSettingsModal');
    
    // Insert after theme button
    themeBtn.parentNode.insertBefore(settingsBtn, themeBtn.nextSibling);
}

// Create layout settings modal
function createLayoutSettingsModal() {
    // Create modal HTML with enhanced options for different resolutions and mobile toggle
    const modalHTML = `
        <div class="modal fade layout-settings-modal" id="layoutSettingsModal" tabindex="-1" aria-labelledby="layoutSettingsModalLabel" aria-hidden="true">
            <div class="modal-dialog">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title" id="layoutSettingsModalLabel">Display Settings</h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                    </div>
                    <div class="modal-body">
                        <div class="control-section">
                            <h6>Screen Resolution Optimization</h6>
                            <div class="btn-group layout-width-group d-flex flex-wrap" role="group">
                                <button type="button" class="btn btn-outline-primary" data-width="small" title="${WIDTH_DESCRIPTIONS.small}">
                                    <i class="bi bi-laptop"></i> Small
                                </button>
                                <button type="button" class="btn btn-outline-primary" data-width="standard" title="${WIDTH_DESCRIPTIONS.standard}">
                                    <i class="bi bi-display"></i> Medium
                                </button>
                                <button type="button" class="btn btn-outline-primary" data-width="wide" title="${WIDTH_DESCRIPTIONS.wide}">
                                    <i class="bi bi-display-fill"></i> Large
                                </button>
                                <button type="button" class="btn btn-outline-primary" data-width="full" title="${WIDTH_DESCRIPTIONS.full}">
                                    <i class="bi bi-pc-display-horizontal"></i> XL
                                </button>
                            </div>
                            <small class="text-muted mt-1 d-block">Optimizes layout for different screen sizes</small>
                        </div>
                        
                        <div class="control-section mt-4">
                            <h6>Mobile Mode</h6>
                            <div class="form-check form-switch">
                                <input class="form-check-input" type="checkbox" id="mobileMode">
                                <label class="form-check-label" for="mobileMode">
                                    Enable Mobile Optimization
                                </label>
                            </div>
                            <small class="text-muted mt-1 d-block">Shows compact headers and icon-only buttons</small>
                        </div>
                        
                        <div class="control-section mt-4">
                            <h6>Table Font Size</h6>
                            <div class="btn-group font-size-group" role="group">
                                <button type="button" class="btn btn-outline-primary" data-font-size="normal">
                                    <i class="bi bi-type"></i> Normal
                                </button>
                                <button type="button" class="btn btn-outline-primary" data-font-size="larger">
                                    <i class="bi bi-type-bold"></i> Larger
                                </button>
                                <button type="button" class="btn btn-outline-primary" data-font-size="largest">
                                    <i class="bi bi-type-h1"></i> Largest
                                </button>
                            </div>
                        </div>
                        
                        <div class="form-check mt-4">
                            <input class="form-check-input" type="checkbox" id="rememberLayoutSettings" checked>
                            <label class="form-check-label" for="rememberLayoutSettings">
                                Remember settings across sessions
                            </label>
                        </div>
                        
                        <div class="alert alert-info mt-4 small">
                            <i class="bi bi-info-circle-fill me-1"></i>
                            These settings control the layout width and table formatting. The Medium setting (1600×1200) is optimized for most displays.
                        </div>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
                        <button type="button" class="btn btn-primary" id="resetLayoutSettings">Reset to Defaults</button>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    // Add modal to the page
    const modalContainer = document.createElement('div');
    modalContainer.innerHTML = modalHTML;
    document.body.appendChild(modalContainer.firstElementChild);
    
    // Setup event handlers
    setupLayoutControls();
}

// Set up layout control event handlers
function setupLayoutControls() {
    // Get current settings
    const settings = loadLayoutSettings();
    
    // Update buttons to reflect current settings
    updateLayoutControlButtons(settings);
    
    // Add event listeners to width buttons
    const widthButtons = document.querySelectorAll('.layout-width-group button');
    widthButtons.forEach(button => {
        button.addEventListener('click', function() {
            const width = this.getAttribute('data-width');
            updateLayoutWidth(width);
            
            // Update selected button
            widthButtons.forEach(btn => btn.classList.remove('active'));
            this.classList.add('active');
            
            // Save settings if remember is checked
            if (document.getElementById('rememberLayoutSettings').checked) {
                saveLayoutSettings();
            }
        });
    });
    
    // Add event listeners to font size buttons
    const fontSizeButtons = document.querySelectorAll('.font-size-group button');
    fontSizeButtons.forEach(button => {
        button.addEventListener('click', function() {
            const fontSize = this.getAttribute('data-font-size');
            updateFontSize(fontSize);
            
            // Update selected button
            fontSizeButtons.forEach(btn => btn.classList.remove('active'));
            this.classList.add('active');
            
            // Save settings if remember is checked
            if (document.getElementById('rememberLayoutSettings').checked) {
                saveLayoutSettings();
            }
        });
    });
    
    // Add event listener to mobile mode toggle
    const mobileModeToggle = document.getElementById('mobileMode');
    if (mobileModeToggle) {
        // Set initial state
        mobileModeToggle.checked = document.body.classList.contains('force-mobile-optimization');
        
        mobileModeToggle.addEventListener('change', function() {
            if (this.checked) {
                document.body.classList.add('force-mobile-optimization');
                
                // Update mobile button
                const mobileBtn = document.getElementById('mobile-mode-toggle');
                if (mobileBtn) mobileBtn.classList.add('active');
            } else {
                document.body.classList.remove('force-mobile-optimization');
                
                // Update mobile button
                const mobileBtn = document.getElementById('mobile-mode-toggle');
                if (mobileBtn) mobileBtn.classList.remove('active');
            }
            
            // Save settings if remember is checked
            if (document.getElementById('rememberLayoutSettings').checked) {
                const settings = {
                    width: document.body.getAttribute('data-layout-width') || DEFAULT_SETTINGS.width,
                    fontSize: document.body.getAttribute('data-font-size') || DEFAULT_SETTINGS.fontSize,
                    mobileMode: this.checked
                };
                
                localStorage.setItem(STORAGE_KEY, JSON.stringify(settings));
            }
        });
    }
    
    // Add event listener to reset button
    document.getElementById('resetLayoutSettings').addEventListener('click', function() {
        resetLayoutSettings();
    });
}

// Update layout width with centering support
function updateLayoutWidth(width) {
    // Remove all width classes
    Object.values(LAYOUT_CLASSES.width).forEach(cls => {
        document.body.classList.remove(cls);
    });
    
    // Add the selected width class
    document.body.classList.add(LAYOUT_CLASSES.width[width]);
    
    // Update data attribute
    document.body.setAttribute('data-layout-width', width);
    
    // Apply centering to fix black bar
    fixBlackBarIssue();
    fixContentCentering();
}

// Update font size
function updateFontSize(fontSize) {
    // Remove all font size classes
    Object.values(LAYOUT_CLASSES.fontSize).forEach(cls => {
        document.body.classList.remove(cls);
    });
    
    // Add the selected font size class
    document.body.classList.add(LAYOUT_CLASSES.fontSize[fontSize]);
    
    // Update data attribute
    document.body.setAttribute('data-font-size', fontSize);
}

// Reset layout settings to defaults
function resetLayoutSettings() {
    // Apply default settings
    updateLayoutWidth(DEFAULT_SETTINGS.width);
    updateFontSize(DEFAULT_SETTINGS.fontSize);
    
    // Reset mobile mode
    if (DEFAULT_SETTINGS.mobileMode) {
        document.body.classList.add('force-mobile-optimization');
    } else {
        document.body.classList.remove('force-mobile-optimization');
    }
    
    // Update mobile toggle in modal
    const mobileToggle = document.getElementById('mobileMode');
    if (mobileToggle) {
        mobileToggle.checked = DEFAULT_SETTINGS.mobileMode;
    }
    
    // Update mobile button
    const mobileBtn = document.getElementById('mobile-mode-toggle');
    if (mobileBtn) {
        if (DEFAULT_SETTINGS.mobileMode) {
            mobileBtn.classList.add('active');
        } else {
            mobileBtn.classList.remove('active');
        }
    }
    
    // Update buttons
    updateLayoutControlButtons(DEFAULT_SETTINGS);
    
    // Ensure containers are properly centered
    fixContentCentering();
    
    // Fix black bar issue
    fixBlackBarIssue();
    
    // Remove from local storage
    localStorage.removeItem(STORAGE_KEY);
}

// Load layout settings from local storage
function loadLayoutSettings() {
    try {
        const savedSettings = localStorage.getItem(STORAGE_KEY);
        if (savedSettings) {
            const parsed = JSON.parse(savedSettings);
            // Apply mobile mode from settings
            if (parsed.mobileMode) {
                document.body.classList.add('force-mobile-optimization');
                
                // Update mobile button
                const mobileBtn = document.getElementById('mobile-mode-toggle');
                if (mobileBtn) mobileBtn.classList.add('active');
            }
            return parsed;
        }
    } catch (error) {
        console.error('Error loading layout settings:', error);
    }
    
    return DEFAULT_SETTINGS;
}

// Save layout settings to local storage
function saveLayoutSettings(settings) {
    try {
        const settingsToSave = settings || {
            width: document.body.getAttribute('data-layout-width') || DEFAULT_SETTINGS.width,
            fontSize: document.body.getAttribute('data-font-size') || DEFAULT_SETTINGS.fontSize,
            mobileMode: document.body.classList.contains('force-mobile-optimization')
        };
        
        localStorage.setItem(STORAGE_KEY, JSON.stringify(settingsToSave));
    } catch (error) {
        console.error('Error saving layout settings:', error);
    }
}

// Apply layout settings
function applyLayoutSettings(settings) {
    // Apply width
    updateLayoutWidth(settings.width);
    
    // Apply font size
    updateFontSize(settings.fontSize);
    
    // Apply mobile mode
    if (settings.mobileMode) {
        document.body.classList.add('force-mobile-optimization');
    } else {
        document.body.classList.remove('force-mobile-optimization');
    }
}

// Update layout control buttons to reflect current settings
function updateLayoutControlButtons(settings) {
    // Update width buttons
    const widthButtons = document.querySelectorAll('.layout-width-group button');
    widthButtons.forEach(button => {
        if (button.getAttribute('data-width') === settings.width) {
            button.classList.add('active');
        } else {
            button.classList.remove('active');
        }
    });
    
    // Update font size buttons
    const fontSizeButtons = document.querySelectorAll('.font-size-group button');
    fontSizeButtons.forEach(button => {
        if (button.getAttribute('data-font-size') === settings.fontSize) {
            button.classList.add('active');
        } else {
            button.classList.remove('active');
        }
    });
    
    // Update mobile mode toggle
    const mobileToggle = document.getElementById('mobileMode');
    if (mobileToggle) {
        mobileToggle.checked = settings.mobileMode || false;
    }
}

// Fix action button text wrapping
function fixActionButtons() {
    // Apply action-button class to all action buttons
    const actionButtons = document.querySelectorAll('.table td:last-child .btn');
    actionButtons.forEach(button => {
        button.classList.add('action-button');
    });
    
    // Add action-col class to all action columns
    const actionCols = document.querySelectorAll('.table th:last-child, .table td:last-child');
    actionCols.forEach(col => {
        col.classList.add('action-col');
    });
}

// Auto-detect mobile and tablet devices
function detectMobileDevice() {
    // Check if device is mobile/tablet
    const isMobileOrTablet = 
        /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent) || 
        window.innerWidth <= 991;
        
    if (isMobileOrTablet) {
        // Add force-mobile-optimization class to body
        document.body.classList.add('force-mobile-optimization');
        console.log('Mobile device detected - applying mobile optimizations');
        
        // Update settings to remember mobile mode
        const settings = loadLayoutSettings();
        settings.mobileMode = true;
        saveLayoutSettings(settings);
    }
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    initLayoutControls();
    fixActionButtons();
    
    // Listen for resize events to detect rotation or window size changes
    window.addEventListener('resize', function() {
        // Fix black bar on resize
        fixBlackBarIssue();
        
        // Toggle mobile mode based on screen size
        if (window.innerWidth <= 991) {
            document.body.classList.add('force-mobile-optimization');
            
            // Update mobile button
            const mobileBtn = document.getElementById('mobile-mode-toggle');
            if (mobileBtn) mobileBtn.classList.add('active');
        } else {
            // Only remove if not manually enabled
            const settings = loadLayoutSettings();
            if (!settings.mobileMode) {
                document.body.classList.remove('force-mobile-optimization');
                
                // Update mobile button
                const mobileBtn = document.getElementById('mobile-mode-toggle');
                if (mobileBtn) mobileBtn.classList.remove('active');
            }
        }
    });
});