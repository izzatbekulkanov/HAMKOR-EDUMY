$(document).ready(function() {
  // Toastr configuration
  toastr.options = {
    closeButton: true,
    debug: false,
    newestOnTop: true,
    progressBar: true,
    positionClass: 'toast-bottom-right',
    preventDuplicates: true,
    showDuration: '300',
    hideDuration: '1000',
    timeOut: '5000',
    extendedTimeOut: '1000',
    showEasing: 'swing',
    hideEasing: 'linear',
    showMethod: 'fadeIn',
    hideMethod: 'fadeOut'
  };

  // Load Kasblar list
  function loadKasblar() {
    $.ajax({
      url: '/api/kasblar/',
      type: 'GET',
      success: function(response) {
        const kasbList = $('#kasbList');
        kasbList.empty();

        if (response.success && response.data.length > 0) {
          response.data.forEach((kasb) => {
            kasbList.append(`
            <li class="list-group-item">
              <div class="d-flex justify-content-between align-items-center">
                <div>
                  <strong>${kasb.nomi}</strong>
                </div>
                <div class="d-flex align-items-center">
                  <span class="badge bg-primary me-2">Yo'nalishlar: ${kasb.yonalish_count}</span>
                  <span class="badge bg-success me-2">Kurslar: ${kasb.kurs_count}</span>
                  <span class="badge bg-warning me-2">Guruhlar: ${kasb.guruh_count}</span>
                  <div class="form-check form-switch">
                    <input
                      class="form-check-input toggle-active"
                      type="checkbox"
                      id="kasb-${kasb.id}"
                      data-id="${kasb.id}"
                      ${kasb.is_active ? 'checked' : ''}>
                  </div>
                </div>
              </div>
            </li>
          `);
          });

          // Handle checkbox toggle
          $('.toggle-active').on('change', function() {
            const kasbId = $(this).data('id');
            const isActive = $(this).is(':checked');

            $.ajax({
              url: `/api/kasblar/${kasbId}/`,
              type: 'PATCH',
              contentType: 'application/json',
              headers: { 'X-CSRFToken': $('input[name="csrfmiddlewaretoken"]').val() },
              data: JSON.stringify({ is_active: isActive }),
              success: function(response) {
                if (response.success) {
                  toastr.success('Faollik muvaffaqiyatli yangilandi!', 'Muvaffaqiyat');
                } else {
                  toastr.error(response.message || 'Faollikni yangilashda xatolik yuz berdi.', 'Xatolik');
                }
              },
              error: function() {
                toastr.error('Faollikni yangilashda xatolik yuz berdi.', 'Xatolik');
              }
            });
          });
        } else {
          kasbList.append('<div class="list-group-item text-center text-muted">Kasblar mavjud emas.</div>');
        }
      },
      error: function() {
        toastr.error('Kasblarni yuklashda xatolik yuz berdi.', 'Xatolik');
      }
    });
  }


  // Add Kasb
  $('#addKasbForm').on('submit', function(e) {
    e.preventDefault();

    const formData = {
      nomi: $('#kasbNomi').val(),
      is_active: $('#kasbActive').val()
    };

    $.ajax({
      url: '/api/kasblar/',
      type: 'POST',
      contentType: 'application/json',
      data: JSON.stringify(formData),
      headers: { 'X-CSRFToken': $('input[name="csrfmiddlewaretoken"]').val() },
      success: function(response) {
        if (response.success) {
          toastr.success('Kasb muvaffaqiyatli qo\'shildi!', 'Muvaffaqiyat');
          $('#addKasbForm')[0].reset();
          loadKasblar();
        } else {
          toastr.error(response.message || 'Kasb qo\'shishda xatolik yuz berdi.', 'Xatolik');
        }
      },
      error: function() {
        toastr.error('Kasb qo\'shishda xatolik yuz berdi.', 'Xatolik');
      }
    });
  });

  // Initial load
  loadKasblar();
});
