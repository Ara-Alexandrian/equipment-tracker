/**
 * Layout Controls for Equipment Tracker
 * Allows users to customize the table layout and font size
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
    fontSize: 'normal'
};

// Local storage key
const STORAGE_KEY = 'gearVueLayoutSettings';

// Initialize layout controls
function initLayoutControls() {
    console.log('Initializing layout controls');

    // Load saved settings
    const settings = loadLayoutSettings();

    // Apply current settings
    applyLayoutSettings(settings);

    // Force container centering
    updateContainerCentering();

    // Apply mobile optimizations
    applyMobileOptimizations();

    // Create layout settings button in navbar
    createLayoutSettingsButton();

    // Create settings modal
    createLayoutSettingsModal();
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
    // Create modal HTML with enhanced options for different resolutions
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

                        <div class="form-check mt-3">
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

    // Update any dynamic containers
    updateContainerCentering();
}

// Force container centering to update
function updateContainerCentering() {
    // Get all container fluid elements
    const containers = document.querySelectorAll('.container-fluid');

    // Ensure they all have mx-auto child divs for proper centering
    containers.forEach(container => {
        // Skip if already has mx-auto direct child
        if (container.querySelector(':scope > .mx-auto')) {
            return;
        }

        // If container has children but no mx-auto wrapper
        if (container.children.length > 0) {
            // Create wrapper
            const wrapper = document.createElement('div');
            wrapper.className = 'mx-auto';

            // Move all children to wrapper
            while (container.firstChild) {
                wrapper.appendChild(container.firstChild);
            }

            // Add wrapper to container
            container.appendChild(wrapper);
        }
    });
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

    // Update buttons
    updateLayoutControlButtons(DEFAULT_SETTINGS);

    // Update container centering
    updateContainerCentering();

    // Remove from local storage
    localStorage.removeItem(STORAGE_KEY);
}

// Load layout settings from local storage
function loadLayoutSettings() {
    try {
        const savedSettings = localStorage.getItem(STORAGE_KEY);
        if (savedSettings) {
            return JSON.parse(savedSettings);
        }
    } catch (error) {
        console.error('Error loading layout settings:', error);
    }
    
    return DEFAULT_SETTINGS;
}

// Save layout settings to local storage
function saveLayoutSettings() {
    try {
        const settings = {
            width: document.body.getAttribute('data-layout-width') || DEFAULT_SETTINGS.width,
            fontSize: document.body.getAttribute('data-font-size') || DEFAULT_SETTINGS.fontSize
        };
        
        localStorage.setItem(STORAGE_KEY, JSON.stringify(settings));
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
    }
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    initLayoutControls();
    fixActionButtons();

    // Listen for resize events to detect rotation or window size changes
    window.addEventListener('resize', function() {
        if (window.innerWidth <= 991) {
            document.body.classList.add('force-mobile-optimization');
        } else {
            document.body.classList.remove('force-mobile-optimization');
        }
    });
});