document.addEventListener('DOMContentLoaded', () => {
  const apiEndpoint = {
    addClass: '/api/classes/add/',
    schools: '/api/schools/list/',
    stats: '/api/classes/stats/', // Sinflar va maktablar statistikasi uchun API
    classes: '/api/classes/list/' // Sinflar ro'yxati uchun API
  };

  const addClassForm = document.getElementById('addClassForm');
  const schoolSelect = document.getElementById('schoolSelect');
  const totalClasses = document.getElementById('totalClasses');
  const totalSchools = document.getElementById('totalSchools');
  const classListContainer = document.getElementById('classList');

  // CSRF tokenni olish
  const getCSRFToken = () => {
    const cookieValue = document.cookie
      .split('; ')
      .find((row) => row.startsWith('csrftoken='))
      ?.split('=')[1];
    return cookieValue || '';
  };

  // Maktablarni yuklash
  const fetchSchools = async () => {
    try {
      const response = await fetch(apiEndpoint.schools);
      const data = await response.json();

      if (data.success) {
        populateSchools(data.schools);
      } else {
        toastr.error('Maktablar ro\'yxatini olishda xatolik yuz berdi.', 'Xatolik');
      }
    } catch (error) {
      toastr.error('Server bilan bog\'lanishda xatolik yuz berdi.', 'Xatolik');
    }
  };

  const populateSchools = (schools) => {
    schoolSelect.innerHTML = '<option value="" disabled selected>Maktabni tanlang</option>';
    schools.forEach((school) => {
      schoolSelect.innerHTML += `<option value="${school.id}">${school.maktab_raqami}</option>`;
    });
  };

  // Statistikani yuklash
  const fetchStats = async () => {
    try {
      const response = await fetch(apiEndpoint.stats);
      const data = await response.json();

      if (data.success) {
        totalClasses.textContent = data.stats.total_classes || 0;
        totalSchools.textContent = data.stats.total_schools || 0;
      } else {
        toastr.error('Statistik ma\'lumotlarni olishda xatolik yuz berdi.', 'Xatolik');
      }
    } catch (error) {
      toastr.error('Server bilan bog\'lanishda xatolik yuz berdi.', 'Xatolik');
    }
  };

  // Sinflar ro'yxatini yuklash va guruhlash
  const fetchClasses = async () => {
    try {
      const response = await fetch(apiEndpoint.classes);
      const data = await response.json();

      if (data.success) {
        groupClassesBySchool(data.classes);
      } else {
        toastr.error('Sinflar ro\'yxatini olishda xatolik yuz berdi.', 'Xatolik');
      }
    } catch (error) {
      toastr.error('Server bilan bog\'lanishda xatolik yuz berdi.', 'Xatolik');
    }
  };

// Maktab bo‘yicha guruhlash
  const groupClassesBySchool = (classes) => {
    classListContainer.innerHTML = '';

    // Maktablarni guruhlash
    const groupedSchools = classes.reduce((group, cls) => {
      if (!group[cls.maktab.raqami]) {
        group[cls.maktab.raqami] = {
          maktab: cls.maktab,
          sinflar: []
        };
      }
      group[cls.maktab.raqami].sinflar.push(cls);
      return group;
    }, {});

    // Har bir maktab uchun kartani yaratish
    Object.values(groupedSchools).forEach((school) => {
      const schoolCard = `
      <div class="col-md-12 mb-4">
        <div class="card shadow-sm">
          <div class="card-header bg-primary text-white">
            <h5 class="card-title">${school.maktab.raqami} - ${school.maktab.viloyat}, ${school.maktab.tuman}</h5>
          </div>
          <div class="card-body">
            <div class="row">
              ${school.sinflar
        .map(
          (cls) => `
                <div class="col-md-4 mb-3">
                  <div class="card">
                    <div class="card-body">
                      <h6 class="card-title text-primary">${cls.sinf_raqami}</h6>
                      <p class="card-text">
                        <strong>Belgi:</strong> ${cls.belgi || 'Noma\'lum'} <br>
                        <strong>Status:</strong> ${cls.is_active ? 'Faol' : 'Nofaol'} <br>
                        <strong>Yaratilgan:</strong> ${cls.created_at}
                      </p>
                    </div>
                  </div>
                </div>
              `
        )
        .join('')}
            </div>
          </div>
        </div>
      </div>
    `;
      classListContainer.insertAdjacentHTML('beforeend', schoolCard);
    });
  };

  fetchClasses();

  const populateClasses = (classes) => {
    classListContainer.innerHTML = '';
    classes.forEach((cls) => {
      const card = `
        <div class="col-md-4 mb-4">
          <div class="card shadow-sm">
            <div class="card-body">
              <h5 class="card-title text-primary">${cls.sinf_raqami}</h5>
              <p class="card-text">
                <strong>Belgi:</strong> ${cls.belgi} <br>
                <strong>Maktab:</strong> ${cls.maktab.raqami} <br>
                <strong>Viloyat:</strong> ${cls.maktab.viloyat} <br>
                <strong>Tuman:</strong> ${cls.maktab.tuman} <br>
                <strong>Status:</strong> ${cls.is_active ? 'Faol' : 'Nofaol'} <br>
                <strong>Yaratilgan:</strong> ${cls.created_at}
              </p>
            </div>
          </div>
        </div>
      `;
      classListContainer.insertAdjacentHTML('beforeend', card);
    });
  };

  // Sinfni qo'shish
  addClassForm.addEventListener('submit', async (e) => {
    e.preventDefault();

    const formData = {
      maktab: schoolSelect.value,
      sinf_raqami: document.getElementById('classNumber').value,
      belgi: document.getElementById('badgeName').value.toUpperCase() // Belgini katta harfga aylantirish
    };

    try {
      const response = await fetch(apiEndpoint.addClass, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': getCSRFToken() // CSRF tokenni yuborish
        },
        body: JSON.stringify(formData)
      });

      const result = await response.json();

      if (result.success) {
        toastr.success(result.message, 'Success');
        addClassForm.reset();
        fetchStats();
        fetchClasses(); // Sinflar ro'yxatini yangilash
      } else {
        toastr.error(result.message || 'Xatolik yuz berdi.', 'Xatolik');
      }
    } catch (error) {
      toastr.error('Sinfni qo\'shishda xatolik yuz berdi.', 'Xatolik');
    }
  });

  fetchSchools();
  fetchStats();
  fetchClasses();
});
