document.addEventListener("DOMContentLoaded", () => {
  const apiEndpoint = {
    schools: "/api/schools/list/",
    addSchool: "/api/schools/add/",
    regionDistrict: "/api/region-district/",
  };

  const addSchoolForm = document.getElementById("addSchoolForm");
  const regionSelect = document.getElementById("regionSelect");
  const districtSelect = document.getElementById("districtSelect");
  const schoolTable = $("#schoolTable").DataTable();

  // Dropdown ma'lumotlarni olish
  const fetchDropdownData = async () => {
    try {
      const response = await fetch(apiEndpoint.regionDistrict);
      const data = await response.json();

      if (data.success) {
        populateRegions(data.regions);
      }
    } catch (error) {
      toastr.error("Dropdown ma'lumotlarni olishda xatolik yuz berdi.", "Xatolik");
    }
  };

  const populateRegions = (regions) => {
    regionSelect.innerHTML = '<option value="" disabled selected>Viloyatni tanlang</option>';
    regions.forEach((region) => {
      regionSelect.innerHTML += `<option value="${region.id}">${region.name}</option>`;
    });
  };

  regionSelect.addEventListener("change", async () => {
    const regionId = regionSelect.value;
    districtSelect.innerHTML = '<option value="" disabled selected>Tuman tanlang</option>';
    districtSelect.disabled = true;

    try {
      const response = await fetch(`${apiEndpoint.regionDistrict}?region=${regionId}`);
      const data = await response.json();

      if (data.success) {
        data.districts.forEach((district) => {
          districtSelect.innerHTML += `<option value="${district.id}">${district.name}</option>`;
        });
        districtSelect.disabled = false;
      }
    } catch (error) {
      toastr.error("Tumanlarni olishda xatolik yuz berdi.", "Xatolik");
    }
  });

  // Formni yuborish
  addSchoolForm.addEventListener("submit", async (e) => {
    e.preventDefault();

    const formData = new FormData(addSchoolForm);

    try {
      const response = await fetch(apiEndpoint.addSchool, {
        method: "POST",
        body: formData,
      });
      const result = await response.json();

      if (result.success) {
        toastr.success(result.message, "Success");
        addSchoolForm.reset();
        loadSchools();
      } else {
        toastr.error(result.message || "Xatolik yuz berdi.", "Xatolik");
      }
    } catch (error) {
      toastr.error("Maktabni qo'shishda xatolik yuz berdi.", "Xatolik");
    }
  });

  // Jadvalni to'ldirish
  const loadSchools = async () => {
    try {
      const response = await fetch(apiEndpoint.schools);
      const data = await response.json();

      if (data.success) {
        schoolTable.clear();
        data.schools.forEach((school, index) => {
          schoolTable.row.add([
            index + 1,
            school.viloyat || "Noma'lum",
            school.tuman || "Noma'lum",
            school.maktab_raqami,
            school.is_active ? "Faol" : "Nofaol",
            school.created_at,
          ]);
        });
        schoolTable.draw();
      }
    } catch (error) {
      toastr.error("Maktablar ro'yxatini olishda xatolik yuz berdi.", "Xatolik");
    }
  };

  fetchDropdownData();
  loadSchools();
});
