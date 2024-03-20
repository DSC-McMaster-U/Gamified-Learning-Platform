// DOM Elements
const inputFields = document.querySelectorAll("form input");
const inputSubmit = document.getElementById("login-submit");
const formLogin = document.getElementById("login-form");
const lblRemember = document.getElementById("lbl-remember");
const errorMsg = document.getElementById("error-msg").innerText.trim();
let fieldsContent;

// Miscellaneous variables
const errorMapping = {
    "This account is locked." : "err-pass",
    "Incorrect password." : "err-pass",
    "The email address is associated with multiple roles. Please contact support." : "err-email",
    "A user with this email does not exist!" : "err-email"
}

const errorHTML = `
<div class="error-img">
    <img src="../static/vendor/images/login/error-icon.png" alt="" srcset="">
</div>
<span class="error-msg">
</span>
` 

function renderError() {
    if (!["", null].includes(errorMsg) &&
        Object.keys(errorMapping).some((error) => errorMsg.includes(error))) {
        
        let errorMapKey = Object.keys(errorMapping).find((error) => errorMsg.includes(error));
        let errorField = document.getElementById(errorMapping[errorMapKey]);
        let inputField = errorField.previousElementSibling;

        errorField.innerHTML = errorHTML;
        errorField.querySelector(".error-msg").innerText = errorMsg;

        errorField.classList.add("show-error");
        inputField.classList.add("show-error");
    }
}

function main() {
    renderError();

    // Text field and form submit button interactions (error messages/button disabling); 
    // primarily occurs whenever a field receives a value/input
    inputFields.forEach((inputField) => {
        inputField.addEventListener("input", () => {
            let errMsg = inputField.nextElementSibling;
    
            // Remove error messages and highlighting from the input box, if any
            inputField.classList.remove("show-error");
            errMsg.classList.remove("show-error");
    
            // Checks to see if this and all other text fields are empty (or bloated 
            // with whitespace); if not, then enables the form submit button
            fieldsContent = Array.from(inputFields, (inputField) => inputField.value.trim() != "");
    
            if (fieldsContent.every((fieldState) => fieldState)) {
                inputSubmit.classList.add("clickable");
                inputSubmit.disabled = false;
            } else {
                inputSubmit.classList.remove("clickable");
                inputSubmit.disabled = true;
            }
        });
    });

    lblRemember.addEventListener("click", () => {
        lblRemember.previousElementSibling.checked = !lblRemember.previousElementSibling.checked; 
    })

    /**
     * QoL feature (more useful for registration): 
     *    If the user fails the login authentication and is brought back to the login page,
     *    then the email they entered will be retained before the page reloads through
     *    sessionStorage and automatically be restored in the text field after redirection.
     *    
     *    Note that since sessionStorage is being used instead of localStorage, any data 
     *    stored will be automatically wiped after the user session ends (e.g. closing browser tab).
     *    Also, no sensitive data (e.g. passwords) will be stored.
     **/ 
    window.addEventListener("DOMContentLoaded", () => {       
        if (!["null", null].includes(sessionStorage.getItem("email"))) {
            inputFields[0].value = sessionStorage.getItem("email");
            sessionStorage.removeItem("email");
        }

        // If any left over data from registration page, remove that from session storage
        if (!["null", null].includes(sessionStorage.getItem("signUpInfo"))) {
            sessionStorage.removeItem("signUpInfo");
        }
    });

    formLogin.addEventListener("submit", (event) => {
        sessionStorage.setItem("email", inputFields[0].value); 
    });
}

main();
