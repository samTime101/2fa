 document.getElementById('submit').addEventListener('click', async (event) => {
      event.preventDefault();
      const prompt = document.getElementById('prompt').value;
      const responseDiv = document.getElementById('response');

      if (!prompt) {
          responseDiv.innerHTML = '<div class="alert alert-warning">Please enter a prompt.</div>';
          return;
      }

      responseDiv.innerHTML = '<div class="text-center"><div class="spinner-border" role="status"></div> <span></span></div>';

      try {
          const response = await fetch('/analysis', {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({ prompt })
          });

          const data = await response.json();
          const raw = data.response || 'No response from server.';

          if (raw.startsWith('data:image/png;base64,')) {
              responseDiv.innerHTML = `<img src="${raw}" class="img-fluid">`;
          } else {
              responseDiv.innerHTML = `<p>${raw}</p>`;
          }

      } catch (error) {
          console.error('Error:', error);
          responseDiv.innerHTML = '<div class="alert alert-danger">error</div>';
      }
    });

    function format_link(link) {
      if (link)
        return "<a href='" + link + "' target='_blank'>" + link + "</a>";
      else return "";
    }

function loadCSV(dateStr) {
//   const csvPath = `../${dateStr}.csv`;
const csvPath = `/csv/${dateStr}.csv`;

  CsvToHtmlTable.init({
    csv_path: csvPath,
    element: "table-container",
    allow_download: true,
    csv_options: {
      separator: ",",
      delimiter: '"'
    },
    datatables_options: {
      paging: false,
      scrollX: true
    },
    custom_formatting: [
      [4, format_link]
    ]
  });
}


    document.getElementById("datePicker").addEventListener("change", function () {
      const selectedDate = this.value;
      if (selectedDate) {
        loadCSV(selectedDate);
      }
    });

    window.onload = function () {
      const today = new Date().toISOString().slice(0, 10);
      document.getElementById("datePicker").value = today;
      loadCSV(today);
    };