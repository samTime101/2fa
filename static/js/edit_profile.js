document.getElementById('changeEmailForm').addEventListener('submit', async function(e) {
    e.preventDefault();
    const newEmail = document.getElementById('newEmail').value;
    const response = await fetch('/user/edit_profile', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({ email: newEmail })
    });
    const result = await response.json();
    const status = document.querySelector('#email-status');
    if (result.success) {
        document.getElementById('email').innerText = `Email: ${result.email}`;
        status.innerText = 'Email updated successfully!';
    } else {
        status.innerText = result.error;
    }
});
document.getElementById('changePhotoForm').addEventListener('submit', async function(e) {
    e.preventDefault();
    const status = document.getElementById('modal-photo-status');
    status.innerHTML = `<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>`;
    const fileInput = document.getElementById('modalPhotoInput');
    const file = fileInput.files[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onload = async function() {
        const response = await fetch('/user/edit_profile', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ photo: reader.result })
        });
        const result = await response.json();
        if (result.success) {
            document.getElementById('preview').src = reader.result;
            status.innerText = 'Photo updated successfully!';
        } else {
            status.innerText = result.error;
        }
    };
    reader.readAsDataURL(file);
});
