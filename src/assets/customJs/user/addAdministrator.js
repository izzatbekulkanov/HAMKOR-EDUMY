'use strict';

// Administratorlarni ko'rsatish uchun DataTable sozlamalari
$(document).ready(function() {

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

  var dt_admins_table = $('.datatables-administrators');

  if (dt_admins_table.length) {
    var dt_administrators = dt_admins_table.DataTable({
      processing: true,
      serverSide: true,
      paging: false, // Paginationni o‘chirib tashlash
      info: false, // "Ko‘rsatilmoqda _START_ dan _END_" matnini olib tashlash
      ajax: {
        url: '/api/get-ceo-administrators/', // API endpoint
        type: 'GET',
        data: function(d) {
          d.searchName = $('#search-name').val(); // Ism bo‘yicha qidirish
          d.filterGender = $('#filter-gender').val(); // Jinsi bo‘yicha filtr
          d.filterStatus = $('#filter-status').val(); // Faollik holati bo‘yicha filtr
        }
      },
      columns: [
        {
          data: null,
          title: '#',
          render: function(data, type, row, meta) {
            return meta.row + 1; // Tartib raqami
          }
        },
        {
          data: null,
          title: 'Foydalanuvchi',
          render: function(data) {
            return `
              <div>
                <strong>${data.first_name || ''} ${data.second_name || ''}</strong><br>
                <small>Foydalanuvchi nomi: ${data.username || '<span class="text-muted">Mavjud emas</span>'}</small><br>
                <small>Email: ${data.email || '<span class="text-muted">Mavjud emas</span>'}</small>
              </div>`;
          }
        },
        { data: 'phone_number', title: 'Telefon raqami', defaultContent: '<span class="text-muted">Noma’lum</span>' },
        { data: 'birth_date', title: 'Tug‘ilgan sanasi', defaultContent: '<span class="text-muted">Noma’lum</span>' },
        {
          data: 'gender__name',
          title: 'Jinsi',
          render: function(data) {
            return data ? data : '<span class="text-muted">Noma’lum</span>';
          }
        },
        {
          data: 'is_active',
          title: 'Faollik holati',
          render: function(data, type, full) {
            return `
              <label class="switch switch-primary">
                <input type="checkbox" class="switch-input is-active-toggle" data-id="${full.id}" ${data ? 'checked' : ''}>
                <span class="switch-toggle-slider"></span>
              </label>`;
          }
        },
        { data: 'now_role', title: 'Hozirgi roli', defaultContent: '<span class="text-muted">Noma’lum</span>' },
        {
          data: 'last_login',
          title: 'Oxirgi kirish',
          render: function(data) {
            return data ? data : '<span class="text-muted">Mavjud emas</span>';
          }
        },
        {
          data: 'id',
          orderable: false,
          title: 'Amallar',
          render: function(data) {
            return `
              <div class="d-inline-block">
                <button class="btn btn-sm btn-icon btn-primary me-1 view-details" data-id="${data}" title="Ko‘rish">
                  <i class="ti ti-eye"></i>
                </button>
                <button class="btn btn-sm btn-icon btn-danger delete-record" data-id="${data}" title="O‘chirish">
                  <i class="ti ti-trash"></i>
                </button>
              </div>`;
          }
        }
      ],
      order: [[1, 'asc']], // Foydalanuvchi ismi bo‘yicha tartiblash
      language: {
        zeroRecords: 'Hech qanday ma’lumot topilmadi'
      },
      dom: '<"d-flex justify-content-between align-items-center mb-4"B>t', // Faqat jadval va tugmalar
      buttons: [
        {
          text: '<i class="ti ti-plus me-0 me-sm-1 ti-xs"></i><span class="d-none d-sm-inline-block">Yangi Admin Qo‘shish</span>',
          className: 'btn btn-primary ms-2 ms-sm-0 waves-effect waves-light',
          action: function() {
            window.location.href = '/user/addAdministrators/'; // Yangi administrator qo'shish sahifasiga yo'naltirish
          }
        }
      ]
    });

    // Filtrlarni qo‘llash
    $('#filter-gender, #filter-status').on('change', function() {
      dt_administrators.draw();
    });

    // Ko‘rish tugmachasi
    dt_admins_table.on('click', '.view-details', function() {
      var adminId = $(this).data('id');
      alert('Administrator ID: ' + adminId);
    });

    // O‘chirish tugmachasi
    dt_admins_table.on('click', '.delete-record', function() {
      var adminId = $(this).data('id');
      if (confirm('Ushbu administratorni o‘chirishni xohlaysizmi?')) {
        $.ajax({
          url: `/api/delete-administrator/${adminId}/`,
          type: 'DELETE',
          success: function(response) {
            alert(response.message);
            dt_administrators.ajax.reload();
          },
          error: function() {
            alert('O‘chirishda xatolik yuz berdi.');
          }
        });
      }
    });

    // Faollik holatini o'zgartirish
    dt_admins_table.on('change', '.is-active-toggle', function() {
      var adminId = $(this).data('id');
      var isActive = $(this).is(':checked');
      $.ajax({
        url: `/api/update-activity/${adminId}/`,
        type: 'POST',
        headers: { 'X-CSRFToken': $('input[name="csrfmiddlewaretoken"]').val() }, // CSRF tokenni yuborish
        contentType: 'application/json', // JSON formatda ma'lumot yuboriladi
        data: JSON.stringify({ is_active: isActive }), // JSON ma'lumotni yuborish
        success: function () {
          toastr.success('Faollik holati muvaffaqiyatli o‘zgartirildi!', 'Yangilandi');
        },
        error: function () {
          toastr.error('Xatolik yuz berdi.', 'Yangilashda xatolik');
        }
      });
    });
  }
});
