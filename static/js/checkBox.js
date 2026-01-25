

// document.querySelectorAll('.points').forEach((checkbox) => {
//     checkbox.addEventListener('change', function () {
//         const displayInput =
//             this.closest('.form-check').querySelector('.displayValue');

//         if (this.checked) {
//             displayInput.value = this.value;
//         } else {
//             displayInput.value = '';
//         }
//     });
// });


document.querySelectorAll('.points').forEach((checkbox) => {
    checkbox.addEventListener('change', function () {
        const row = this.closest('tr');
        const displayInput =
            this.closest('.form-check').querySelector('.displayValue');

        if (this.checked) {
            displayInput.value = this.value;

            // Disable all inputs in this row
            row.querySelectorAll('input').forEach(input => {
                input.disabled = true;
            });

            // Optional: visually show disabled state
            row.style.opacity = '0.5';
            row.style.pointerEvents = 'none';
        }
    });
});






