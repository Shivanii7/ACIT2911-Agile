const openModalButtons = document.querySelectorAll("[data-modal-target]");
const closeModalButtons = document.querySelectorAll("[data-close-button]");
const overlay = document.getElementById("overlay");

openModalButtons.forEach((button) => {
  button.addEventListener("click", (event) => {
    event.preventDefault();
    const modal = document.querySelector(button.dataset.modalTarget);
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
      })
      .catch((e) => {
        console.log(
          "There was a problem with the fetch operation: " + e.message
        );
      });
  });
});

overlay.addEventListener("click", () => {
  const modals = document.querySelectorAll(".modal.active");
  modals.forEach((modal) => {
    closeModal(modal);
  });
});

closeModalButtons.forEach((button) => {
  button.addEventListener("click", () => {
    const modal = button.closest(".modal");
    closeModal(modal);
  });
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