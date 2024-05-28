const overlay = document.getElementById("overlay");
const openModalButton =document.getElementById("open_window_button");
const closeModalButton =document.getElementById("close_window_button");
let redirectUrl

document.querySelector("form").addEventListener("submit", function(event){
  event.preventDefault();
});

  openModalButton.addEventListener("click", (event) => {
    event.preventDefault();
    const modal = document.querySelector(openModalButton.dataset.modalTarget);
    openModal(modal);

    const form = document.querySelector("form");
    const formData = new FormData(form);
    const modalBody = document.querySelector(".modal-body");

    fetch(form.action, {
      method: "POST",
      body: formData,
    })
      .then((response) => {
        console.log(response);
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
      })
      .then((json) => {
        console.log(json);
        modalBody.textContent = json.message;

        redirectUrl = json.redirect_url;
      })
      .catch((e) => {
        console.log(
          "There was a problem with the fetch operation: " + e.message
        );
      });
  });

overlay.addEventListener("click", () => {
  const modals = document.querySelectorAll(".modal.active");
  modals.forEach((modal) => {
    closeModal(modal);
  });
});

closeModalButton.addEventListener("click", (event) => {
  console.log(2)
  console.log(redirectUrl)
  const modal = closeModalButton.closest(".modal");
  closeModal(modal);    
  window.location.href = redirectUrl;
});


function openModal(modal) {
  if (modal == null) return;
  modal.classList.add("active");
  overlay.classList.add("active");
}

function closeModal(modal) {
  if (modal == null) return;
  modal.classList.remove("active");
  overlay.classList.remove("active");
}