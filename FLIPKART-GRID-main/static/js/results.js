let socket = io.connect();
let serialNumber = 1;

// Listen for real-time results from the server
socket.on("results_channel", function (data) {
  console.log(data);
  let resultsBody = document.getElementById("results-body");

  // Assuming data.objects is a single object with the required keys
  let object = data.objects;

  let newRow = document.createElement("tr");

  newRow.innerHTML = `
          <td>${serialNumber}</td>
          <td>${object.name || ""}</td>
          <td>${object.mrp || ""}</td>
          <td>${object.status || ""}</td>
          <td>${object.mfg_date || ""}</td>
          <td>${object.exp_date || ""}</td>
          <td>${object.brand || ""}</td>
          <td>${object.pack_size || ""}</td>
        `;

  resultsBody.appendChild(newRow);
  serialNumber++;
});
