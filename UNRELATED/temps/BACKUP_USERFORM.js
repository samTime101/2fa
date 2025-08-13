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
statusBox.innerText = `${result.status} [${result.name}]`;
alert(`Detected user: ${result.name}\nStatus: ${result.status}`);

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



        // const result = await response.json();
        // statusBox.innerText = `${result.status} [${result.name}]`;
        // alert(`Detected user: ${result.name}\nStatus: ${result.status}`);
      } catch (err) {
        console.error(err);
        statusBox.innerText = "Failed to connect to backend.";
      }
    });