  document.getElementById("main-section").style.display = "block";
  // document.getElementById("welcome").innerHTML = `<h2 class="text-white fw-bold mb-4 text-center"><i class="fas fa-user"></i>2 USER</h2>`;
  // document.getElementById("username").innerText = `username: ${currentUser.name}`;
// function showMainUI() {
//   document.getElementById("login-section").style.display = "none";
//   document.getElementById("main-section").style.display = "block";
//   document.getElementById("username").innerText = `user: ${currentUser.name}`;

//   $.get("./2fa.csv", function(data) {
//     const rows = $.csv.toArrays(data);
//     console.log(rows)
//     const header = rows[0];
//     const filtered = rows.filter((row, index) => {
//       if (index === 0) return true; 
//       return row[1].trim().toLowerCase() === currentUser.name; 
//     });

    
//     let table = `<table class="table table-bordered table-striped"><thead><tr>`;
//     header.forEach(h => table += `<th>${h}</th>`);
//     table += `</tr></thead><tbody>`;
//     for (let i = 1; i < filtered.length; i++) {
//       table += "<tr>";
//       filtered[i].forEach(cell => table += `<td>${cell}</td>`);
//       table += "</tr>";
//     }
//     table += "</tbody></table>";

//     document.getElementById("table-container").innerHTML = table;
//     $('#table-container table').DataTable({ paging: false });
//   });
// }

// function showMainUI() {
//   document.getElementById("welcome").innerHTML = `<h2 class="text-white fw-bold mb-4 text-center"><i class="fas fa-user"></i> 2FA USER</h2>`;
//   document.getElementById("username").innerText = `username: ${currentUser.name}`;
//   $.get("/csv/2fa.csv", function(csvData) {
//     var rows = $.csv.toArrays(csvData);
//     console.log(rows)
//     var filtered = rows.filter((row, index) => {
//       if (index === 0) return true;
//       return row[1] && row[1].trim() === currentUser.name;
//     });

//     var filteredCSV = filtered.map(r => r.join(",")).join("\n");
//     var csvBlob = new Blob([filteredCSV], { type: "text/csv" });
//     var csvUrl = URL.createObjectURL(csvBlob);

//     CsvToHtmlTable.init({
//       csv_path: csvUrl,
//       element: "table-container",
//       allow_download: false,
//       csv_options: { separator: ",", delimiter: '"' },
//       datatables_options: {
//         paging: true,
//         searching: true,
//         ordering: true,
//         order: [[0, 'desc']],
//         pageLength: 5,
//         scrollX: true
//       },
//       custom_formatting: [
//         [4, format_link] 
//       ]
//     });
//   });
// }

// function showMainUI() {

//   document.getElementById("welcome").innerHTML = `<h2 class="text-white fw-bold mb-4 text-center"><i class="fas fa-user"></i>2FA USER</h2>`;
//   document.getElementById("username").innerText = `username: ${currentUser.name}`;
//   $.get("/csv/2fa.csv", function(csvData) {
//     var allRows = $.csv.toArrays(csvData);

//     var headerRow = allRows[0];

//     var filteredRows = [];

//     for (var i = 0; i < allRows.length; i++) {
//       var row = allRows[i];

     
//       if (i === 0) {
//         filteredRows.push(row);
//       } else {
//         var nameInRow = row[1]; 
        
//         var userName = currentUser.name;

//         if (nameInRow === userName) {
//           filteredRows.push(row);
//         }
//       }
//     }
//         console.log(filteredRows)


//     var htmlTable = "<table class='table table-bordered table-striped'>";
//     htmlTable += "<thead><tr>";
//     for (var i = 0; i < headerRow.length; i++) {
//       htmlTable += "<th>" + headerRow[i] + "</th>";
//     }
//     htmlTable += "</tr></thead><tbody>";

//     for (var i = 1; i < filteredRows.length; i++) {
//       htmlTable += "<tr>";
//       var row = filteredRows[i];
//       for (var j = 0; j < row.length; j++) {
//         htmlTable += "<td>" + row[j] + "</td>";
//       }
//       htmlTable += "</tr>";
//     }

//     htmlTable += "</tbody></table>";

//     document.getElementById("table-container").innerHTML = htmlTable;

// $('#table-container table').DataTable({
//   paging: true,
//   searching: false,
//   // info: true,
//   ordering: true,
//   order: [[0, 'desc']],
//   pageLength: 5,

// });
//   }
// );
// }
function showMainUI() {
  // document.getElementById("welcome").innerHTML = `<h2 class="text-white fw-bold mb-4 text-center"><i class="fas fa-user"></i> 2FA USER</h2>`;
document.getElementById("welcome").innerHTML = `
  <div class="text-center my-4">
    <h2 class="fw-bold text-light">
      <span class="animated-gradient"><i class="fas fa-lock me-2 text-light"></i>2FA Systems</span>
    </h2>
    <p class="text-light">Welcome, <strong>${currentUser.name}</strong></p>
  </div>
`;

  // document.getElementById("username").innerText = `username: ${currentUser.name}`;

  $.get("/csv/2fa.csv", function(csvData) {
    var allRows = $.csv.toArrays(csvData);

    var filteredRows = [];
    var userName = currentUser.name;

    for (var i = 0; i < allRows.length; i++) {
      var row = allRows[i];

      if (i === 0) {
        filteredRows.push(row);
      } else {
        if (row[1] && row[1].trim() === userName) {
          filteredRows.push(row);
        }
      }
    }

    var filteredCSV = "";
    for (var r = 0; r < filteredRows.length; r++) {
      filteredCSV += filteredRows[r].join(",") + "\n";
    }

    var csvBlob = new Blob([filteredCSV], { type: "text/csv" });
    var csvUrl = URL.createObjectURL(csvBlob);

    CsvToHtmlTable.init({
      csv_path: csvUrl,
      element: "table-container",
      allow_download: false,
      csv_options: { separator: ",", delimiter: '"' },
      datatables_options: {
        lengthMenu: [5, 10, 25, 50],
        paging: true,
        searching: true,
        ordering: true,
        order: [[0, 'desc']],
        pageLength: 5,
        scrollX: true
      },
      custom_formatting: [
        [4, format_link] 
      ]
    });
  });
}

    // function showMainUI() {
    //   document.getElementById("login-section").style.display = "none";
    //   document.getElementById("main-section").style.display = "block";
    //    document.getElementById("username").innerText = `user: ${currentUser.name}`
    //   CsvToHtmlTable.init({
    //     csv_path: "./2fa.csv",
    //     element: "table-container",
    //     allow_download: false,
    //     csv_options: { separator: ",", delimiter: '"' },
    //     datatables_options: { paging: false },
    //     custom_formatting: [
    //       [4, format_link]
    //     ]
    //   });
    // }


//JUly 19

    function format_link(link) {
      return link ? "<a href='" + link + "' target='_blank'>" + link + "</a>" : "";
    }

    async function generateAndPlayTone(user) {
      document.getElementById('generated_frequency').hidden = false;
      const now = new Date();
      const minute = now.getUTCMinutes();
      now.setUTCSeconds(0, 0);
      const timestampStr = now.toISOString().split('.')[0] + 'Z';

      const combo = `${user.secret}-${timestampStr}`;
      const hashHex = sha256(combo);
      const hashValue = parseInt(hashHex.slice(-4), 16);
      const bias = hashValue % 20;
      const finalFrequency = user.frequency + bias + minute;

      console.log(`[${user.name}] Final Frequency: ${finalFrequency.toFixed(2)} Hz`);

      // document.getElementById("username").innerText = `Welcome, ${user.name}`;

      document.getElementById("generated_frequency").innerText = `Freq: ${finalFrequency.toFixed(2)} Hz`;
      playTone(finalFrequency);
    }

    function playTone(freq) {
      const synth = new Tone.Synth().toDestination();
      Tone.start().then(() => {
        synth.triggerAttackRelease(freq, "2s");
      });
    }
    showMainUI()