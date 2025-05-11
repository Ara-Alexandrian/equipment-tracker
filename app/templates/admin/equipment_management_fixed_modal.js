    $('#editEquipmentModal').on('show.bs.modal', function() {
        console.log("jQuery modal show event triggered (before modal is shown)");
        
        // Apply the values again just before the modal is shown
        if (currentEditData) {
            console.log("Pre-populating form fields before modal is shown:", currentEditData);
            
            // Set form action
            $('#editEquipmentForm').attr('action', `/admin/equipment/edit/${currentEditData.id}`);
            
            // Set all form fields using jQuery
            $('#edit_id').val(currentEditData.id);
            $('#edit_category').val(currentEditData.category);
            $('#edit_equipment_type').val(currentEditData.type);
            $('#edit_manufacturer').val(currentEditData.manufacturer);
            $('#edit_model').val(currentEditData.model);
            $('#edit_serial_number').val(currentEditData.serial);
            $('#edit_location').val(currentEditData.location);
            $('#edit_calibration_due_date').val(currentEditData.calibration);
            $('#edit_notes').val(currentEditData.notes);
            
            // Set QR button data
            $('#generateQRBtn').attr('data-id', currentEditData.id);
            
            // Force select elements to update
            const categorySelect = document.getElementById('edit_category');
            for (let i = 0; i < categorySelect.options.length; i++) {
                if (categorySelect.options[i].value === currentEditData.category) {
                    categorySelect.selectedIndex = i;
                    break;
                }
            }
            
            // Add custom attributes to check values at all stages
            $('#edit_id').attr('data-original', currentEditData.id);
            $('#edit_manufacturer').attr('data-original', currentEditData.manufacturer);
            $('#edit_serial_number').attr('data-original', currentEditData.serial);
        }
    });
    
    $('#editEquipmentModal').on('shown.bs.modal', function() {
        console.log("jQuery modal shown event triggered (after modal is shown)");

        // Verify the form values after the modal is fully shown
        const formValues = {
            id: $('#edit_id').val(),
            category: $('#edit_category').val(),
            type: $('#edit_equipment_type').val(),
            manufacturer: $('#edit_manufacturer').val(),
            model: $('#edit_model').val(),
            serial: $('#edit_serial_number').val(),
            location: $('#edit_location').val(),
            calibration: $('#edit_calibration_due_date').val(),
            notes: $('#edit_notes').val()
        };

        console.log("Modal shown - current form values:", formValues);

        // If values are missing or incorrect, try to repopulate from the stored data
        if (currentEditData && (
            !formValues.id || 
            formValues.category !== currentEditData.category ||
            formValues.type !== currentEditData.type ||
            formValues.manufacturer !== currentEditData.manufacturer ||
            formValues.model !== currentEditData.model ||
            formValues.serial !== currentEditData.serial ||
            formValues.location !== currentEditData.location ||
            formValues.calibration !== currentEditData.calibration
        )) {
            console.log("Values missing or incorrect, repopulating from stored data:", currentEditData);

            // Repopulate the form again with stored data
            $('#edit_id').val(currentEditData.id);
            $('#edit_category').val(currentEditData.category);
            $('#edit_equipment_type').val(currentEditData.type);
            $('#edit_manufacturer').val(currentEditData.manufacturer);
            $('#edit_model').val(currentEditData.model);
            $('#edit_serial_number').val(currentEditData.serial);
            $('#edit_location').val(currentEditData.location);
            $('#edit_calibration_due_date').val(currentEditData.calibration);
            $('#edit_notes').val(currentEditData.notes);

            // Set QR button data
            $('#generateQRBtn').attr('data-id', currentEditData.id);
            
            // Use setTimeout to ensure this runs after any browser form resets
            setTimeout(() => {
                // One more attempt at setting the values
                document.getElementById('edit_id').value = currentEditData.id;
                document.getElementById('edit_category').value = currentEditData.category;
                document.getElementById('edit_equipment_type').value = currentEditData.type;
                document.getElementById('edit_manufacturer').value = currentEditData.manufacturer;
                document.getElementById('edit_model').value = currentEditData.model;
                document.getElementById('edit_serial_number').value = currentEditData.serial;
                document.getElementById('edit_location').value = currentEditData.location;
                document.getElementById('edit_calibration_due_date').value = currentEditData.calibration;
                document.getElementById('edit_notes').value = currentEditData.notes;
                
                // Force select elements to update again
                const categorySelect = document.getElementById('edit_category');
                for (let i = 0; i < categorySelect.options.length; i++) {
                    if (categorySelect.options[i].value === currentEditData.category) {
                        categorySelect.selectedIndex = i;
                        break;
                    }
                }
                
                // Check if our values were properly set
                const finalCheck = {
                    id: document.getElementById('edit_id').value,
                    manufacturer: document.getElementById('edit_manufacturer').value,
                    serial: document.getElementById('edit_serial_number').value
                };
                
                console.log("Final value check:", finalCheck);
            }, 50);
        }

        // Display debug info in the modal
        setTimeout(() => {
            // Check for existing debug info
            const existingDebug = $('.modal-debug-info');
            if (existingDebug.length > 0) {
                existingDebug.remove();
            }

            // Create new debug info
            const updatedValues = {
                id: $('#edit_id').val(),
                category: $('#edit_category').val(),
                manufacturer: $('#edit_manufacturer').val(),
                model: $('#edit_model').val(),
                type: $('#edit_equipment_type').val(),
                serial: $('#edit_serial_number').val(),
                location: $('#edit_location').val(),
                calibration: $('#edit_calibration_due_date').val()
            };

            const debugHtml = `
                <div class="alert alert-info mt-3 modal-debug-info">
                    <p><strong>Form Values After Modal Shown:</strong></p>
                    <p>ID: ${updatedValues.id}</p>
                    <p>Category: ${updatedValues.category}</p>
                    <p>Type: ${updatedValues.type}</p>
                    <p>Manufacturer: ${updatedValues.manufacturer}</p>
                    <p>Model: ${updatedValues.model}</p>
                    <p>Serial: ${updatedValues.serial}</p>
                    <p>Location: ${updatedValues.location}</p>
                    <p>Calibration: ${updatedValues.calibration}</p>
                </div>
            `;

            $('#editEquipmentModal .modal-body').append(debugHtml);
        }, 200);
    });