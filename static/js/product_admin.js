document.addEventListener('DOMContentLoaded', function() {
    const categoryField = document.getElementById('id_category');
    const addButton = document.querySelector('.add-row a');

    if (categoryField) {
        categoryField.addEventListener('change', function() {
            const categoryId = this.value;

            if (categoryId) {
                // Отправляем запрос на сервер для получения характеристик категории
                fetch(`/admin/get_characteristics/?category_id=${categoryId}`)
                    .then(response => response.json())
                    .then(data => {
                        // Очищаем существующие строки характеристик
                        const rows = document.querySelectorAll('.dynamic-productcharacteristic_set');
                        rows.forEach(row => row.remove());

                        // Добавляем строки для каждой характеристики
                        data.characteristics.forEach(characteristic => {
                            // Нажимаем кнопку "Добавить ещё"
                            addButton.click();

                            // Заполняем последнюю добавленную строку
                            const lastRow = document.querySelector('.dynamic-productcharacteristic_set:last-child');
                            const characteristicField = lastRow.querySelector('select[name$="-characteristic"]');
                            const valueField = lastRow.querySelector('input[name$="-value"]');

                            if (characteristicField && valueField) {
                                characteristicField.value = characteristic.id;
                                valueField.value = '';
                            }
                        });
                    });
            } else {
                // Если категория не выбрана, очищаем строки характеристик
                const rows = document.querySelectorAll('.dynamic-productcharacteristic_set');
                rows.forEach(row => row.remove());
            }
        });
    }
});