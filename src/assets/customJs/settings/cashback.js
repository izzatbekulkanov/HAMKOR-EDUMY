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
      <div class="col-md-6 mb-4">
        <div class="card shadow-lg rounded-4 border-0" style="background: linear-gradient(135deg, #f5f7fa, #c3cfe2);">
          <div class="card-body">
            <h5 class="card-title text-primary fw-bold">${cashback.name}</h5>
            <p class="card-text">
              <span class="badge bg-success">Summasi: ${cashback.summasi}</span> <br>
              <span class="badge bg-info mt-2">Turi: ${cashback.type}</span> <br>
              <span class="badge bg-warning mt-2">Foydalanuvchi turi: ${cashback.user_type}</span> <br>
              <span class="badge ${cashback.is_active ? 'bg-primary' : 'bg-danger'} mt-2">
                Status: ${cashback.is_active ? 'Faol' : 'Nofaol'}
              </span>
            </p>
            <div class="mt-3">
              <h6 class="text-muted fw-semibold">Foydalanuvchilar:</h6>
              <ul class="list-unstyled mb-0">
                ${cashback.users
        .map(
          (user) =>
            `<li class="d-flex align-items-center mb-2">
                        <i class="ti ti-user text-primary me-2"></i>
                        <span>${user.full_name} <small class="text-muted">(${user.email})</small></span>
                      </li>`
        )
        .join('')}
              </ul>
            </div>
            <button class="btn btn-light shadow-sm rounded-pill mt-3">
              <i class="ti ti-pencil text-info"></i> O'zgartirish
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
