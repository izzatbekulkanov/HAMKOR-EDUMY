// CSRF tokenni olish funksiyasi
function getCSRFToken() {
  const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]');
  return csrfToken ? csrfToken.value : "";
}

document.addEventListener("DOMContentLoaded", () => {
  const addSchoolForm = document.getElementById("addSchoolForm");
  const schoolTable = $("#schoolTable");
  const jsonFileInput = document.getElementById("jsonFileInput");
  const analyzeButton = document.getElementById("analyzeButton");
  const saveButton = document.getElementById("saveButton");
  const progressContainer = document.getElementById("progressContainer");
  const progressBar = document.getElementById("progressBar");
  const resultsContainer = document.getElementById("results");

  let fileData = null;

  // Jadvalni ishga tushirish
  const loadTable = () => {
    schoolTable.DataTable({
      ajax: {
        url: "/api/schools/", // Maktablar ma'lumotlarini olish uchun API
        dataSrc: "",
      },
      columns: [
        { data: "id" },
        { data: "viloyat" },
        { data: "tuman" },
        { data: "maktab_raqami" },
        { data: "sharntoma_raqam" },
        { data: "nomi" },
        {
          data: null,
          render: function (data, type, row) {
            return `<button class="btn btn-danger btn-sm delete-school" data-id="${row.id}">O'chirish</button>`;
          },
        },
      ],
      destroy: true,
    });
  };

  loadTable();

  // Forma orqali yangi maktab qo‘shish
  addSchoolForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    const formData = new FormData(addSchoolForm);

    // CSRF tokenni forma ma'lumotlariga qo‘shish
    const csrfToken = getCSRFToken();
    if (csrfToken) {
      formData.append("csrfmiddlewaretoken", csrfToken);
    }

    const response = await fetch("/api/schools/add/", {
      method: "POST",
      body: formData,
      headers: {
        "X-CSRFToken": csrfToken, // CSRF tokenni so‘rov sarlavhasiga qo'shish
      },
    });

    const result = await response.json();
    if (response.ok) {
      toastr.success("Maktab muvaffaqiyatli qo'shildi!");
      addSchoolForm.reset();
      schoolTable.DataTable().ajax.reload();
    } else {
      toastr.error(result.error || "Xatolik yuz berdi");
    }
  });

  // Maktabni o'chirish
  schoolTable.on("click", ".delete-school", async function () {
    const schoolId = this.getAttribute("data-id");
    if (!confirm("Bu maktabni o‘chirishni xohlaysizmi?")) return;

    const csrfToken = getCSRFToken(); // CSRF tokenni olish

    const response = await fetch(`/api/schools/delete/${schoolId}/`, {
      method: "DELETE",
      headers: {
        "X-CSRFToken": csrfToken, // CSRF tokenni qo'shish
      },
    });

    if (response.ok) {
      toastr.success("Maktab muvaffaqiyatli o'chirildi!");
      schoolTable.DataTable().ajax.reload();
    } else {
      toastr.error("Maktabni o'chirishda xatolik yuz berdi.");
    }
  });

  // JSON fayl orqali tahlil qilish
  analyzeButton.addEventListener("click", async () => {
    const file = jsonFileInput.files[0];
    if (!file) {
      toastr.error("JSON faylni yuklang.");
      return;
    }

    try {
      const reader = new FileReader();
      reader.onload = (e) => {
        try {
          fileData = JSON.parse(e.target.result);

          // Tekshiruv natijalarini ko‘rsatish
          const viloyatlar = new Set(fileData.map((item) => item.viloyat)).size;
          const tumanlar = new Set(fileData.map((item) => item.tuman)).size;
          const maktablar = fileData.length;

          document.getElementById("viloyatlarCount").textContent = viloyatlar;
          document.getElementById("tumanlarCount").textContent = tumanlar;
          document.getElementById("maktablarCount").textContent = maktablar;

          resultsContainer.style.display = "block";
          saveButton.style.display = "block";
        } catch (error) {
          toastr.error("JSON fayl noto‘g‘ri formatda.");
        }
      };
      reader.readAsText(file);
    } catch (error) {
      toastr.error("Faylni o'qishda xatolik yuz berdi.");
    }
  });

  // JSON fayldagi ma'lumotlarni saqlash
  saveButton.addEventListener("click", async () => {
    if (!fileData) {
      toastr.error("Avval JSON faylni tahlil qiling.");
      return;
    }

    progressContainer.style.display = "block";
    progressBar.style.width = "0%";
    progressBar.textContent = "0%";

    try {
      const csrfToken = getCSRFToken();
      const response = await fetch("/api/schools/bulk-add/", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": csrfToken,
        },
        body: JSON.stringify(fileData),
      });

      if (response.ok) {
        const reader = response.body.getReader();
        let receivedLength = 0;
        const contentLength = +response.headers.get("Content-Length");
        schoolTable.DataTable().ajax.reload();
        while (true) {
          const { done, value } = await reader.read();
          if (done) break;
          receivedLength += value.length;
          const progress = Math.round((receivedLength / contentLength) * 100);
          progressBar.style.width = `${progress}%`;
          progressBar.textContent = `${progress}%`;
        }

        toastr.success("Maktablar muvaffaqiyatli saqlandi.");
      } else {
        toastr.error("Saqlashda xatolik yuz berdi.");
      }
    } catch (error) {
      toastr.error("Server bilan bog'lanishda xatolik yuz berdi.");
    } finally {
      progressContainer.style.display = "none";
    }
  });
});
