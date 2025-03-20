document.addEventListener('DOMContentLoaded', function () {
    const showAddressCheckbox = document.getElementById('show-address');
    const addressFields = document.getElementById('address-fields');
    const form = document.querySelector('form');

    const alwaysOptionalFields = ['id_address_field1', 'id_address_field2', 'id_state'];

    function toggleAddressFields() {
        const addressInputs = addressFields.querySelectorAll('input, select, textarea');

        if (showAddressCheckbox.checked) {
            addressFields.classList.remove('hidden');
            addressInputs.forEach(input => {
                input.removeAttribute('disabled');
                if (!alwaysOptionalFields.includes(input.id)) {
                    input.setAttribute('required', 'required');
                } else {
                    input.removeAttribute('required'); 
                }
            });
        } else {
            addressFields.classList.add('hidden');
            addressInputs.forEach(input => {
                input.removeAttribute('required');
                input.setAttribute('disabled', true);
            });
        }
    }
    showAddressCheckbox.addEventListener('change', toggleAddressFields);
    toggleAddressFields();
    form.addEventListener('submit', function () {
        toggleAddressFields();  
    });
});