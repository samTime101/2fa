    document.addEventListener('DOMContentLoaded', () => {
      const datePicker = document.getElementById('date');
      datePicker.value = new Date().toISOString().split('T')[0];
    });