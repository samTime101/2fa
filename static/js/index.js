    // UPDATED ON AUGUST 8
    // AUTO CLICK AND DETECT FREQUENCY
    
    let start_scanning = false;
    let users;
    let detected_person = "";
    let base64Photo = "";
    let detected_frequency = 0;
    let tolerance = 0.0;

    const video = document.getElementById("video");
    const preview = document.getElementById("preview");
    const startCameraBtn = document.getElementById("startCamera");
    const captureBtn = document.getElementById("captureBtn");
    const statusBox = document.getElementById("status");
    const startScanningBtn = document.getElementById("startScanning");
    const liveFreqDisplay = document.getElementById("liveFreq");

    let audioContext, analyser, source, dataArray, audioStream;



    document.addEventListener("DOMContentLoaded", async () => {
      await loadUsers();
            // document.querySelector('.fingerprint').classList.remove ('scanning');

      // statusBox.innerText = "Ready to scan!";
    });
    // ----------------------------------------------------------------------------------
    function smoothScrollTo(element) {
        element.scrollIntoView({ behavior: "smooth", block: "center" });
    }

    // ----------------------------------------------------------------------------------

    async function loadUsers() {
      try {
        const response = await fetch('/users');
        if (!response.ok) throw new Error('fail fail fail');
        users = await response.json();
        console.log("Loaded users:", users);
      } catch (error) {
        console.error("Error loading users:", error);
        statusBox.innerText = "Failed to load user data.";
      }
    }

    // ---------------------------------------------------------------------------------

    // CAMERA WHEN DETECTED
    startCameraBtn.addEventListener("click", async () => {
      smoothScrollTo(video);
      try {
        const stream = await navigator.mediaDevices.getUserMedia({ video: true });
        video.srcObject = stream;
        video.style.display = "block";
        captureBtn.style.display = "block";

      // auto capture
        setTimeout(function() {
        captureBtn.click();
      }, 3000);
      
        // document.getElementById('detect').style.display = 'block'
        preview.style.display = "none";
        base64Photo = "";
      } catch (err) {
        alert("no access camera.");
        console.error(err);
      }
    });

    // ---------------------------------------------------------------------------------

    // PHOTO CAPTURE

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
      smoothScrollTo(statusBox);
      console.log("📷 Captured photo");
      document.getElementById('detect').style.display = 'block'
      //submit userForm
              setTimeout(function() {
        document.getElementById('detect').click();
              }, 2000);

    });

// SUBMISSION --------------------------------------------------------------------------------------
    document.getElementById('userForm').addEventListener('submit', async function (e) {
      e.preventDefault();

      if (!base64Photo) {
        statusBox.innerText = "photo not detected , maybe no frequency !!!!!!!!";
        return;
      }

      statusBox.innerText = "processing....";


      // SENDING POST REQUEST
      try {
        const response = await fetch(`/detect`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            image: base64Photo,
            frequency: detected_frequency
          })
        });
const result = await response.json();

// wait for 3 seconds before resuming scan

console.log("Detection result:", result);
//CHANGED THIS-------------
statusBox.className = 'alert alert-dark text-center';
statusBox.style.display = 'block';
//--------------
statusBox.innerText = `RESULT: ${result.status} [${result.name}]`;
// alert(`Detected user: ${result.name}\nStatus: ${result.status}`);

// ---------------------_ADDED SET TIME OUT
setTimeout( async () => {
  statusBox.classList.remove('alert', 'alert-dark', 'text-center');
if (video.srcObject) {
  video.srcObject.getTracks().forEach(track => track.stop());
  video.srcObject = null;
}
video.style.display = "none";
captureBtn.style.display = "none";
document.getElementById('detect').style.display = 'none'

preview.style.display = "none";
base64Photo = "";

    start_scanning = true;
    startScanningBtn.innerText = "Stop Scanning";
    statusBox.innerText = "Resuming scan...";
    await detect_frequency_continuous();
}, 3000);
// ---------------------WITH ALERT BELOW
// if (video.srcObject) {
//   video.srcObject.getTracks().forEach(track => track.stop());
//   video.srcObject = null;
// }
// video.style.display = "none";
// captureBtn.style.display = "none";
// document.getElementById('detect').style.display = 'none'

// preview.style.display = "none";
// base64Photo = "";

//     start_scanning = true;
//     startScanningBtn.innerText = "Stop Scanning";
//     statusBox.innerText = "Resuming scan...";
//     await detect_frequency_continuous();
      } catch (err) {
        console.error(err);
        statusBox.innerText = "Failed to connect to backend.";
      }
    });


    // ---------------------------------------------------------------------------------

    startScanningBtn.addEventListener("click", async (e) => {
      e.preventDefault();

      if (start_scanning) {
        start_scanning = false;
        statusBox.innerText = "Scanning stopped.";
        liveFreqDisplay.innerText = "";
        startScanningBtn.innerText = "Start Scanning";
        stopAudio();
        return;
      }

      start_scanning = true;
      startScanningBtn.innerText = "Stop Scanning";
      statusBox.innerText = "Starting frequency detection...";
      await detect_frequency_continuous();
    });

    async function detect_frequency_continuous() {
      audioContext = new AudioContext();
      analyser = audioContext.createAnalyser();
      analyser.fftSize = 2048;
      dataArray = new Float32Array(analyser.fftSize);

      try {
        audioStream = await navigator.mediaDevices.getUserMedia({ audio: true });
        source = audioContext.createMediaStreamSource(audioStream);
        source.connect(analyser);
        updateLiveFrequency();

        const checkInterval = setInterval(async () => {
          if (!start_scanning) {
            clearInterval(checkInterval);
            return;
          }

          const valid = await verify_frequency(detected_frequency);
          if (valid) {
            statusBox.innerText = "Frequency detected , potential match :"+detected_person
            startCameraBtn.click();
            start_scanning = false;
            startScanningBtn.innerText = "Start Scanning";
            clearInterval(checkInterval);
            stopAudio();
          }
        }, 1000);
      } catch (err) {
        console.error("Error accessing microphone:", err);
        statusBox.innerText = "Microphone error.";
      }
    }

    function updateLiveFrequency() {
      if (!start_scanning) return;

      analyser.getFloatTimeDomainData(dataArray);
      const frequency = autoCorrelate(dataArray, audioContext.sampleRate);
      if (frequency > 0) {
        detected_frequency = Math.round(frequency);
        liveFreqDisplay.innerText = ` Frequency: ${detected_frequency} Hz`;
      } else {
        liveFreqDisplay.innerText = `Listening...`;
      }

      requestAnimationFrame(updateLiveFrequency);
    }

    function stopAudio() {
      if (audioStream) audioStream.getTracks().forEach(track => track.stop());
      if (audioContext) audioContext.close();
    }

    function autoCorrelate(buf, sampleRate) {
      let SIZE = buf.length;
      let rms = 0;
      for (let i = 0; i < SIZE; i++) rms += buf[i] * buf[i];
      rms = Math.sqrt(rms / SIZE);
      if (rms < 0.01) return -1;

      let r1 = 0, r2 = SIZE - 1, thres = 0.2;
      for (let i = 0; i < SIZE / 2; i++) if (Math.abs(buf[i]) < thres) { r1 = i; break; }
      for (let i = 1; i < SIZE / 2; i++) if (Math.abs(buf[SIZE - i]) < thres) { r2 = SIZE - i; break; }

      buf = buf.slice(r1, r2);
      SIZE = buf.length;

      const c = new Array(SIZE).fill(0);
      for (let i = 0; i < SIZE; i++)
        for (let j = 0; j < SIZE - i; j++)
          c[i] = c[i] + buf[j] * buf[j + i];

      let d = 0;
      while (c[d] > c[d + 1]) d++;
      let maxval = -1, maxpos = -1;
      for (let i = d; i < SIZE; i++) {
        if (c[i] > maxval) {
          maxval = c[i];
          maxpos = i;
        }
      }

      let T0 = maxpos;
      let x1 = c[T0 - 1], x2 = c[T0], x3 = c[T0 + 1];
      let a = (x1 + x3 - 2 * x2) / 2;
      let b = (x3 - x1) / 2;
      if (a) T0 = T0 - b / (2 * a);

      return sampleRate / T0;
    }

    async function generate_dynamic_frequency(user) {
      const now = new Date();
      const minute = now.getUTCMinutes();
      now.setUTCSeconds(0, 0);
      const timestampStr = now.toISOString().split('.')[0] + 'Z';
      const combo = `${user.secret}-${timestampStr}`;
      const hashHex = sha256(combo);
      const hashValue = parseInt(hashHex.slice(-4), 16);
      const bias = hashValue % 20;
      return user.frequency + bias + minute;
    }

    async function verify_frequency(peak_freq) {
      for (const user of users) {
        const expected = await generate_dynamic_frequency(user);
        if (Math.abs(Math.round(peak_freq) - Math.round(expected)) <= tolerance) {
          detected_person = user.name
          console.log("Frequency matched:", user.name);
          return true;
        }
      }
      return false;
    }