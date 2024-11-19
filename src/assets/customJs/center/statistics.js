document.addEventListener("DOMContentLoaded", () => {
  const apiEndpoint = "/api/statistics/";
  const totalBranches = document.getElementById("totalBranches");
  const totalProfessions = document.getElementById("totalProfessions");
  const totalCourses = document.getElementById("totalCourses");
  const totalGroups = document.getElementById("totalGroups");

  // List Containers
  const branchLocations = document.getElementById("branchLocations");
  const professionFieldList = document.getElementById("professionFieldList");
  const activeGroupsList = document.getElementById("activeGroupsList");

  // Charts
  const branchGrowthChartCtx = document.getElementById("branchGrowthChart").getContext("2d");
  const professionDistributionChartCtx = document.getElementById("professionDistributionChart").getContext("2d");
  const weeklyScheduleChartCtx = document.getElementById("weeklyScheduleChart").getContext("2d");
  const courseRevenueChartCtx = document.getElementById("courseRevenueChart").getContext("2d");

  let branchGrowthChart, professionDistributionChart, weeklyScheduleChart, courseRevenueChart;

  // Fetch data from API
  fetch(apiEndpoint)
    .then((response) => response.json())
    .then((data) => {
      if (data.success) {
        const stats = data.data;

        // Update key statistics
        totalBranches.textContent = stats.branches.total;
        totalProfessions.textContent = stats.professions.total;
        totalCourses.textContent = stats.courses.total;
        totalGroups.textContent = stats.groups.total;

        // Populate branch locations
        branchLocations.innerHTML = stats.branches.locations
          .map(
            (branch) =>
              `<li class="list-group-item">
                <strong>${branch.location}</strong> - Contact: ${branch.contact}, Telegram: ${branch.telegram}
              </li>`
          )
          .join("");

        // Populate profession-field list
        professionFieldList.innerHTML = stats.fields.kasb_distribution
          .map(
            (field) =>
              `<li class="list-group-item">
                <strong>${field.kasb__nomi}</strong> - Yo'nalishlar soni: ${field.count}
              </li>`
          )
          .join("");

        // Populate active groups
        activeGroupsList.innerHTML = stats.groups.recent_groups
          .map(
            (group) =>
              `<li class="list-group-item">
                <strong>${group.group_name}</strong> - Kurs: ${group.kurs__nomi}, Faolmi: ${group.is_active ? "Ha" : "Yo'q"}
              </li>`
          )
          .join("");

        // Initialize Branch Growth Chart
        if (branchGrowthChart) branchGrowthChart.destroy();
        branchGrowthChart = new Chart(branchGrowthChartCtx, {
          type: "line",
          data: {
            labels: ["Oxirgi yil", "Oxirgi oy", "Bugun"],
            datasets: [
              {
                label: "Filiallar",
                data: [stats.branches.last_year, stats.branches.last_month, stats.branches.today],
                borderColor: "rgba(75, 192, 192, 1)",
                fill: false,
              },
            ],
          },
        });

        // Initialize Profession Distribution Chart
        if (professionDistributionChart) professionDistributionChart.destroy();
        professionDistributionChart = new Chart(professionDistributionChartCtx, {
          type: "pie",
          data: {
            labels: stats.fields.kasb_distribution.map((item) => item.kasb__nomi),
            datasets: [
              {
                data: stats.fields.kasb_distribution.map((item) => item.count),
                backgroundColor: ["#4caf50", "#ff9800", "#f44336", "#2196f3", "#9c27b0"],
              },
            ],
          },
        });

        // Initialize Weekly Schedule Chart
        if (weeklyScheduleChart) weeklyScheduleChart.destroy();
        weeklyScheduleChart = new Chart(weeklyScheduleChartCtx, {
          type: "bar",
          data: {
            labels: ["Dushanba", "Seshanba", "Chorshanba", "Payshanba", "Juma", "Shanba", "Yakshanba"],
            datasets: [
              {
                label: "Guruhlar soni",
                data: calculateWeeklySchedule(stats.weekly_schedule),
                backgroundColor: "#ff9800",
              },
            ],
          },
        });

        // Initialize Course Revenue Chart
        if (courseRevenueChart) courseRevenueChart.destroy();
        courseRevenueChart = new Chart(courseRevenueChartCtx, {
          type: "doughnut",
          data: {
            labels: stats.courses.recent_courses.map((course) => course.nomi),
            datasets: [
              {
                data: stats.courses.recent_courses.map((course) => course.narxi),
                backgroundColor: ["#f44336", "#4caf50", "#2196f3", "#9c27b0", "#ff9800"],
              },
            ],
          },
        });
      } else {
        toastr.error("Statistikani yuklashda xatolik yuz berdi.", "Xatolik");
      }
    })
    .catch(() => toastr.error("Statistikani yuklashda xatolik yuz berdi.", "Xatolik"));

  // Helper function to calculate weekly schedule counts
  function calculateWeeklySchedule(weeklyData) {
    const weekDays = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"];
    const dayCounts = weekDays.reduce((acc, day) => ({ ...acc, [day]: 0 }), {});

    weeklyData.forEach((group) => {
      group.days_of_week.forEach((day) => {
        if (dayCounts[day] !== undefined) {
          dayCounts[day]++;
        }
      });
    });

    return weekDays.map((day) => dayCounts[day]);
  }
});
