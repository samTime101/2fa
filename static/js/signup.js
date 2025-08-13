
    let base64Photo = "";
    const photoInput = document.getElementById("photo");
    const preview = document.getElementById("preview");
    const video = document.getElementById("video");
    const startCameraBtn = document.getElementById("startCamera");
    const captureBtn = document.getElementById("captureBtn");

    photoInput.addEventListener("change", function () {
      const file = this.files[0];
      if (file) {
        const reader = new FileReader();
        reader.onload = function (e) {
          base64Photo = e.target.result.split(',')[1];
          preview.src = e.target.result;
          preview.style.display = "block";
          video.style.display = "none";
                document.getElementById('detect').style.display = 'block'

        };
        reader.readAsDataURL(file);
      }
    });

    startCameraBtn.addEventListener("click", async function () {
      try {
        const stream = await navigator.mediaDevices.getUserMedia({ video: true });
        video.srcObject = stream;
        video.style.display = "block";
        captureBtn.style.display = "block";
        preview.style.display = "none";
        base64Photo = ""; 
      } catch (err) {
        alert("Camera access denied.");
        console.error(err);
      }
    });

    captureBtn.addEventListener("click", function () {
      const canvas = document.createElement("canvas");
      canvas.width = video.videoWidth;
      canvas.height = video.videoHeight;
      const ctx = canvas.getContext("2d");
      ctx.drawImage(video, 0, 0);
      const dataURL = canvas.toDataURL("image/png");
      base64Photo = dataURL.split(',')[1];
      preview.src = dataURL;
      preview.style.display = "block";
      document.getElementById('detect').style.display = 'block'
    });

    document.getElementById('userForm').addEventListener('submit', async function (e ) {
      e.preventDefault();
      document.getElementById('status').innerHTML = `<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> `;
      const username = document.getElementById('username').value;
      const secret_code = document.getElementById('secret').value;
      const email = document.getElementById('Email').value; 

      if (!username || !secret_code || !email) {
        document.getElementById('status').innerText = "Please fill in all fields.";
        return;
      }
      const sanitizedUsername = username.split(' ').join('').toLowerCase();

      if (!base64Photo) {
        document.getElementById('status').innerText = "Please select or capture a photo.";
        return;
      }

      try {
        console.log("Sending data to server...");
        const response = await fetch(`/signup`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            username : sanitizedUsername,
            secret:secret_code,
            email:email,
            photo: base64Photo
          })
        });

        const result = await response.json();
        console.log(result)
  if (result.success) {
    document.getElementById('status').innerText = result.success;
    window.location.href = "/login";
  } else {
    document.getElementById('status').innerText = result.error || "error occured";
  }
      } catch (err) {
        document.getElementById('status').innerText = "server connection error";
        console.error(err);
      }
    });