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
    settingsBtn.id = 'layout-settings-btn';  // Add ID for easier finding
    settingsBtn.innerHTML = '<i class="bi bi-grid-3x3-gap-fill"></i>';
    settingsBtn.setAttribute('title', 'Layout Size: Click to toggle');
    settingsBtn.setAttribute('type', 'button'); // Explicit button type

    // Simple direct toggle through sizes instead of modal
    settingsBtn.onclick = function(e) {
        e.preventDefault();
        e.stopPropagation();

        console.log('Layout size toggle clicked');

        // Get current width and determine next width
        const currentWidth = document.body.getAttribute('data-layout-width') || 'standard';
        let nextWidth;

        switch(currentWidth) {
            case 'small':
                nextWidth = 'standard';
                break;
            case 'standard':
                nextWidth = 'wide';
                break;
            case 'wide':
                nextWidth = 'full';
                break;
            case 'full':
                nextWidth = 'small';
                break;
            default:
                nextWidth = 'standard';
        }

        // Update width
        console.log(`Toggling layout width from ${currentWidth} to ${nextWidth}`);
        updateLayoutWidth(nextWidth);

        // Flash the button to indicate change
        this.classList.add('active');
        setTimeout(() => {
            this.classList.remove('active');
        }, 300);

        // Update tooltip to show current setting
        this.setAttribute('title', `Layout Size: ${nextWidth} (click to toggle)`);

        // Save settings
        saveLayoutSettings();

        // Apply immediately
        applyLayoutSettings({
            width: nextWidth,
            fontSize: document.body.getAttribute('data-font-size') || 'normal',
            mobileMode: document.body.classList.contains('force-mobile-optimization')
        });

        return false;
    };

    // Insert before theme button
    themeBtn.parentNode.insertBefore(settingsBtn, themeBtn);

    // Log success message
    console.log('Layout settings button added successfully');
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
    console.log('Setting up layout controls...');

    // Get current settings
    const settings = loadLayoutSettings();
    console.log('Loaded settings:', settings);

    // Update buttons to reflect current settings
    updateLayoutControlButtons(settings);

    // Enhanced button handler setup with improved reliability
    function setupButtons() {
        // Debug current settings state before binding
        console.log('Setting up buttons with current settings:', {
            width: document.body.getAttribute('data-layout-width'),
            fontSize: document.body.getAttribute('data-font-size'),
            mobileMode: document.body.classList.contains('force-mobile-optimization')
        });

        // Width buttons - critical layout control
        const widthButtons = document.querySelectorAll('.layout-width-group button');
        console.log('Found width buttons:', widthButtons.length);

        if (widthButtons.length > 0) {
            // Clear any existing handlers
            widthButtons.forEach(button => {
                // Clone and replace to remove existing handlers
                const newButton = button.cloneNode(true);
                button.parentNode.replaceChild(newButton, button);
            });

            // Re-query the fresh buttons
            const freshWidthButtons = document.querySelectorAll('.layout-width-group button');

            // Add new handlers
            freshWidthButtons.forEach(button => {
                // Use both addEventListener and onclick for maximum compatibility
                const widthValue = button.getAttribute('data-width');
                console.log('Setting up handler for width button:', widthValue);

                button.onclick = function(e) {
                    e.preventDefault();
                    e.stopPropagation();
                    console.log('Width button clicked (onclick):', widthValue);

                    // Apply the width change
                    updateLayoutWidth(widthValue);

                    // Update active state
                    freshWidthButtons.forEach(btn => btn.classList.remove('active'));
                    this.classList.add('active');

                    // Save settings
                    if (document.getElementById('rememberLayoutSettings').checked) {
                        saveLayoutSettings();
                    }

                    // Apply immediately
                    applyLayoutSettings({
                        width: widthValue,
                        fontSize: document.body.getAttribute('data-font-size') || 'normal',
                        mobileMode: document.body.classList.contains('force-mobile-optimization')
                    });

                    return false;
                };

                // Add click listener as backup
                button.addEventListener('click', function(e) {
                    console.log('Width button clicked (addEventListener):', widthValue);
                    // The onclick handler above should take precedence
                });

                // Mark active based on current settings
                if (widthValue === (document.body.getAttribute('data-layout-width') || 'standard')) {
                    button.classList.add('active');
                }
            });
        }

        // Font size buttons
        const fontSizeButtons = document.querySelectorAll('.font-size-group button');
        console.log('Found font size buttons:', fontSizeButtons.length);

        if (fontSizeButtons.length > 0) {
            // Clear any existing handlers
            fontSizeButtons.forEach(button => {
                // Clone and replace to remove existing handlers
                const newButton = button.cloneNode(true);
                button.parentNode.replaceChild(newButton, button);
            });

            // Re-query the fresh buttons
            const freshFontButtons = document.querySelectorAll('.font-size-group button');

            // Add new handlers
            freshFontButtons.forEach(button => {
                // Use both addEventListener and onclick for maximum compatibility
                const fontSizeValue = button.getAttribute('data-font-size');
                console.log('Setting up handler for font size button:', fontSizeValue);

                button.onclick = function(e) {
                    e.preventDefault();
                    e.stopPropagation();
                    console.log('Font size button clicked (onclick):', fontSizeValue);

                    // Apply the font size change
                    updateFontSize(fontSizeValue);

                    // Update active state
                    freshFontButtons.forEach(btn => btn.classList.remove('active'));
                    this.classList.add('active');

                    // Save settings
                    if (document.getElementById('rememberLayoutSettings').checked) {
                        saveLayoutSettings();
                    }

                    // Apply immediately
                    applyLayoutSettings({
                        width: document.body.getAttribute('data-layout-width') || 'standard',
                        fontSize: fontSizeValue,
                        mobileMode: document.body.classList.contains('force-mobile-optimization')
                    });

                    return false;
                };

                // Add click listener as backup
                button.addEventListener('click', function(e) {
                    console.log('Font size button clicked (addEventListener):', fontSizeValue);
                    // The onclick handler above should take precedence
                });

                // Mark active based on current settings
                if (fontSizeValue === (document.body.getAttribute('data-font-size') || 'normal')) {
                    button.classList.add('active');
                }
            });
        }
    }

    // Run setup with delay
    setTimeout(setupButtons, 300);
}
    
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

// Update layout width with centering support - enhanced reliability
function updateLayoutWidth(width) {
    console.log('Updating layout width to:', width);

    // Validate width parameter
    if (!LAYOUT_CLASSES.width[width]) {
        console.error('Invalid width:', width);
        width = 'standard'; // Fallback to standard
    }

    // Get the target class
    const targetClass = LAYOUT_CLASSES.width[width];
    console.log('Target width class:', targetClass);

    // Debug before update
    console.log('Current body classes before width update:', document.body.className);

    // Remove all width classes with error checking
    Object.values(LAYOUT_CLASSES.width).forEach(cls => {
        if (document.body.classList.contains(cls)) {
            console.log('Removing class:', cls);
            document.body.classList.remove(cls);
        }
    });

    // Add the selected width class
    console.log('Adding class:', targetClass);
    document.body.classList.add(targetClass);

    // Update data attribute
    document.body.setAttribute('data-layout-width', width);

    // Debug after update
    console.log('Current body classes after width update:', document.body.className);

    // Apply centering to fix black bar
    fixBlackBarIssue();
    fixContentCentering();

    // Update any active buttons
    const widthButtons = document.querySelectorAll('.layout-width-group button');
    widthButtons.forEach(button => {
        if (button.getAttribute('data-width') === width) {
            button.classList.add('active');
        } else {
            button.classList.remove('active');
        }
    });

    // Update layout settings button tooltip if it exists
    const layoutBtn = document.getElementById('layout-settings-btn');
    if (layoutBtn) {
        layoutBtn.setAttribute('title', `Layout Size: ${width} (click to toggle)`);
    }

    // Dispatch a custom event for the width change
    document.dispatchEvent(new CustomEvent('layout-width-changed', {
        detail: { width: width, class: targetClass }
    }));
}

// Update font size - enhanced reliability
function updateFontSize(fontSize) {
    console.log('Updating font size to:', fontSize);

    // Validate font size parameter
    if (!LAYOUT_CLASSES.fontSize[fontSize]) {
        console.error('Invalid font size:', fontSize);
        fontSize = 'normal'; // Fallback to normal
    }

    // Get the target class
    const targetClass = LAYOUT_CLASSES.fontSize[fontSize];
    console.log('Target font size class:', targetClass);

    // Debug before update
    console.log('Current body classes before font size update:', document.body.className);

    // Remove all font size classes with error checking
    Object.values(LAYOUT_CLASSES.fontSize).forEach(cls => {
        if (document.body.classList.contains(cls)) {
            console.log('Removing class:', cls);
            document.body.classList.remove(cls);
        }
    });

    // Add the selected font size class
    console.log('Adding class:', targetClass);
    document.body.classList.add(targetClass);

    // Update data attribute
    document.body.setAttribute('data-font-size', fontSize);

    // Debug after update
    console.log('Current body classes after font size update:', document.body.className);

    // Update any active buttons
    const fontSizeButtons = document.querySelectorAll('.font-size-group button');
    fontSizeButtons.forEach(button => {
        if (button.getAttribute('data-font-size') === fontSize) {
            button.classList.add('active');
        } else {
            button.classList.remove('active');
        }
    });
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
    console.log('Applying layout settings:', settings);

    // Make sure we have valid settings
    const validSettings = {
        width: settings.width || 'standard',
        fontSize: settings.fontSize || 'normal',
        mobileMode: settings.mobileMode || false
    };

    // Apply width with proper class
    const widthClass = LAYOUT_CLASSES.width[validSettings.width];
    if (widthClass) {
        // Remove all width classes
        Object.values(LAYOUT_CLASSES.width).forEach(cls => {
            document.body.classList.remove(cls);
        });

        // Add the selected width class
        document.body.classList.add(widthClass);

        // Update data attribute for tracking
        document.body.setAttribute('data-layout-width', validSettings.width);

        console.log('Applied width class:', widthClass);
    } else {
        console.warn('Invalid width setting:', validSettings.width);
    }

    // Apply font size with proper class
    const fontSizeClass = LAYOUT_CLASSES.fontSize[validSettings.fontSize];
    if (fontSizeClass) {
        // Remove all font size classes
        Object.values(LAYOUT_CLASSES.fontSize).forEach(cls => {
            document.body.classList.remove(cls);
        });

        // Add the selected font size class
        document.body.classList.add(fontSizeClass);

        // Update data attribute for tracking
        document.body.setAttribute('data-font-size', validSettings.fontSize);

        console.log('Applied font size class:', fontSizeClass);
    } else {
        console.warn('Invalid font size setting:', validSettings.fontSize);
    }

    // Apply mobile mode
    if (validSettings.mobileMode) {
        document.body.classList.add('force-mobile-optimization');
    } else {
        document.body.classList.remove('force-mobile-optimization');
    }

    // Update the mobile toggle in the modal if it exists
    const mobileToggle = document.getElementById('mobileMode');
    if (mobileToggle) {
        mobileToggle.checked = validSettings.mobileMode;
    }

    // Fix any visual layout issues
    fixBlackBarIssue();
    fixContentCentering();

    // Debug output of applied settings
    console.log('Current body classes:', document.body.className);
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
    console.log('Initializing layout controls with persistent scale');

    // Load settings immediately - this ensures persistence across page navigation
    const settings = loadLayoutSettings();
    console.log('Retrieved saved layout settings:', settings);

    // Apply settings immediately to prevent flash of unstyled content
    applyLayoutSettings(settings);

    // Initialize with a short delay to ensure all elements are loaded
    setTimeout(() => {
        console.log('Continuing initialization after delay');
        initLayoutControls();
        fixActionButtons();

        // Re-apply settings to ensure everything is consistent
        applyLayoutSettings(settings);

        // Ensure any missed elements are updated
        setTimeout(() => {
            fixContentCentering();
            fixBlackBarIssue();

            // Double check that classes are applied
            Object.values(LAYOUT_CLASSES.width).forEach(cls => {
                if (document.body.classList.contains(cls)) {
                    console.log('Width class verified:', cls);
                }
            });
        }, 200);
    }, 50);

    // Add settings button to static elements for additional reliability
    const addLayoutControls = () => {
        // Add buttons if they don't exist yet
        if (!document.getElementById('layout-settings-btn')) {
            createLayoutSettingsButton();
        }

        if (!document.getElementById('mobile-mode-toggle')) {
            createMobileToggleButton();
        }
    };

    // Try adding buttons immediately and after a delay
    addLayoutControls();
    setTimeout(addLayoutControls, 1000);

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

    // Make the layout settings button more reliable
    document.addEventListener('click', function(e) {
        // Handle direct clicks on the settings button even if dynamically added later
        if (e.target && (
            e.target.id === 'layout-settings-btn' ||
            (e.target.parentNode && e.target.parentNode.id === 'layout-settings-btn')
        )) {
            console.log('Layout settings button clicked via delegate');

            // Ensure modal exists
            let modalElement = document.getElementById('layoutSettingsModal');
            if (!modalElement) {
                createLayoutSettingsModal();
                modalElement = document.getElementById('layoutSettingsModal');
            }

            if (modalElement && typeof bootstrap !== 'undefined') {
                const modal = new bootstrap.Modal(modalElement);
                modal.show();

                setTimeout(() => {
                    setupLayoutControls();
                }, 300);
            }
        }
    });
});