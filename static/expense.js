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
