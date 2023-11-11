// DOM Elements
const inputFields = document.querySelectorAll("form input");
const inputSubmit = document.getElementById("login-submit");
const formLogin = document.getElementById("login-form");
const lblRemember = document.getElementById("lbl-remember");

let fieldsContent;

function main() {
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
