if (localStorage.getItem("darko") === null) {
    localStorage.setItem("darko", "false");
  } else {
    darko = localStorage.getItem("darko") === "true";
  }
  
  document.addEventListener("DOMContentLoaded", (event) => {
    if (darko) {
      document.body.classList.add("darkmode");
      document.getElementById("dmtoggle").checked = true;
      console.log("darkness");
    } else {
      document.body.classList.remove("darkmode");
      document.getElementById("dmtoggle").checked = false;
    }
  });
  
  function darktime() {
    console.log("darkness");
    darko = !darko;
    if (darko) {
      document.body.classList.add("darkmode");
      localStorage.setItem("darko", "true");
    } else {
      document.body.classList.remove("darkmode");
      localStorage.setItem("darko", "false");
    }
  }
  
  document.getElementById("dmtoggle").onclick = darktime;
  
  function openModal() {
    document.getElementById("expenseModal").style.display = "block";
    fetch("{{ url_for('fill') }}")
      .then((response) => response.text())
      .then((html) => {
        document.getElementById("modalContent").innerHTML = html;
      })
      .catch((error) => console.error("Error fetching create.html:", error));
  }
  
  function closeModal() {
    document.getElementById("expenseModal").style.display = "none";
  }
  
  function show_noti(value) {
    if (value <= 0) {
      console.log(value)
      var reminder = document.getElementById("reminder");
      reminder.classList.add("show");
    }
  }
  
  show_noti({{value}});
  
  function openEditModal(transaction_id) {
    document.getElementById('editModal').style.display = 'block';
    fetch(`{{ url_for('edit_form') }}?id=${transaction_id}`)
      .then(response => response.text())
      .then(html => {
        document.getElementById('editModalContent').innerHTML = html;
      })
      .catch(error => console.error('Error fetching edit form:', error));
  }
  
  function closeEditModal() {
    document.getElementById('editModal').style.display = 'none';
  }
  
  