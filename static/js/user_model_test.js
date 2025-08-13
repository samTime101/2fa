// UPLOADED FOR TESTING





// ----------------------------------------------------------------
const video = document.getElementById('video');
const canvas = document.getElementById('canvas');
const captureButton = document.getElementById('capture');
// const uploadInput = document.getElementById('upload');
const resultDiv = document.getElementById('result');

navigator.mediaDevices.getUserMedia({ video: true })
.then(stream => {
    video.srcObject = stream;
})
.catch(err => {
    console.error("webcam access error", err);
    resultDiv.innerText = "webcam access error , upload image";
});
captureButton.addEventListener('click', async () => {
    resultDiv.innerText = 'Processing...';
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;

    canvas.getContext('2d').drawImage(video, 0, 0);

    const base64Photo = canvas.toDataURL('image/png').split(',')[1];

    try {
        console.log("Sending data to server...");
        const response = await fetch(`/recognize`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ photo: base64Photo })
        });

        const data = await response.json();
        if (data.name) {
            resultDiv.innerText = `Recognized: ${data.name}`;
        } else {
            resultDiv.innerText = 'No match found';
        }
    } catch (err) {
        console.error(err);
        resultDiv.innerText = 'Error: ' + err.message;
    }
});




// AAILE LAI KAM CHAIDAINA

// uploadInput.addEventListener('change', () => {
//     const formData = new FormData();
//     formData.append('file', uploadInput.files[0]);
//     sendImage(formData);
// });

