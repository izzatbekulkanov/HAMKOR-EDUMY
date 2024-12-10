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
    <div class="col-lg-4 col-md-6 mb-3">
      <div class="card border-0 shadow-sm h-100">
        <div class="card-header d-flex justify-content-between align-items-center bg-light">
          <h6 class="card-title mb-0 text-primary fw-bold">${cashback.name}</h6>
        </div>
        <div class="card-body small">
          <p class="mb-1">
            <strong>Summasi:</strong> ${cashback.summasi} |
            <strong>Parent:</strong> ${cashback.parent_sum}
          </p>
          <p class="mb-1">
            <strong>Turi:</strong> ${cashback.type} |
            <strong>Foydalanuvchi turi:</strong> ${cashback.user_type}
          </p>
          <p class="mb-1">
            <strong>Status:</strong> <span class="badge ${cashback.is_active ? 'bg-success' : 'bg-danger'}">
              ${cashback.is_active ? 'Faol' : 'Nofaol'}
            </span>
          </p>
          <div class="mt-2">
            <strong>Foydalanuvchilar:</strong>
            <ul class="list-group list-group-flush small">
              ${cashback.users
                .map(
                  (user) => `
                    <li class="list-group-item px-0 d-flex align-items-center">
                      <i class="ti ti-user text-primary me-2"></i>
                      ${user.full_name} <small class="text-muted">(${user.email})</small>
                    </li>`
                )
                .join('')}
            </ul>
          </div>
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
