    // document.addEventListener('DOMContentLoaded', () => {
    //   const datePicker = document.getElementById('date');
    //   datePicker.value = new Date().toISOString().split('T')[0];
    // });

    document.addEventListener('DOMContentLoaded', () => {
  const datePicker = document.getElementById('date');
  const today = new Date();
  const formattedToday = today.toLocaleDateString('en-CA'); 
  datePicker.value = formattedToday;
});
