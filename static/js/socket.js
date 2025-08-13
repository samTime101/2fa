    // const output = document.getElementById('output');
    // const input = document.getElementById('input');
    // const sendButton = document.getElementById('send');
    // const socket = io();

    // socket.on('connect', () => appendMessage('2FA 2025 Connected'));
    // socket.on('message', (msg) => appendMessage(msg));

    // sendButton.onclick = () => {
    //   const text = input.value.trim();
    //   if (text) {
    //     socket.send(text);
    //     input.value = '';
    //   }
    // };

    // input.addEventListener('keypress', (event) => {
    //   if (event.key === 'Enter') sendButton.click();
    // });

    // function appendMessage(message) {
    //   output.textContent += message + '\n';
    //   output.scrollTop = output.scrollHeight;
    // }const output = document.getElementById('output');
const input = document.getElementById('input');
const sendButton = document.getElementById('send');
const socket = io();

let loaderLine = null;

// socket.on('connect', () => appendMessage('2FA 2025 Connected'));
socket.on('message', (msg) => {
  removeLoader();
  appendMessage(msg);
});

sendButton.onclick = () => {
  const text = input.value.trim();
  if (text) {
    socket.send(text);
    input.value = '';
    showLoader();
  }
};

input.addEventListener('keypress', (event) => {
  if (event.key === 'Enter') sendButton.click();
});

function appendMessage(message) {
  output.textContent += message + '\n';
  output.scrollTop = output.scrollHeight;
}



function showLoader() {
  loaderLine = "Waiting for server's response...";
  appendMessage(loaderLine);
}

function removeLoader() {
  if (loaderLine) {
    output.textContent = output.textContent.replace(loaderLine + '\n', '');
    loaderLine = null;
  }
}
