$(document).ready(function() {
  const apiEndpoints = {
    kasblar: '/api/kasblar/',
    yonalishlar: '/api/filter-yonalishlar/',
    kurslar: '/api/filter-kurslar/',
    groups: '/api/groups/'
  };

  const selects = {
    kasb: $('#kasbSelect'),
    yonalish: $('#yonalishSelect'),
    kurs: $('#kursSelect')
  };

  const groupsList = $('#groupsList');
  const totalGroupsCount = $('#totalGroupsCount');

  // Function to handle errors
  const handleError = () => toastr.error('Ma\'lumotlarni yuklashda xatolik yuz berdi.', 'Xatolik');

  // Function to format select options
  const formatOption = (option) => {
    if (!option.id) return option.text;
    const additionalInfo = option.element.getAttribute('data-yonalish') || option.element.getAttribute('data-kurs') || option.element.getAttribute('data-narxi');
    return $(`<span><strong>${option.text}</strong><br><small class="text-muted">${additionalInfo ? `(${additionalInfo})` : ''}</small></span>`);
  };

  const formatSelection = (option) => option.text;

  // Load select options
  const loadSelectOptions = (url, select, templateKey, params = {}) => {
    select.empty().append('<option value="" disabled selected>Tanlang</option>').prop('disabled', true);
    $.ajax({
      url,
      type: 'GET',
      data: params,
      success: (response) => {
        if (response.success && response.data.length > 0) {
          response.data.forEach((item) => {
            select.append(`<option value="${item.id}" data-${templateKey}="${item[`${templateKey}_count`] || item.narxi}">${item.nomi}</option>`);
          });
          select.prop('disabled', false).select2({ templateResult: formatOption, templateSelection: formatSelection });
        }
      },
      error: handleError
    });
  };

// Map for translating weekdays to Uzbek
  const weekDaysUzbek = {
    Monday: 'Dushanba',
    Tuesday: 'Seshanba',
    Wednesday: 'Chorshanba',
    Thursday: 'Payshanba',
    Friday: 'Juma',
    Saturday: 'Shanba',
    Sunday: 'Yakshanba'
  };

// Load groups
  const loadGroups = () => {
    groupsList.empty();
    $.ajax({
      url: apiEndpoints.groups,
      type: 'GET',
      success: (response) => {
        if (response.success && response.data.length > 0) {
          totalGroupsCount.text(response.data.length);
          response.data.forEach((group, index) => {
            groupsList.append(`
            <div class="col-12">
              <div class="card border-0 shadow-sm mb-2">
                <div class="card-body d-flex justify-content-between align-items-center">
                  <div>
                    <h6 class="fw-bold text-primary mb-1">
                      <i class="ti ti-users"></i> ${group.group_name}
                    </h6>
                    <p class="mb-0 small">
                      <strong>Kurs:</strong> ${group.kurs.nomi},
                      <strong>Narxi:</strong> ${group.kurs.narxi.toLocaleString('uz-UZ')} so'm
                    </p>
                    <p class="mb-0 small">
                      <strong>Dars kunlari:</strong> ${group.days_of_week
              .map((day) => weekDaysUzbek[day])
              .join(', ')}
                    </p>
                  </div>
                  <div>
                    <button
                      class="btn btn-sm btn-outline-primary"
                      data-bs-toggle="collapse"
                      data-bs-target="#groupDetails${index}"
                    >
                      <i class="ti ti-eye"></i>
                    </button>
                  </div>
                </div>
                <div class="collapse" id="groupDetails${index}">
                  <div class="card-footer bg-light p-2">
                    <p class="mb-0 small">
                      <strong>Yo'nalish:</strong> ${group.yonalish.nomi},
                      <strong>Kasb:</strong> ${group.kasb.nomi}
                    </p>
                    <p class="mb-0 small text-muted">
                      <strong>Yaratilgan:</strong> ${group.created_at},
                      <strong>Yangilangan:</strong> ${group.updated_at}
                    </p>
                  </div>
                </div>
              </div>
            </div>
          `);
          });
        } else {
          totalGroupsCount.text(0);
          groupsList.append('<div class="col-12 text-center text-muted">Guruhlar mavjud emas.</div>');
        }
      },
      error: handleError
    });
  };

  // Add group
  $('#addGroupForm').on('submit', function(e) {
    e.preventDefault();
    const formData = $(this).serializeArray();
    formData.push({
      name: 'days_of_week',
      value: $('input[name="days_of_week"]:checked').map(function() {
        return $(this).val();
      }).get()
    });

    $.ajax({
      url: apiEndpoints.groups,
      type: 'POST',
      data: JSON.stringify(Object.fromEntries(formData.map((item) => [item.name, item.value]))),
      contentType: 'application/json',
      headers: { 'X-CSRFToken': $('input[name="csrfmiddlewaretoken"]').val() },
      success: (response) => {
        if (response.success) {
          toastr.success('Guruh muvaffaqiyatli qo\'shildi!', 'Muvaffaqiyat');
          $('#addGroupForm')[0].reset();
          loadGroups();
        } else {
          toastr.error(response.message || 'Guruh qo\'shishda xatolik yuz berdi.', 'Xatolik');
        }
      },
      error: handleError
    });
  });

  // Event handlers for selects
  selects.kasb.on('change', function() {
    loadSelectOptions(`${apiEndpoints.yonalishlar}?kasb_id=${$(this).val()}`, selects.yonalish, 'kurs');
    selects.kurs.empty().append('<option value="" disabled selected>Kursni tanlang</option>').prop('disabled', true);
  });

  selects.yonalish.on('change', function() {
    loadSelectOptions(`${apiEndpoints.kurslar}?yonalish_id=${$(this).val()}`, selects.kurs, 'narxi');
  });

  // Initialize
  loadSelectOptions(apiEndpoints.kasblar, selects.kasb, 'yonalish');
  loadGroups();
});
