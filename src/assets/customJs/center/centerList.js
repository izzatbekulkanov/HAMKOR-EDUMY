 $(document).ready(function() {
  // Toastr configuration
  toastr.options = {
    closeButton: true,
    debug: false,
    newestOnTop: true,
    progressBar: true,
    positionClass: 'toast-bottom-right',
    preventDuplicates: true,
    onclick: null,
    showDuration: '300',
    hideDuration: '1000',
    timeOut: '5000',
    extendedTimeOut: '1000',
    showEasing: 'swing',
    hideEasing: 'linear',
    showMethod: 'fadeIn',
    hideMethod: 'fadeOut'
  };

  // Load available admins into the dropdown
  function loadAdmins() {
    $.ajax({
      url: '/api/get-admins/', // API endpoint for fetching admins
      type: 'GET',
      success: function(response) {
        const adminDropdown = $('#centerAdmin');
        adminDropdown.empty().append('<option value="" selected disabled>Adminni tanlang</option>');

        if (response.success) {
          response.data.forEach((admin) => {
            adminDropdown.append(
              `<option value="${admin.id}">${admin.full_name} (${admin.phone_number || 'Telefon yo‘q'})</option>`
            );
          });
        } else {
          toastr.error(response.message || 'Adminlarni yuklashda xatolik yuz berdi.', 'Xatolik');
        }
      },
      error: function() {
        toastr.error('Adminlarni yuklashda xatolik yuz berdi.', 'Xatolik');
      }
    });
  }

  // Trigger admin loading when the modal is shown
  $('#addCenterModal').on('show.bs.modal', function() {
    loadAdmins(); // Load admins dynamically
  });

    // Markaz qo'shish formasi yuborilishi
  $('#addCenterForm').on('submit', function (e) {
    e.preventDefault(); // Formani odatiy yuborishdan to'xtatish

    const formData = new FormData(this); // Formni avtomatik yig'ish

    $.ajax({
        url: '/api/add-center/', // API endpoint
        type: 'POST',
        headers: { 'X-CSRFToken': $('input[name="csrfmiddlewaretoken"]').val() }, // CSRF Token
        data: formData,
        processData: false, // FormData obyekti ishlatganda kerak
        contentType: false, // FormData bilan content-type avtomatik aniqlanadi
        success: function (response) {
            if (response.success) {
                toastr.success('O‘quv markaz muvaffaqiyatli qo‘shildi!', 'Muvaffaqiyat');
                $('#addCenterModal').modal('hide'); // Modalni yopish
                $('#addCenterForm')[0].reset(); // Formani tozalash
                loadCenters(); // Yangi markazlarni yuklash funksiyasi
            } else {
                toastr.error(response.message || 'Markaz qo‘shishda xatolik yuz berdi.', 'Xatolik');
            }
        },
        error: function () {
            toastr.error('So‘rovda xatolik yuz berdi.', 'Xatolik');
        },
    });
});


  // Reusable AJAX function
  function ajaxRequest(url, type, data, successCallback, errorCallback) {
    $.ajax({
      url,
      type,
      headers: { 'X-CSRFToken': $('input[name="csrfmiddlewaretoken"]').val() },
      data,
      processData: false,
      contentType: false,
      success: successCallback,
      error: function(xhr) {
        let errorMessage = 'Xatolik yuz berdi.';
        if (xhr.responseJSON && xhr.responseJSON.message) {
          errorMessage = xhr.responseJSON.message;
        }
        if (errorCallback) {
          errorCallback(errorMessage);
        } else {
          toastr.error(errorMessage, 'Xatolik');
        }
      }
    });
  }

  function capitalizeWords(str) {
    return str
      .split(' ') // Split the string into words
      .map(word => word.charAt(0).toUpperCase() + word.slice(1).toLowerCase()) // Capitalize the first letter and make the rest lowercase
      .join(' '); // Join the words back together
  }

  // Load centers and their filial counts
  function loadCenters() {
    ajaxRequest(
      '/api/get-centers/',
      'GET',
      null,
      function(response) {
        const centersContainer = $('#all-centers');
        console.log(response)
        centersContainer.empty();

        if (response.success) {
  if (response.data.length > 0) {
  response.data.forEach((center) => {
    // Capitalizing the names
    const adminFullName = capitalizeWords(center.admin_full_name);
    const adminFirstName = capitalizeWords(center.admin_first_name);
    const adminLastName = capitalizeWords(center.admin_last_name);
    const adminPhone = center.admin_phone;

    const centerCard = `
      <div class="card p-3 mb-4 shadow-sm border">
        <div class="d-flex justify-content-between align-items-center">
          <h5 class="mb-0 text-primary">${capitalizeWords(center.center_name)}</h5>
          <span class="badge bg-primary">
            Filiallar: ${center.filials_count}
            <a href="/learning/center-detail/${center.center_id}" class="text-light ms-2" title="Filiallarni ko'rish">
              <i class="ti ti-external-link"></i>
            </a>
          </span>
        </div>
        <p class="mt-2"><strong>Markaz rahbari:</strong> ${adminFullName}</p>
        <p class="mt-2"><strong>Markaz rahbari ismi:</strong> ${adminFirstName} ${adminLastName}</p>
        <p class="mb-2"><strong>Telefon:</strong> ${adminPhone}</p>
        <div class="d-flex gap-2">
          <button class="btn btn-sm btn-outline-info d-flex align-items-center gap-1" onclick="viewDetails(${center.center_id})">
            <i class="ti ti-eye"></i> Ko'proq
          </button>
          <button class="btn btn-sm btn-outline-success d-flex align-items-center gap-1" onclick="openAddFilialModal(${center.center_id})">
            <i class="ti ti-plus"></i> Fillial qo'shish
          </button>
        </div>
      </div>
    `;
    centersContainer.append(centerCard);
  });
} else {
    centersContainer.append('<p class="text-muted fs-4">Mavjud o‘quv markazlari yo‘q</p>');
  }

} else {
          toastr.error(response.message || 'Markaz ma‘lumotlarini yuklashda xatolik yuz berdi.', 'Xatolik');
        }


      },
      null
    );
  }

  // View center details
  function viewDetails(centerId) {
    ajaxRequest(
      `/api/get-center-details/${centerId}/`,
      'GET',
      null,
      function(response) {
        if (response.success) {
          const detailsContainer = $('#center-details');
          const center = response.data;

          let filialDetails = '';
          if (center.filials.length > 0) {
            center.filials.forEach((filial) => {
              filialDetails += `
                <div class="card mt-4 p-3 shadow-sm border">
                  <h5 class="text-secondary">${filial.location || 'Joylashuv ko‘rsatilmagan'}</h5>
                  <p><strong>Aloqa:</strong> ${filial.contact || 'Mavjud emas'}</p>
                  <p><strong>Telegram:</strong> ${filial.telegram || 'Mavjud emas'}</p>
                  <div class="d-flex gap-2">
                    <button class="btn btn-sm btn-outline-primary d-flex align-items-center gap-1" onclick="window.location.href='/learning/filial-detail/' + ${filial.id} + '/';">
                        <i class="ti ti-eye"></i> Ko'proq
                    </button>
                  </div>
                </div>`;
            });
          } else {
            filialDetails = '<p class="text-muted">Filiallar mavjud emas</p>';
          }

          detailsContainer.html(`
            <div class="card p-4 mb-4 shadow-sm border">
              <h4 class="text-primary mb-3">${center.center_name}</h4>
              <p><strong>Admin:</strong> ${center.admin_name}</p>
              <p><strong>Telefon:</strong> ${center.admin_phone}</p>
              <p><strong>Filiallar soni:</strong> ${center.filials_count}</p>
              <div>${filialDetails}</div>
            </div>
          `);

          $('html, body').animate({ scrollTop: detailsContainer.offset().top }, 800);
        } else {
          toastr.error(response.message || 'Markaz ma‘lumotlarini yuklashda xatolik yuz berdi.', 'Xatolik');
        }
      },
      null
    );
  }

  // Open Filial Modal
  function openAddFilialModal(centerId) {
    $('#filialCenterId').val(centerId); // Set center ID
    $('#addFilialModal').modal('show'); // Show modal
  }

  // Add new Filial
  $('#addFilialForm').on('submit', function(e) {
    e.preventDefault();

    const centerId = $('#filialCenterId').val();
    const formData = new FormData(this);

    $.ajax({
      url: `/api/add-filial/${centerId}/`,
      type: 'POST',
      headers: { 'X-CSRFToken': $('input[name="csrfmiddlewaretoken"]').val() },
      data: formData,
      processData: false,
      contentType: false,
      success: function(response) {
        if (response.success) {
          toastr.success('Filial muvaffaqiyatli qo‘shildi!', 'Muvaffaqiyat!');
          $('#addFilialModal').modal('hide'); // Hide modal
          loadCenters(); // Reload centers
        } else {
          toastr.error(response.message || 'Filial qo‘shishda xatolik yuz berdi.', 'Xatolik');
        }
      },
      error: function() {
        toastr.error('API so‘rovda xatolik yuz berdi.', 'Xatolik');
      }
    });
  });


  // Expose globally
  window.viewDetails = viewDetails;
  window.openAddFilialModal = (centerId) => console.log(`Adding filial for center ID: ${centerId}`);
  window.openAddFilialModal = openAddFilialModal;

  // Load centers on page load
  loadCenters();
});
