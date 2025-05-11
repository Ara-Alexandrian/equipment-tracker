    // Direct edit function for equipment (receives parameters directly)
    function directEditEquipment(id, category, type, manufacturer, model, serial, location, calibration, notes) {
        console.log("Direct edit called with:", { id, category, type, manufacturer, model, serial, location, calibration, notes });
        showDebug(`Editing equipment: ${id} - ${manufacturer} ${model} - ${serial} - ${location} - ${calibration}`);
        
        // Force the notes parameter to be a string, even if undefined
        notes = notes || "";
        
        // Make sure data is properly escaped if it contains quotes
        notes = notes.replace(/"/g, '&quot;').replace(/'/g, '&#39;');
        
        // Store the data in a global variable to ensure it's available even if the form fields lose focus
        currentEditData = {
            id: id,
            category: category,
            type: type,
            manufacturer: manufacturer,
            model: model,
            serial: serial,
            location: location,
            calibration: calibration,
            notes: notes
        };
        
        console.log("Stored data in currentEditData:", currentEditData);

        // Set form action
        document.getElementById('editEquipmentForm').action = `/admin/equipment/edit/${id}`;

        // Wait a tiny bit to ensure the DOM is ready
        setTimeout(() => {
            try {
                // Use multiple techniques to ensure form fields are set correctly
                
                // 1. Set values using standard DOM methods
                document.getElementById('edit_id').value = id;
                document.getElementById('edit_category').value = category;
                document.getElementById('edit_equipment_type').value = type;
                document.getElementById('edit_manufacturer').value = manufacturer;
                document.getElementById('edit_model').value = model;
                document.getElementById('edit_serial_number').value = serial;
                document.getElementById('edit_location').value = location;
                document.getElementById('edit_calibration_due_date').value = calibration;
                document.getElementById('edit_notes').value = notes;

                // 2. Also set using jQuery for redundancy
                $('#edit_id').val(id);
                $('#edit_category').val(category);
                $('#edit_equipment_type').val(type);
                $('#edit_manufacturer').val(manufacturer);
                $('#edit_model').val(model);
                $('#edit_serial_number').val(serial);
                $('#edit_location').val(location);
                $('#edit_calibration_due_date').val(calibration);
                $('#edit_notes').val(notes);

                // 3. Force select elements to update
                const categorySelect = document.getElementById('edit_category');
                for (let i = 0; i < categorySelect.options.length; i++) {
                    if (categorySelect.options[i].value === category) {
                        categorySelect.selectedIndex = i;
                        break;
                    }
                }

                // Set QR button data
                document.getElementById('generateQRBtn').setAttribute('data-id', id);

                // Print current form values
                const formValues = {
                    id: document.getElementById('edit_id').value,
                    category: document.getElementById('edit_category').value,
                    type: document.getElementById('edit_equipment_type').value,
                    manufacturer: document.getElementById('edit_manufacturer').value,
                    model: document.getElementById('edit_model').value,
                    serial: document.getElementById('edit_serial_number').value,
                    location: document.getElementById('edit_location').value,
                    calibration: document.getElementById('edit_calibration_due_date').value
                };

                console.log("Form values after initial setting:", formValues);
                
                // Check for missing values and try again if needed
                if (!formValues.id || !formValues.manufacturer || !formValues.serial) {
                    console.warn("Some values weren't set properly, trying again");
                    setTimeout(() => {
                        // Try setting again after a delay
                        document.getElementById('edit_id').value = id;
                        document.getElementById('edit_category').value = category;
                        document.getElementById('edit_equipment_type').value = type;
                        document.getElementById('edit_manufacturer').value = manufacturer;
                        document.getElementById('edit_model').value = model;
                        document.getElementById('edit_serial_number').value = serial;
                        document.getElementById('edit_location').value = location;
                        document.getElementById('edit_calibration_due_date').value = calibration;
                        document.getElementById('edit_notes').value = notes;
                        
                        console.log("Values after second attempt:", {
                            id: document.getElementById('edit_id').value,
                            category: document.getElementById('edit_category').value,
                            type: document.getElementById('edit_equipment_type').value,
                            manufacturer: document.getElementById('edit_manufacturer').value
                        });
                    }, 100);
                }
            } catch (error) {
                console.error("Error setting form values:", error);
            }
        }, 10);

        // Create debug info on the modal
        setTimeout(() => {
            // Find existing debug info and remove it
            const existingInfo = document.querySelector('#editEquipmentModal .alert');
            if (existingInfo) {
                existingInfo.remove();
            }

            // Add new info
            const modalBody = document.querySelector('#editEquipmentModal .modal-body');
            if (modalBody) {
                const infoDiv = document.createElement('div');
                infoDiv.className = 'alert alert-info mt-3';
                infoDiv.innerHTML = `
                    <p><strong>Equipment Data:</strong></p>
                    <p>ID: ${id}</p>
                    <p>Category: ${category}</p>
                    <p>Type: ${type}</p>
                    <p>Manufacturer: ${manufacturer}</p>
                    <p>Model: ${model}</p>
                    <p>Serial: ${serial}</p>
                    <p>Location: ${location}</p>
                    <p>Calibration: ${calibration}</p>
                `;
                modalBody.appendChild(infoDiv);
            }
        }, 300);
    }