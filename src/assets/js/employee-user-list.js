/**
 * Page User List
 */

'use strict';

$(function() {
  const dt_user_table = $('.datatables-users'),
    select2 = $('.select2'),
    statusObj = {
      true: { title: 'Active', class: 'bg-label-success' },
      false: { title: 'Inactive', class: 'bg-label-secondary' }
    };

  let borderColor, bodyBg, headingColor;

  if (isDarkStyle) {
    borderColor = config.colors_dark.borderColor;
    bodyBg = config.colors_dark.bodyBg;
    headingColor = config.colors_dark.headingColor;
  } else {
    borderColor = config.colors.borderColor;
    bodyBg = config.colors.bodyBg;
    headingColor = config.colors.headingColor;
  }

  if (select2.length) {
    const $this = select2;
    $this.wrap('<div class="position-relative"></div>').select2({
      placeholder: 'Select Country',
      dropdownParent: $this.parent()
    });
  }

  // Initialize DataTable
  if (dt_user_table.length) {
    dt_user_table.DataTable({
      ajax: {
        url: '/api/employees',
        type: 'GET',
        dataSrc: 'data'
      },
      columns: [
        { data: null },  // Tartib raqami uchun ustun
        { data: 'email' },
        { data: 'full_name' },
        { data: 'combined_info' },
        { data: 'is_active' },
        { data: 'last_login' },
        { data: null }  // Amallar uchun ustun
      ],
      columnDefs: [
        {
          // Tartib raqami ustuni
          targets: 0,
          orderable: false,
          searchable: false,
          render: function(data, type, row, meta) {
            return meta.row + 1; // 1 dan boshlab tartib raqami chiqaradi
          }
        },
        {
          // Email va Username bir ustunda
          targets: 1,
          render: function(data, type, full) {
            return `<div><strong>Email:</strong> ${full.email}<br><strong>Username:</strong> ${full.username}</div>`;
          }
        },
        {
          // Faoliyat holati
          targets: 4,
          render: function(data) {
            const status = statusObj[data] || { title: 'Unknown', class: 'bg-label-default' };
            return `<span class="badge ${status.class}">${status.title}</span>`;
          }
        },
        {
          // Oxirgi kirish
          targets: 5,
          render: function(data) {
            return data ? moment(data).format('YYYY-MM-DD HH:mm:ss') : 'N/A';
          }
        },
        {
          // Amallar
          targets: -1,
          title: 'Actions',
          orderable: false,
          render: function(data, type, full) {
            return (
              `<a href="/users/user/view/account/${full.id}" class="btn btn-icon btn-text-secondary"><i class="ti ti-eye ti-md"></i></a>`
            );
          }
        }
      ],
      responsive: true,
      dom:
        '<"row"' +
        '<"col-md-2"<"ms-n2"l>>' +
        '<"col-md-10"<"dt-action-buttons text-xl-end text-lg-start text-md-end text-start d-flex align-items-center justify-content-end flex-md-row flex-column mb-6 mb-md-0 mt-n6 mt-md-0"fB>>' +
        '>t' +
        '<"row"' +
        '<"col-sm-12 col-md-6"i>' +
        '<"col-sm-12 col-md-6"p>' +
        '>',
      language: {
        sLengthMenu: '_MENU_',
        search: '',
        searchPlaceholder: 'Search User',
        paginate: {
          next: '<i class="ti ti-chevron-right ti-sm"></i>',
          previous: '<i class="ti ti-chevron-left ti-sm"></i>'
        }
      },
      // Export Buttons
      buttons: [
        {
          extend: 'collection',
          className: 'btn btn-label-secondary dropdown-toggle mx-4 waves-effect waves-light',
          text: '<i class="ti ti-upload me-2 ti-xs"></i>Yuklash',
          buttons: ['print', 'csv', 'excel', 'pdf', 'copy']
        }
      ],
      initComplete: function() {
        // Adding filters after table initialization
        this.api().columns(4).every(function() {  // Status ustuni uchun
          const column = this;
          const select = $(
            '<select id="UserStatus" class="form-select text-capitalize"><option value="">Statusni tanlang</option></select>'
          ).appendTo('.user_status').on('change', function() {
            const val = $.fn.dataTable.util.escapeRegex($(this).val());
            column.search(val ? '^' + val + '$' : '', true, false).draw();
          });

          // Unique status qiymatlarini qo'shish
          column.data().unique().sort().each(function(d) {
            const statusTitle = statusObj[d] ? statusObj[d].title : d;  // Agar mavjud bo'lsa statusObj'dan nomi olish
            select.append('<option value="' + d + '">' + statusTitle + '</option>');
          });
        });
      }
    });
  }


});
