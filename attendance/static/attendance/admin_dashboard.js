/**
 * admin_dashboard.js
 * Pure JavaScript - Handles Geofencing and Live Scan Updates
 */

// 1. Capture Laptop Location and Submit Form
function getLaptopLocation() {
  const form = document.getElementById("qrForm");

  if (navigator.geolocation) {
    const options = {
      enableHighAccuracy: true,
      timeout: 10000,
      maximumAge: 0,
    };

    navigator.geolocation.getCurrentPosition(
      (position) => {
        // These IDs must match the hidden inputs in your HTML form
        document.getElementById("admin_lat").value = position.coords.latitude;
        document.getElementById("admin_long").value = position.coords.longitude;

        console.log(
          "Laptop Location Captured:",
          position.coords.latitude,
          position.coords.longitude,
        );
        form.submit();
      },
      (error) => {
        alert(
          "Error: Location access is required to secure the QR code. Please enable GPS.",
        );
      },
      options,
    );
  } else {
    alert("Geolocation is not supported by your browser.");
  }
}

// 2. Live Update Logic
function fetchRecentScans(sessionId) {
  if (!sessionId) {
    console.log("No active session ID found to poll scans.");
    return;
  }

  fetch(`/get-live-scans/${sessionId}/`)
    .then((response) => response.json())
    .then((data) => {
      const listContainer = document.querySelector(".scan-list");
      const countBadge = document.querySelector(".total-count");

      // Update the total count badge if it exists
      if (countBadge) countBadge.innerText = `Total: ${data.students.length}`;

      if (listContainer) {
        // If no students have scanned yet
        if (data.students.length === 0) {
          listContainer.innerHTML =
            '<p class="text-center text-gray-400 py-4">Waiting for scans...</p>';
          return;
        }

        listContainer.innerHTML = "";
        data.students.forEach((student) => {
          listContainer.innerHTML += `
                        <div class="student-card flex items-center gap-4 p-3 border-b border-gray-100">
                            <div class="avatar bg-blue-100 text-blue-600 w-10 h-10 rounded-full flex items-center justify-center font-bold">
                                ${student.name.charAt(0).toUpperCase()}
                            </div>
                            <div class="details flex-1">
                                <strong class="block text-gray-800">${student.name}</strong>
                                <small class="text-gray-500 text-xs uppercase">ID: #STU-${student.id}</small>
                            </div>
                            <div class="time-status text-xs font-semibold text-green-500 bg-green-50 px-2 py-1 rounded">
                                ${student.time || "Present"}
                            </div>
                        </div>
                    `;
        });
      }
    })
    .catch((err) => console.error("Update Error:", err));
}

document.addEventListener("DOMContentLoaded", function () {
  // Check if the variable from our HTML exists and is a valid ID
  if (
    typeof activeSessionId !== "undefined" &&
    activeSessionId !== "None" &&
    activeSessionId !== ""
  ) {
    // 1. Initial fetch (so we don't wait 3 seconds for the first load)
    fetchRecentScans(activeSessionId);

    // 2. Start the 3-second update loop
    setInterval(() => fetchRecentScans(activeSessionId), 3000);

    console.log("Attendance polling started for Session:", activeSessionId);
  } else {
    console.log("No active session detected. Polling skipped.");
  }
});

// Toggle Modal Visibility
function toggleModal(show) {
  const modal = document.getElementById("manualModal");
  modal.classList.toggle("hidden", !show);
}

function submitManualEntry() {
  const studentSelect = document.getElementById("manualStudentId");
  const studentId = studentSelect ? studentSelect.value : "";

  if (!studentId) {
    alert("Please select a student first.");
    return;
  }

  if (
    typeof activeSessionId === "undefined" ||
    activeSessionId === "None" ||
    activeSessionId === ""
  ) {
    alert("No active session found. Please start a session first.");
    return;
  }

  fetch("/mark-manual-attendance/", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-CSRFToken": getCookie("csrftoken"),
    },
    body: JSON.stringify({
      student_id: studentId,
      session_id: activeSessionId,
    }),
  })
    .then((response) => response.json())
    .then((data) => {
      if (data.status === "success") {
        studentSelect.value = "";
        toggleModal(false);

        fetchRecentScans(activeSessionId);
        console.log("Student marked present manually.");
      } else {
        alert("Error: " + data.message);
      }
    })
    .catch((err) => console.error("Manual Entry Error:", err));
}

function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== "") {
    const cookies = document.cookie.split(";");
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim();
      if (cookie.substring(0, name.length + 1) === name + "=") {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}
