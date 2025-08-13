const photoInput = document.getElementById('photoInput');
    const preview = document.getElementById('preview');
    const form = document.getElementById('editProfileForm');
    const statusDiv = document.getElementById('status');

    photoInput.addEventListener('change', () => {
      const file = photoInput.files[0];
      if (file) {
        const reader = new FileReader();
        reader.onload = e => preview.src = e.target.result;
        reader.readAsDataURL(file);
      }
    });

    form.addEventListener('submit', async (e) => {
      e.preventDefault();
      if (!photoInput.files[0]) return;
        statusDiv.innerHTML = '<div class="spinner-border text-light" role="status"><span class="visually-hidden"></span></div>';
      const reader = new FileReader();
      reader.onload = async (e) => {
        const base64Photo = e.target.result.split(',')[1];
        
        try {
          const response = await fetch('/user/edit_profile', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ photo: base64Photo })
          });

          const data = await response.json();
          if (data.success) {
            statusDiv.textContent = data.success;
            statusDiv.className = 'text-success mt-2';
            window.location.href = '/user'; 
          } else {
            statusDiv.textContent = data.error || 'Error updating photo';
            statusDiv.className = 'text-danger mt-2';
          }
        } catch (err) {
          statusDiv.textContent = 'Error connecting to server';
          statusDiv.className = 'text-danger mt-2';
        }
      };
      reader.readAsDataURL(photoInput.files[0]);
    });