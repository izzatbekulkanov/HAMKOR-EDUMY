document.addEventListener('DOMContentLoaded', () => {
  const apiEndpoint = '/api/setting_locations/';
  const addLocationForm = document.getElementById('addLocationForm');
  const levelField = document.getElementById('level');
  const parentIdField = document.getElementById('parentId');

  // Toast konfiguratsiyasi
  toastr.options = {
    closeButton: true,
    progressBar: true,
    positionClass: 'toast-top-right',
    showDuration: '300',
    hideDuration: '1000',
    timeOut: '5000',
    extendedTimeOut: '1000',
    showEasing: 'swing',
    hideEasing: 'linear',
    showMethod: 'fadeIn',
    hideMethod: 'fadeOut'
  };

  const fetchLocations = async () => {
    try {
      const response = await fetch(apiEndpoint);
      const data = await response.json();

      if (data.success) {
        return data;
      } else {
        toastr.error('Ma\'lumotlarni olishda xatolik yuz berdi', 'Xatolik');
      }
    } catch (error) {
      toastr.error('Server bilan bog\'lanishda xatolik yuz berdi', 'Xatolik');
    }
  };

  const updateParentOptions = async () => {
    try {
      const data = await fetchLocations();
      const selectedLevel = levelField.value;

      parentIdField.innerHTML = '<option value="" disabled selected>Ota-ona elementni tanlang</option>';
      if (selectedLevel === 'district') {
        data.regions.forEach(region => {
          parentIdField.innerHTML += `<option value="${region.id}">${region.name}</option>`;
        });
        parentIdField.disabled = false;
      } else if (selectedLevel === 'quarter') {
        data.districts.forEach(district => {
          parentIdField.innerHTML += `<option value="${district.id}">${district.name}</option>`;
        });
        parentIdField.disabled = false;
      } else {
        parentIdField.disabled = true;
      }
    } catch (error) {
      toastr.error('Ota-ona elementlarini yangilashda xatolik yuz berdi', 'Xatolik');
    }
  };

  levelField.addEventListener('change', updateParentOptions);

  addLocationForm.addEventListener('submit', async (e) => {
    e.preventDefault();

    try {
      const formData = new FormData(addLocationForm);
      const response = await fetch(apiEndpoint, {
        method: 'POST',
        body: formData
      });
      const result = await response.json();

      if (result.success) {
        toastr.success(result.message, 'Muvaffaqiyatli');
        // Filterlar bo'yicha ma'lumotni yangilash
        const updateTable = () => {
          table.ajax.reload();
        };

        addLocationForm.reset();
        parentIdField.disabled = true;
      } else {
        toastr.error('Joyni qo\'shishda xatolik yuz berdi', 'Xatolik');
      }
    } catch (error) {
      toastr.error('Server bilan bog\'lanishda xatolik yuz berdi', 'Xatolik');
    }
  });
});
