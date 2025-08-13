

// -------------------------------------------------------------------------------------
  console.log("Present Dates:", presentDates);
  console.log("Absent Dates:", absentDates);
  const allDates = Array.from(new Set(presentDates.concat(absentDates))).sort();
  console.log("All Dates:", allDates);
  const attendanceData = allDates.map(date => presentDates.includes(date) ? 1 : 0);
  console.log("Attendance Data:", attendanceData);
  const ctx = document.getElementById('attendanceChart').getContext('2d');
  new Chart(ctx, {
      type: 'line',  
      data: {        
          labels: allDates,
          datasets: [{
              label: '1 = Present, 0 = Absent',
              data: attendanceData,
              backgroundColor: attendanceData.map(d => d ? 'green' : 'red'),
              // fill:false,
              // tension:0.1,
              borderColor: 'rgb(75, 192, 192)',
              // change the outer border color to a lighter shade
              borderWidth: 2,
              pointRadius: 5,
          }]
      },
      options: {
          responsive: true,
          scales: {
              x:{
                ticks:{
                  // X AXIS KO LABEL HIDE GARNA

                  display:true,
                  // color: 'white'
                },
                // grid:{// color:'white'}
              },
              y: {
                  beginAtZero: true,
                  ticks: { stepSize: 1 },
                  // grid:{color:'white'}
              }
          },
          plugins: {
              legend: { display: false }
          }
      }
  });
// -------------------------------------------------------------------------------------

document.getElementById('aiAnalysisButton').addEventListener('click', async function() {
    document.querySelector('.row.justify-content-center.mt-4').removeAttribute('hidden');
    const analysisCardParagraph = document.querySelector('.card.bg-dark.border-0.shadow-lg.p-3.rounded-4.mb-4 p');
    analysisCardParagraph.innerHTML = "<div class='spinner-border' role='status'><span class='visually-hidden'></span></div>";
    document.getElementById('aiAnalysisButton').setAttribute('hidden', true);
    // alert(username)

    try {
        const response = await fetch('/admin/user_info/analysis', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username: username })
        });

        const data = await response.json();

        if (data.error) {
            alert(data.error);
        } else {
            // RESPONSE WIL BE IN MARKDOWN FORMAT
            console.log("AI Analysis Response:", data.analysis);
            analysisCardParagraph.innerHTML = marked.parse(data.analysis);

            // analysisCardParagraph.textContent = data.analysis;
            document.querySelector('.row.justify-content-center.mt-4').removeAttribute('hidden');
        }
    } catch (error) {
        console.error('Error:', error);
        analysisCardParagraph.textContent = "An error occurred while analyzing the data";
    }
});


// -------------------------------------------------------------------------------------
// add toggle to show/hide the attendance chart
document.getElementById('attendanceChartButton').addEventListener('click', function() {
    const attendanceOverview = document.getElementById('attendanceOverview');
    attendanceOverview.toggleAttribute('hidden');
});