$(document).ready(function() {
  // Narxni formatlash uchun funksiyani o'rnatish
  function formatCurrency(input) {
    const value = input.value.replace(/,/g, '');
    if (!isNaN(value)) {
      input.value = parseFloat(value).toLocaleString('uz-UZ');
    } else {
      input.value = input.value.substring(0, input.value.length - 1);
    }
  }

  // Kurs narxi input qatori uchun real vaqtli formatlash
  $(document).on('input', '.kurs-narxi', function() {
    formatCurrency(this);
  });

// Global kurslar ro'yxati
  let kurslarData = [];

  // Kurslar ro'yxatini yuklash
  function loadKurslar() {
    $.ajax({
      url: '/api/kurslar/',
      type: 'GET',
      success: function(response) {
        const kursList = $('#kursList');
        kursList.empty();

        if (response.success && response.data.length > 0) {
          // Kurslarni global o'zgaruvchiga saqlash
          kurslarData = response.data;

          response.data.forEach((kurs) => {
            kursList.append(`
              <div class="col-md-6">
                <div class="card border-0 shadow-sm h-100">
                  <div class="card-body d-flex flex-column">
                    <h6 class="fw-bold text-primary"><i class="ti ti-book me-2"></i> ${kurs.nomi}</h6>
                    <p class="mb-1"><strong>Narxi:</strong> ${kurs.narxi.toLocaleString('uz-UZ')} so'm</p>
                    <p class="text-muted mb-1"><strong>Yo'nalish:</strong> ${kurs.yonalish_nomi}</p>
                    <p class="text-muted mb-3"><strong>Guruhlar soni:</strong> ${kurs.guruh_count}, <strong>Talabalar soni:</strong> ${kurs.student_count}</p>
                    <div class="mt-auto d-flex justify-content-between">
                      <button class="btn btn-sm btn-outline-info" onclick="viewKursDetails(${kurs.id})">
                        <i class="ti ti-eye me-1"></i> Batafsil
                      </button>
                      <button class="btn btn-sm btn-outline-danger">
                        <i class="ti ti-trash me-1"></i> O'chirish
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            `);
          });
        } else {
          kursList.append('<div class="col-12 text-center text-muted" id="emptyKursMessage">Kurslar mavjud emas.</div>');
        }
      },
      error: function() {
        toastr.error('Kurslarni yuklashda xatolik yuz berdi.', 'Xatolik');
      }
    });
  }

  // Kurs tafsilotlarini ko'rsatish
  window.viewKursDetails = function(kursId) {
    // Kursni global o'zgaruvchidan qidirish
    const kurs = kurslarData.find((k) => k.id === kursId);
    if (kurs) {
      $('#kursDetailsModal .modal-title').text(kurs.nomi);
      $('#kursDetailsModal .modal-body').html(`
        <p><strong>Narxi:</strong> ${kurs.narxi.toLocaleString('uz-UZ')} so'm</p>
        <p><strong>Yo'nalish:</strong> ${kurs.yonalish_nomi}</p>
        <p><strong>Guruhlar soni:</strong> ${kurs.guruh_count}</p>
        <p><strong>Talabalar soni:</strong> ${kurs.student_count}</p>
        <p><strong>Yaratilgan:</strong> ${kurs.created_at}</p>
        <p><strong>Yangilangan:</strong> ${kurs.updated_at}</p>
      `);
      $('#kursDetailsModal').modal('show');
    } else {
      toastr.error('Kurs topilmadi.', 'Xatolik');
    }
  };

  // Yo'nalishlarni yuklash va select dropdownni to'ldirish
  function loadYonalishOptions() {
    $.ajax({
      url: '/api/yonalishlar/',
      type: 'GET',
      success: function(response) {
        const yonalishDropdown = $('#kursYonalish');
        yonalishDropdown.empty().append('<option value="" selected disabled>Yo\'nalish tanlang</option>');

        if (response.success && response.data.length > 0) {
          response.data.forEach((yonalish) => {
            yonalishDropdown.append(`<option value="${yonalish.id}">${yonalish.nomi}</option>`);
          });
        } else {
          toastr.error('Yo\'nalishlarni yuklashda xatolik yuz berdi.', 'Xatolik');
        }
      },
      error: function() {
        toastr.error('Yo\'nalishlarni yuklashda xatolik yuz berdi.', 'Xatolik');
      }
    });
  }

  // Yangi Kurs qo'shish
  $('#addKursForm').on('submit', function(e) {
    e.preventDefault();

    const kursNarxi = $('#kursNarxi').val().replace(/,/g, ''); // Narxni formatdan tozalash
    const formData = $(this).serializeArray();
    formData.find((field) => field.name === 'narxi').value = kursNarxi;

    $.ajax({
      url: '/api/kurslar/',
      type: 'POST',
      data: $.param(formData),
      headers: { 'X-CSRFToken': $('input[name="csrfmiddlewaretoken"]').val() },
      success: function(response) {
        if (response.success) {
          toastr.success('Kurs muvaffaqiyatli qo\'shildi!', 'Muvaffaqiyat');
          $('#addKursForm')[0].reset();
          loadKurslar();
        } else {
          toastr.error(response.message || 'Kurs qo\'shishda xatolik yuz berdi.', 'Xatolik');
        }
      },
      error: function() {
        toastr.error('Kurs qo\'shishda xatolik yuz berdi.', 'Xatolik');
      }
    });
  });

  // Dastlabki yuklash
  loadYonalishOptions(); // Yo'nalishlarni yuklash
  loadKurslar(); // Kurslarni yuklash
});
