/**
 * Table Enhancements for GearVue
 * Improves table layout and responsiveness
 */

document.addEventListener('DOMContentLoaded', function() {
    // Fix table headers - ensure they wrap properly
    enhanceTableHeaders();
    
    // Format manufacturer names to allow wrapping
    formatManufacturerNames();

    // Make tables responsive on window resize
    window.addEventListener('resize', function() {
        adjustTableResponsiveness();
    });

    // Initial adjustment
    adjustTableResponsiveness();
    
    // Set a mutation observer to handle dynamically loaded tables
    observeTableChanges();
});

/**
 * Helper function to break long manufacturer names into multiple lines
 */
function formatManufacturerNames() {
    // Find all manufacturer cells
    const manufacturerCells = document.querySelectorAll('table td.manufacturer-cell');

    // If we don't find any specifically marked manufacturer cells, use a more general approach
    if (manufacturerCells.length === 0) {
        const allCells = document.querySelectorAll('table td');

        allCells.forEach(cell => {
            const text = cell.textContent.trim();

            // Check if it's likely a manufacturer name (avoid actions column)
            if (text.length > 10 && text.includes(' ') && !cell.querySelector('a, button, .btn')) {
                // If it's a potential manufacturer name (check surrounding cells)
                const prevCell = cell.previousElementSibling;
                const nextCell = cell.nextElementSibling;

                if ((prevCell && prevCell.textContent.trim().match(/^(id|type|category)$/i)) ||
                    (nextCell && nextCell.textContent.trim().match(/^(model|serial)$/i))) {
                    // Insert soft hyphens for better word breaking
                    const enhancedText = text.replace(/([a-z])([A-Z])/g, '$1&shy;$2');
                    cell.innerHTML = enhancedText;
                    cell.style.wordBreak = 'break-word';
                    cell.style.whiteSpace = 'normal';
                    cell.style.hyphens = 'auto';
                }
            }
        });
    } else {
        // Process specifically marked manufacturer cells
        manufacturerCells.forEach(cell => {
            const text = cell.textContent.trim();

            // Insert soft hyphens for better word breaking in longer manufacturer names
            if (text.length > 8) {
                const words = text.split(' ');
                let enhancedText = text;

                // If there are multiple words
                if (words.length >= 2) {
                    enhancedText = words.join(' ').replace(/([a-z])([A-Z])/g, '$1&shy;$2');
                }

                cell.innerHTML = enhancedText;
                cell.style.wordBreak = 'break-word';
                cell.style.whiteSpace = 'normal';
                cell.style.hyphens = 'auto';
                cell.style.lineHeight = '1.4';
            }
        });
    }
}

/**
 * Enhance table headers for better readability
 */
function enhanceTableHeaders() {
    // Get all table headers
    const tableHeaders = document.querySelectorAll('table th');

    // Process each header
    tableHeaders.forEach((header, index) => {
        // Get the header text
        const headerText = header.textContent.trim().toLowerCase();

        // Abbreviate "Manufacturer" to "MFR"
        if (headerText.includes('manufacturer')) {
            header.innerHTML = header.innerHTML.replace(/manufacturer/i, 'MFR');
            header.setAttribute('title', 'Manufacturer');
        }

        // Special case for Actions column (usually last column)
        if (headerText.includes('action') ||
            header.querySelector('.btn') ||
            header.parentElement.lastElementChild === header) {
            header.style.width = 'auto';
            header.style.minWidth = '130px';
            header.style.maxWidth = '140px';
            header.style.whiteSpace = 'nowrap';
            return;
        }

        // Apply widths based on content
        if (headerText.includes('manufacturer') || headerText.includes('model') || headerText.includes('mfr')) {
            header.style.width = '120px';
        }
        else if (headerText.includes('serial') || headerText.includes('category')) {
            header.style.width = '120px';
        }
        else if (headerText.includes('type') || headerText.includes('name')) {
            header.style.width = '110px';
        }
        else if (headerText.includes('status') || headerText.includes('location')) {
            header.style.width = '100px';
        }
        else if (headerText.includes('date') || headerText.includes('calibration')) {
            header.style.width = '100px';
        }
        else if (headerText.includes('id')) {
            header.style.width = '80px';
        }
        else {
            header.style.width = '110px';
        }
        
        // Ensure headers wrap words properly
        header.style.whiteSpace = 'normal';
        header.style.wordWrap = 'break-word';
        header.style.hyphens = 'auto';
        
        // Add some spacing
        header.style.lineHeight = '1.4';
        header.style.padding = '10px 8px';
    });
    
    // Fix action column cells
    fixActionColumns();
}

/**
 * Fix action column cells with buttons
 */
function fixActionColumns() {
    // Find tables
    const tables = document.querySelectorAll('table.table');

    tables.forEach(table => {
        // Get all rows
        const rows = table.querySelectorAll('tbody tr');

        rows.forEach(row => {
            const cells = row.querySelectorAll('td');

            if (cells.length === 0) return;

            const lastCell = cells[cells.length - 1];

            // Check if the last cell contains buttons/actions
            if (lastCell && (lastCell.querySelector('.btn') || lastCell.querySelector('a'))) {
                lastCell.style.whiteSpace = 'nowrap';
                lastCell.style.width = 'auto';
                lastCell.style.minWidth = '140px';
                lastCell.style.paddingRight = '10px';

                // Make buttons larger
                const buttons = lastCell.querySelectorAll('.btn');
                buttons.forEach(btn => {
                    btn.classList.add('btn-md');
                    btn.style.marginRight = '5px';
                    btn.style.padding = '0.4rem 0.7rem';
                    btn.style.fontSize = '0.9rem';
                    btn.style.boxShadow = '0 1px 3px rgba(0,0,0,0.2)';

                    // Add hover effect with JavaScript
                    btn.addEventListener('mouseover', function() {
                        this.style.transform = 'translateY(-1px)';
                        this.style.boxShadow = '0 2px 5px rgba(0,0,0,0.25)';
                    });

                    btn.addEventListener('mouseout', function() {
                        this.style.transform = 'translateY(0)';
                        this.style.boxShadow = '0 1px 3px rgba(0,0,0,0.2)';
                    });
                });
            }
        });
    });
    
    // Apply to other cells
    const tableCells = document.querySelectorAll('table td:not(:last-child)');
    tableCells.forEach(cell => {
        cell.style.wordBreak = 'break-word';
        cell.style.hyphens = 'auto';
        cell.style.verticalAlign = 'middle';
        cell.style.minHeight = '3.5em';

        // Allow multi-line content
        cell.style.whiteSpace = 'normal';
        cell.style.lineHeight = '1.3';

        // Special handling for manufacturer cells
        if (cell.classList.contains('manufacturer-cell') ||
            (cell.previousElementSibling &&
             cell.previousElementSibling.textContent.trim().toLowerCase().includes('type'))) {
            cell.style.wordBreak = 'break-word';
            cell.style.maxWidth = '150px';
            cell.style.minWidth = '120px';
        }
    });
}

/**
 * Adjust table responsiveness based on viewport width
 */
function adjustTableResponsiveness() {
    const tables = document.querySelectorAll('.table-responsive table');
    const windowWidth = window.innerWidth;
    
    tables.forEach(table => {
        if (windowWidth < 768) {
            // On mobile, focus on the important columns
            const rows = table.querySelectorAll('tr');
            
            rows.forEach(row => {
                const cells = row.querySelectorAll('th, td');
                
                // Hide less important columns on small screens
                if (cells.length > 4) {
                    // Don't hide the first column (usually ID) and last column (usually actions)
                    for (let i = 2; i < cells.length - 1; i++) {
                        // Skip hiding important columns
                        const cellText = cells[i].textContent.trim().toLowerCase();
                        if (cellText.includes('name') || 
                            cellText.includes('status') || 
                            cellText.includes('manufacturer') || 
                            cellText.includes('mfr') || 
                            cells[i].querySelector('.btn')) {
                            continue;
                        }
                        
                        // Hide less important columns on mobile
                        if (i >= 3 && i < cells.length - 1) {
                            cells[i].style.display = 'none';
                        }
                    }
                }
            });
        } else {
            // Show all columns on desktop
            const cells = table.querySelectorAll('th, td');
            cells.forEach(cell => {
                cell.style.display = '';
            });
        }
    });
}

/**
 * Observer for dynamic table changes
 */
function observeTableChanges() {
    // Create a MutationObserver to watch for changes in the DOM
    const observer = new MutationObserver(function(mutations) {
        mutations.forEach(function(mutation) {
            // Check if new tables were added
            if (mutation.addedNodes && mutation.addedNodes.length > 0) {
                for (let i = 0; i < mutation.addedNodes.length; i++) {
                    const node = mutation.addedNodes[i];
                    
                    // Check if the node is an element
                    if (node.nodeType === 1) {
                        // Check if the node is a table or contains tables
                        if (node.tagName === 'TABLE' || node.querySelector('table')) {
                            // Re-apply our enhancements
                            enhanceTableHeaders();
                            formatManufacturerNames();
                            adjustTableResponsiveness();
                            fixActionColumns();
                            return;
                        }
                    }
                }
            }
        });
    });
    
    // Start observing the document body for changes
    observer.observe(document.body, {
        childList: true,
        subtree: true
    });
}