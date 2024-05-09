function showPopupModal(url) {
  // Create a modal container element
  var modalContainer = document.createElement("div");
  modalContainer.setAttribute("class", "popup-modal-container");

  // Create an iframe element for the modal content
  var modalContent = document.createElement("iframe");
  modalContent.setAttribute("src", url);
  modalContent.setAttribute("class", "popup-modal-content");

  // Create a close button
  var closeButton = document.createElement("a");
  closeButton.setAttribute("class", "close");
  closeButton.addEventListener("click", closeModal);

  // Append the modal content to the modal container
  modalContainer.appendChild(modalContent);
  // Append the modal container to the body
  document.body.appendChild(modalContainer);
  // Append close button to the modal
  modalContainer.appendChild(closeButton);
  // Prevent scrolling of the page while the modal is open
  document.body.style.overflow = "hidden";

  // Function to close the modal
  function closeModal() {
    // Remove the modal container from the body
    modalContainer.remove();
    // Restore scrolling of the page
    document.body.style.overflow = "";
  }

  // Close the modal when clicking outside the iframe content
  modalContainer.addEventListener("click", function (event) {
    if (event.target === modalContainer) {
      closeModal();
    }
  });
}