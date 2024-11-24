document.addEventListener("DOMContentLoaded", () => {
  const regionSelect = document.getElementById("regionSelect");
  const districtSelect = document.getElementById("districtSelect");
  const schoolSelect = document.getElementById("schoolSelect");
  const addClassForm = document.getElementById("addClassForm");
  const groupedClassesDiv = document.getElementById("groupedClasses");
  const totalClassesElem = document.getElementById("totalClasses");
  const totalSchoolsElem = document.getElementById("totalSchools");

  const resetDropdown = (dropdown, placeholder) => {
    dropdown.innerHTML = `<option value="" disabled selected>${placeholder}</option>`;
    dropdown.disabled = true;
  };

  // Load statistics and update the UI
  const loadStatistics = async () => {
    try {
      const response = await fetch("/api/classes/stats/");
      const data = await response.json();

      if (data.success) {
        totalClassesElem.textContent = data.stats.total_classes || 0;
        totalSchoolsElem.textContent = data.stats.total_schools || 0;
      } else {
        toastr.error("Statistikani yuklashda xatolik yuz berdi.");
      }
    } catch (error) {
      toastr.error("Server bilan bog'lanishda xatolik yuz berdi.");
      console.error("Error loading statistics:", error);
    }
  };

  // Load grouped classes from API
  const loadGroupedClasses = async () => {
    try {
      const response = await fetch("/api/classes/stats/");
      const data = await response.json();

      if (data.success) {
        displayGroupedClasses(data.grouped_classes);
      } else {
        toastr.error("Ma'lumotlarni yuklashda xatolik yuz berdi.");
      }
    } catch (error) {
      toastr.error("Server bilan bog'lanishda xatolik yuz berdi.");
      console.error("Error loading grouped classes:", error);
    }
  };

  // Display grouped classes
  const displayGroupedClasses = (groupedData) => {
    groupedClassesDiv.innerHTML = "";

    for (const [viloyat, tumans] of Object.entries(groupedData)) {
      const regionDiv = document.createElement("div");
      regionDiv.className = "mt-4";
      regionDiv.innerHTML = `<h5 class="text-primary">${viloyat}</h5>`;

      for (const [tuman, schools] of Object.entries(tumans)) {
        const districtDiv = document.createElement("div");
        districtDiv.className = "mt-2";
        districtDiv.innerHTML = `<h6>${tuman}</h6>`;

        const schoolList = document.createElement("ul");
        schoolList.className = "list-group";

        schools.forEach((school) => {
          const schoolItem = document.createElement("li");
          schoolItem.className = "list-group-item";
          schoolItem.textContent = `${school.nomi} (${school.class_count} sinf)`;
          schoolList.appendChild(schoolItem);
        });

        districtDiv.appendChild(schoolList);
        regionDiv.appendChild(districtDiv);
      }

      groupedClassesDiv.appendChild(regionDiv);
    }
  };

  // Load regions (viloyatlar)
  const loadRegions = async () => {
    try {
      const response = await fetch("/api/schools/grouped/");
      const data = await response.json();

      if (data.data) {
        for (const viloyat in data.data) {
          const option = document.createElement("option");
          option.value = viloyat;
          option.textContent = viloyat;
          regionSelect.appendChild(option);
        }
        regionSelect.disabled = false;
      } else {
        toastr.error("Viloyatlar ma'lumotini yuklashda xatolik yuz berdi.");
      }
    } catch (error) {
      console.error("Error loading regions:", error);
      toastr.error("Server bilan bog'lanishda xatolik yuz berdi.");
    }
  };

  // Load districts (tumanlar) based on selected region
  regionSelect.addEventListener("change", () => {
    const selectedRegion = regionSelect.value;
    resetDropdown(districtSelect, "Tuman tanlang");
    resetDropdown(schoolSelect, "Maktabni tanlang");

    if (!selectedRegion) return;

    try {
      fetch("/api/schools/grouped/")
        .then((response) => response.json())
        .then((data) => {
          const districts = data.data[selectedRegion];
          if (districts) {
            for (const tuman in districts) {
              const option = document.createElement("option");
              option.value = tuman;
              option.textContent = tuman;
              districtSelect.appendChild(option);
            }
            districtSelect.disabled = false;
          } else {
            toastr.warning("Tanlangan viloyatda tumanlar topilmadi.");
          }
        });
    } catch (error) {
      console.error("Error loading districts:", error);
      toastr.error("Server bilan bog'lanishda xatolik yuz berdi.");
    }
  });

  // Load schools (maktablar) based on selected district
  districtSelect.addEventListener("change", () => {
    const selectedRegion = regionSelect.value;
    const selectedDistrict = districtSelect.value;
    resetDropdown(schoolSelect, "Maktabni tanlang");

    if (!selectedRegion || !selectedDistrict) return;

    try {
      fetch("/api/schools/grouped/")
        .then((response) => response.json())
        .then((data) => {
          const schools = data.data[selectedRegion][selectedDistrict]?.maktablar;
          if (schools) {
            schools.forEach((school) => {
              const option = document.createElement("option");
              option.value = school.id;
              option.textContent = `${school.maktab_raqami || "No Number"} | ${school.nomi}`;
              schoolSelect.appendChild(option);
            });
            schoolSelect.disabled = false;
          } else {
            toastr.warning("Tanlangan tumanda maktablar topilmadi.");
          }
        });
    } catch (error) {
      console.error("Error loading schools:", error);
      toastr.error("Server bilan bog'lanishda xatolik yuz berdi.");
    }
  });

  // Submit the add class form
  addClassForm.addEventListener("submit", async (e) => {
    e.preventDefault();

    const maktabId = schoolSelect.value;
    const sinfRaqami = document.getElementById("classNumber").value;
    const belgisi = document.getElementById("badgeName").value;

    if (!maktabId || !sinfRaqami) {
      toastr.error("Maktab va sinf raqami majburiy.");
      return;
    }

    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;

    try {
      const response = await fetch("/api/classes/add/", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": csrfToken,
        },
        body: JSON.stringify({
          maktab_id: maktabId,
          sinf_raqami: sinfRaqami,
          belgisi: belgisi || null,
        }),
      });

      const result = await response.json();
      if (response.ok) {
        toastr.success(result.message || "Sinf muvaffaqiyatli qo'shildi.");
        addClassForm.reset();
        resetDropdown(districtSelect, "Tuman tanlang");
        resetDropdown(schoolSelect, "Maktabni tanlang");
        loadStatistics(); // Reload statistics after adding a new class
        loadGroupedClasses(); // Reload grouped classes after adding a new class
      } else {
        toastr.error(result.error || "Xatolik yuz berdi.");
      }
    } catch (error) {
      console.error("Error:", error);
      toastr.error("Server bilan bog'lanishda xatolik yuz berdi.");
    }
  });

  // Initialize dropdowns on page load
  resetDropdown(regionSelect, "Viloyatni tanlang");
  resetDropdown(districtSelect, "Tuman tanlang");
  resetDropdown(schoolSelect, "Maktabni tanlang");

  // Load initial data
  loadRegions();
  loadStatistics();
  loadGroupedClasses();
});
