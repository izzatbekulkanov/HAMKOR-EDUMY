$(document).ready(function() {
  // Load Kasblar for Dropdown
  function loadKasblar() {
    $.ajax({
      url: '/api/kasblar/',
      type: 'GET',
      success: function(response) {
        const kasbDropdown = $('#yonalishKasb');
        kasbDropdown.empty().append('<option value="" selected disabled>Kasb tanlang</option>');

        if (response.success && response.data.length > 0) {
          response.data.forEach((kasb) => {
            kasbDropdown.append(`<option value="${kasb.id}">${kasb.nomi}</option>`);
          });
        } else {
          kasbDropdown.append('<option value="" disabled>Kasblar mavjud emas.</option>');
        }
      },
      error: function() {
        // toastr.error('Kasblarni yuklashda xatolik yuz berdi.', 'Xatolik');
        console.log("Kasblarni yuklashda xatolik yuz berdi")
      }
    });
  }

// Yo'nalishlar ro'yxatini yuklash
  function loadYonalishlar() {
    $.ajax({
      url: '/api/yonalishlar/',
      type: 'GET',
      success: function(response) {
        const yonalishList = $('#yonalishList');
        yonalishList.empty();

        if (response.success && response.data.length > 0) {
          $('#emptyYonalishMessage').hide();
          response.data.forEach((yonalish) => {
            yonalishList.append(`
            <div class="col-md-6">
              <div class="card border-0 shadow-sm h-100">
                <div class="card-body d-flex flex-column">
                  <h6 class="fw-bold">
                    <i class="ti ti-writing me-2"></i> ${yonalish.nomi}
                  </h6>
                  <p class="text-muted mb-2">Kasb: ${yonalish.kasb_nomi}</p>
                  <p class="mb-2">
                    <span class="badge bg-primary">Kurslar: ${yonalish.kurslar_soni}</span>
                    <span class="badge bg-warning">Guruhlar: ${yonalish.guruhlar_soni}</span>
                  </p>
                  <div class="mt-auto">
                    <button class="btn btn-sm btn-outline-info">
                      <i class="ti ti-eye me-1"></i> Batafsil
                    </button>
                    <button class="btn btn-sm btn-outline-danger ms-1">
                      <i class="ti ti-trash me-1"></i> O'chirish
                    </button>
                  </div>
                </div>
              </div>
            </div>
          `);
          });
        } else {
          yonalishList.append('<div class="col-12 text-center text-muted" id="emptyYonalishMessage">Yo\'nalishlar mavjud emas.</div>');
        }
      },
      error: function() {
        console.log("Yo\'nalishlarni yuklashda xatolik yuz berdi.")
      }
    });
  }

  // Add New Yo'nalish
  $('#addYonalishForm').on('submit', function(e) {
    e.preventDefault();

    const formData = $(this).serialize();

    $.ajax({
      url: '/api/yonalishlar/',
      type: 'POST',
      data: formData,
      headers: { 'X-CSRFToken': $('input[name="csrfmiddlewaretoken"]').val() },
      success: function(response) {
        if (response.success) {
          toastr.success('Yo\'nalish muvaffaqiyatli qo\'shildi!', 'Muvaffaqiyat');
          $('#addYonalishForm')[0].reset();
          $('#addYonalishCollapse').collapse('hide');
          loadYonalishlar();
        } else {
          toastr.error(response.message || 'Yo\'nalish qo\'shishda xatolik yuz berdi.', 'Xatolik');
        }
      },
      error: function() {
        toastr.error('Yo\'nalish qo\'shishda xatolik yuz berdi.', 'Xatolik');
      }
    });
  });

  // Initial Load
  loadKasblar();
  loadYonalishlar();
});
