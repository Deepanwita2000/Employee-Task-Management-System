
function validateTask() {
     const titleField = document.getElementById('title');
     const title_error = document.getElementById('title_error');
     const title = titleField.value.trim()

     const descriptioField = document.getElementById('description');
     const description_error = document.getElementById('description_error');
     const description = descriptioField.value.trim()

     const emp_emailField = document.getElementById('emp_email');
     const emp_email_error = document.getElementById('email_error');
     const emp_email = emp_emailField.value.trim()

    let isValid = true;
    title_error.innerHTML = '';
    description_error.innerHTML = '';
    emp_email_error.innerHTML = '';

    const regex = /^[A-Za-z\s]+$/;

    if (title === '') {
        title_error.innerHTML = `<div class="alert alert-danger">title  cannot be blank.</div>`;
        isValid = false;
    } else if (!regex.test(title)) {
        title_error.innerHTML = `<div class="alert alert-danger">title_error must contain only alphabets and spaces.</div>`;
        isValid = false;
    } else if (title.length < 2) {
        title_error.innerHTML = `<div class="alert alert-danger">title must be at least 2 characters long.</div>`;
        isValid = false;
    }   
    
    // deacription field
    if (description === '') {
        description_error.innerHTML = `<div class="alert alert-danger"> description cannot be blank.</div>`;
        isValid = false;
    } else if (description.length < 10) {
        description_error.innerHTML = `<div class="alert alert-danger"> description must be at least 10 characters long.</div>`;
        isValid = false;
    }

    // email
    if (emp_email === '') {
        emp_email_error.innerHTML = `<div class="alert alert-danger"> email cannot be blank.</div>`;
        isValid = false;
    }else if (!emp_email.endsWith('@gmail.com')) {
    emp_email_error.innerHTML = `<div class="alert alert-danger">Email must end with @gmail.com.</div>`;
    isValid = false;
    } 

    document.getElementById('task-btn').disabled = !isValid;
    return isValid;
}


function clearError(id) {
    document.getElementById(id).innerHTML = '';
}
