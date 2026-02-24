let html5QrScanner;

function launchScanner() {
  const container = document.getElementById("reader-container");

  container.style.display = "flex";

  if (navigator.geolocation) {
    navigator.geolocation.getCurrentPosition(
      (position) => {
        const lat = position.coords.latitude;
        const lon = position.coords.longitude;

        startCamera(lat, lon);
      },
      (err) => {
        alert("GPS needed to verify you are in the classroom.");
        container.style.display = "none";
      },
    );
  }
}

function startCamera(lat, lon) {
  const html5QrScanner = new Html5Qrcode("reader");
  html5QrScanner
    .start(
      { facingMode: "environment" },
      { fps: 10, qrbox: 250 },
      (decodedText) => {
        submitAttendance(decodedText, lat, lon);
        html5QrScanner.stop();
        document.getElementById("reader-container").style.display = "none";
      },
    )
    .catch((err) => {
      console.error("Camera Error:", err);
      alert("Camera failed. Check permissions.");
    });
}

function openScannerModal(lat, lon) {
  if (html5QrScanner) {
    html5QrScanner.clear();
  }

  html5QrScanner = new Html5Qrcode("reader");

  const config = {
    fps: 15,
    qrbox: { width: 250, height: 250 },
    aspectRatio: 1.0,
  };

  html5QrScanner
    .start({ facingMode: "environment" }, config, (decodedText) => {
      if (navigator.vibrate) navigator.vibrate(100);

      submitAttendance(decodedText, lat, lon);

      html5QrScanner.stop().then(() => {
        document.getElementById("reader-container").style.display = "none";
      });
    })
    .catch((err) => {
      console.error("Scanner Error:", err);
      alert("Camera failed to start. Please refresh.");
    });
}

function submitAttendance(token, lat, lon) {
  fetch("/submit-attendance/", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-CSRFToken": getCookie("csrftoken"),
    },
    body: JSON.stringify({
      token: token,
      student_lat: lat,
      student_long: lon,
    }),
  })
    .then((response) => response.json())
    .then((data) => {
      if (data.status === "success") {
        alert("Attendance Marked Successfully!");
        location.reload();
      } else {
        alert("Error: " + data.message);
        html5QrScanner.stop();
      }
    });
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
