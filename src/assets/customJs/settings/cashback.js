document.addEventListener('DOMContentLoaded', () => {
  const apiEndpoint = {
    addCashback: '/api/cashbacks/add/',
    listCashbacks: '/api/cashbacks/list/',
    userTypes: '/api/user-types/' // Foydalanuvchi turi uchun API
  };

  const addCashbackForm = document.getElementById('addCashbackForm');
  const cashbackList = document.getElementById('cashbackList');
  const userTypeSelect = document.getElementById('userType');

  // CSRF tokenni olish
  const getCSRFToken = () => {
    const cookieValue = document.cookie
      .split('; ')
      .find((row) => row.startsWith('csrftoken='))
      ?.split('=')[1];
    return cookieValue || '';
  };

  // Foydalanuvchi turlarini yuklash
  const fetchUserTypes = async () => {
    try {
      const response = await fetch(apiEndpoint.userTypes);
      const data = await response.json();

      if (data.success) {
        populateUserTypes(data.user_types);
      } else {
        toastr.error('Foydalanuvchi turlarini olishda xatolik yuz berdi.', 'Xatolik');
      }
    } catch (error) {
      toastr.error('Server bilan bog\'lanishda xatolik yuz berdi.', 'Xatolik');
    }
  };

  const populateUserTypes = (userTypes) => {
    userTypeSelect.innerHTML = '<option value="" disabled selected>Foydalanuvchi turini tanlang</option>';
    userTypes.forEach((type) => {
      userTypeSelect.innerHTML += `<option value="${type.value}">${type.label}</option>`;
    });
  };

  // Cashback yaratish
  addCashbackForm.addEventListener('submit', async (e) => {
    e.preventDefault();

    const formData = new FormData(addCashbackForm);

    try {
      const response = await fetch(apiEndpoint.addCashback, {
        method: 'POST',
        headers: {
          'X-CSRFToken': getCSRFToken()
        },
        body: formData
      });

      const result = await response.json();
      if (result.success) {
        toastr.success(result.message, 'Success');
        fetchCashbacks(); // Cashbacklar ro'yxatini yangilash
        addCashbackForm.reset();
      } else {
        toastr.error(result.message, 'Xatolik');
      }
    } catch (error) {
      toastr.error('Cashbackni qo\'shishda xatolik yuz berdi.', 'Xatolik');
    }
  });

  // Cashback ro'yxatini olish
  const fetchCashbacks = async () => {
    try {
      const response = await fetch(apiEndpoint.listCashbacks);
      const data = await response.json();

      if (data.success) {
        populateCashbacks(data.cashbacks);
      } else {
        toastr.error('Cashback ro\'yxatini olishda xatolik yuz berdi.', 'Xatolik');
      }
    } catch (error) {
      toastr.error('Server bilan bog\'lanishda xatolik yuz berdi.', 'Xatolik');
    }
  };

const populateCashbacks = (cashbacks) => {
  cashbackList.innerHTML = '';
  cashbacks.forEach((cashback) => {
    const card = `
    <div class="col-lg-4 col-md-6 mb-4">
      <div class="card border-0 shadow-sm h-100">
        <div class="card-header text-white rounded-top">
          <h5 class="card-title mb-0 fw-bold">${cashback.name}</h5>
        </div>
        <div class="card-body">
          <p class="card-text">
            <span class="badge bg-success mb-2 d-block">Summasi: ${cashback.summasi}</span>
            <span class="badge bg-info mb-2 d-block">Turi: ${cashback.type}</span>
            <span class="badge bg-warning mb-2 d-block">Foydalanuvchi turi: ${cashback.user_type}</span>
            <span class="badge ${cashback.is_active ? 'bg-primary' : 'bg-danger'} d-block">
              Status: ${cashback.is_active ? 'Faol' : 'Nofaol'}
            </span>
          </p>
          <div class="mt-4">
            <h6 class="fw-bold text-muted">Foydalanuvchilar:</h6>
            <ul class="list-group list-group-flush">
              ${cashback.users
                .map(
                  (user) =>
                    `<li class="list-group-item d-flex align-items-center">
                      <i class="ti ti-user text-primary me-2"></i>
                      <span>${user.full_name} <small class="text-muted">(${user.email})</small></span>
                    </li>`
                )
                .join('')}
            </ul>
          </div>
        </div>
        <div class="card-footer bg-light d-flex justify-content-between align-items-center">
          <button class="btn btn-outline-primary btn-sm shadow-sm rounded-pill">
            <i class="ti ti-pencil"></i> O'zgartirish
          </button>
          <button class="btn btn-outline-danger btn-sm shadow-sm rounded-pill">
            <i class="ti ti-trash"></i> O'chirish
          </button>
        </div>
      </div>
    </div>
    `;
    cashbackList.insertAdjacentHTML('beforeend', card);
  });
};



  fetchUserTypes();
  fetchCashbacks();
});
