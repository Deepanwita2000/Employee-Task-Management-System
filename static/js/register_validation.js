function validateUser() {
    const fnameField= document.getElementById("first_name");
    const fname_error= document.getElementById("fname_error");
    const fname = fnameField.value.trim()
    
    const lnameField = document.getElementById("last_name"); 
    const lname_error = document.getElementById("lname_error"); 
    const lname = lnameField.value.trim()

    const bioField = document.getElementById("bio")
    const bio_error = document.getElementById("bio_error")
    const bio = bioField.value.trim()

    const usernameField = document.getElementById("username"); 
    const username_error = document.getElementById("username_error"); 
    const username = usernameField.value.trim()


    const emailField = document.getElementById("email"); 
    const email_error = document.getElementById("email_error"); 
    const email = emailField.value.trim()


    // const designationField = document.getElementById("designation"); 
    // const designation_error = document.getElementById("designation_error"); 
    // const designation = designationField.value.trim()

    const dateField = document.getElementById("date"); 
    const date_error = document.getElementById("date_error"); 
    const date = dateField.value.trim()


    const passwordField = document.getElementById("password"); 
    const password_error = document.getElementById("password_error"); 
    const password = passwordField.value.trim()
    
    const confirmField = document.getElementById("password_confirm"); 
    const confirm_error = document.getElementById("confirm_error"); 
    const confirm = confirmField.value.trim()
    
    const roleField = document.getElementById("role"); 
    const role_error = document.getElementById("role_error"); 
    const role = roleField.value.trim()

    const imageField = document.getElementById("user_image"); 
    const image_error = document.getElementById("image_error"); 
    const image = imageField.files[0];


    let isValid = true;
    fname_error.innerHTML = '';
    lname_error.innerHTML = '';
    username_error.innerHTML = '';
    email_error.innerHTML = '';
    bio_error.innerHTML = '';
    // designation_error.innerHTML = '';
    date_error.innerHTML = '';
    password_error.innerHTML = '';
    confirm_error.innerHTML = '';
    role_error.innerHTML = '';

    const regex = /^[A-Za-z\s]+$/;

    if (fname === '') {
        
         fname_error.innerHTML = `<span class="text-danger">First name cannot be blank.</span>`;
        isValid = false;
    
    } 
    else if (!regex.test(fname)) {
        fname_error.innerHTML = `<div class="alert alert-danger">fname must contain only alphabets and spaces.</div>`;
        isValid = false;
    }   

    // last name
    if (lname === '') {
        lname_error.innerHTML = `<span class="text-danger">last name  cannot be blank.</span>`;
        isValid = false;
    }
    else if (!regex.test(lname)) {
        lname_error.innerHTML = `<span class="text-danger">last name must contain only alphabets and spaces.</span>`;
        isValid = false;
    } 

    // bio
    if(bio === ''){
        bio_error.innerHTML = `<span class="text-danger">bio field cannot be blank  .</span>`
    }
    else if(bio.length > 200){
        bio_error.innerHTML = `<span class="text-danger">no.of characters cannot exeed more than 200  .</span>`
    }


    



    // username
    if (username === '') {
        username_error.innerHTML = `<span class="text-danger">username cannot be blank.</span>`;
        isValid = false;
    }  else if (username.length < 4) {
        username_error.innerHTML = `<span class="text-danger">username be at least 4 characters long.</span>`;
        isValid = false;
    }
    designation
    if (designation === '' || designation ==='****') {
        designation_error.innerHTML = `<span class="text-danger">designation  cannot be blank.</span>`;
        isValid = false;
    } 

     // date
    // const today = new Date().toISOString().split('T')[0];  // format: "2025-12-04"
    
    if (date === '') {
        date_error.innerHTML = `<div class="alert alert-danger">date cannot be blank.</div>`;
        isValid = false;
    }
    // } else if (date !== today) {
    // date_error.innerHTML = `<div class="alert alert-danger">Please write current date (${today}).</div>`;
    // isValid = false;
    // }



    // email
    if (email === '') {
        email_error.innerHTML = `<span class="text-danger"> email cannot be blank.</span>`;
        isValid = false;
    }else if (!email.endsWith('@gmail.com')) {
    email_error.innerHTML = `<span class="text-danger">Email must end with @gmail.com.</span>`;
    isValid = false;
    } 

    // password
    const passwordRegex = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$/;

    if (password === '') {
        password_error.innerHTML = `<span class="text-danger">password  cannot be blank.</span>`;
        isValid = false;
  
    } else if (password.length < 8) {
        password_error.innerHTML = `<span class="text-danger">password be at least 8 characters long.</span>`;
        isValid = false;
    }  else if (!passwordRegex.test(password)) {
    password_error.innerHTML = `
        <span class="text-danger">
            Password must contain:
            <br>• At least 1 uppercase letter  
            <br>• At least 1 lowercase letter  
            <br>• At least 1 digit  
            <br>• At least 1 special character  
            <br>• Minimum 8 characters
        </span>`;
    isValid = false;
}

    // confirm password
    if (confirm === '') {
        confirm_error.innerHTML = `<span class="text-danger">password  cannot be blank.</span>`;
        isValid = false;
    } else if (!(password)) {
        fname_error.innerHTML = `<span class="text-danger">password does not match.</span>`;
        isValid = false;
    } else if (confirm.length < 8) {
        confirm.innerHTML = `<span class="text-danger">password be at least 8 characters long.</span>`;
        isValid = false;
    }  

    // role
    if (role === '') {
        role_error.innerHTML = `<span class="text-danger">role  cannot be blank.</span>`;
        isValid = false;
      }

    // image
    if (image === '') {
        image_error.innerHTML = `<span class="text-danger">image  cannot be blank.</span>`;
        isValid = false;
    }
    //   }else  if (image.size > 2 * 1024 * 1024) {
    //     image_error.innerHTML = `<span class="text-danger">Image must be less than 2 MB.</span>`;
    //     return false;
    // }

      document.getElementById('signup_btn').disabled = !isValid;
    return isValid;
   
}



function clearError(id) {
    document.getElementById(id).innerHTML = '';
}
