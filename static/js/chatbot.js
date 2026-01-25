// $('#exampleModal').on('show.bs.modal', function (event) {
//   var button = $(event.relatedTarget) // Button that triggered the modal
//   var recipient = button.data('whatever') // Extract info from data-* attributes
//   // If necessary, you could initiate an AJAX request here (and then do the updating in a callback).
//   // Update the modal's content. We'll use jQuery here, but you could use a data binding library or other methods instead.
//   var modal = $(this)
//   modal.find('.modal-title').text('New message to ' + recipient)
//   modal.find('.modal-body input').val(recipient)
// })


// var exampleModal = document.getElementById('exampleModal')
// exampleModal.addEventListener('show.bs.modal', function (event) {
//   var button = event.relatedTarget
//   var recipient = button.getAttribute('data-bs-whatever')

//   var modalTitle = exampleModal.querySelector('.modal-title')
//   var modalInput = exampleModal.querySelector('.modal-body input')

//   modalTitle.textContent = 'New message to ' + recipient
//   modalInput.value = recipient
// })


// document.addEventListener('DOMContentLoaded', function () {

//     var exampleModal = document.getElementById('exampleModal');
//     if (!exampleModal) return;  // Safety check

//     exampleModal.addEventListener('show.bs.modal', function (event) {
//         var button = event.relatedTarget;
//         var recipient = button.getAttribute('data-bs-whatever');

//         var modalTitle = exampleModal.querySelector('.modal-title');
//         var modalInput = exampleModal.querySelector('#recipient-name');

//         modalTitle.textContent = 'New message to ' + recipient;
//         modalInput.value = recipient;
//     });
// });
