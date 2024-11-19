document.addEventListener('DOMContentLoaded', () => {
    const apiEndpoint = '/api/get-locations/';

    // Filter elementlari
    const searchField = document.getElementById('searchField');
    const levelFilter = document.getElementById('levelFilter');

    // DataTable sozlash
    const table = $('#locationTable').DataTable({
        processing: true,
        serverSide: true,
        ajax: {
            url: apiEndpoint,
            type: 'GET',
            data: function (d) {
                d.search = searchField.value || '';
                d.level = levelFilter.value || '';
            }
        },
        columns: [
            { data: 'name', title: 'Nomi' },
            { data: 'code', title: 'Kodi' },
            { data: 'level', title: 'Daraja' },
            { data: 'parent_name', title: 'Ota-ona elementi' }
        ]
    });

    // Filterlar bo'yicha ma'lumotni yangilash
    const updateTable = () => {
        table.ajax.reload();
    };

    // Filter eventlari
    searchField.addEventListener('input', updateTable);
    levelFilter.addEventListener('change', updateTable);
});
