// DOM elements
const inputDoB = document.getElementById("form-dob");
const inputFields = Array.from(document.querySelectorAll("form input, #form-grade"))
    .filter((inputField) => !(inputField.parentElement.classList.contains("role-switch")));
const roleSwitch = document.querySelectorAll("form .role-switch input");
const selectField = document.getElementById("form-grade");
const inputSubmit = document.getElementById("register-submit");
const formRegister = document.getElementById("register-form");
const errorMsg = document.getElementById("error-msg").innerText.trim();

// Miscellaneous variables
const dateToday = new Date();     // Latest date = today  
let yearEarliest = dateToday.getFullYear() - 101;
let monthEarliest = dateToday.getMonth();
let dayEarliest, dateEarliest;
let selectedRole = document.querySelector('input[name="role"]:checked').value; // Stores position of role switch

const errorMapping = {
    "You must provide your name." : "err-name",
    "This username already exists." : "err-username",
    "You must provide a username." : "err-username",
    "This email already exists." : "err-email",
    "The emails do not match!" : "err-confirm-email",
    "You must provide a password." : "err-pass",
    "Password is not strong enough." : "err-pass",
    "The passwords do not match!" : "err-confirm-pass"
}

const errorHTML = `
<div class="error-img">
    <img src="../static/vendor/images/login/error-icon.png" alt="" srcset="">
</div>
<span class="error-msg">
</span>
` 

const objKeys = ["name", "username", "grade", "email"];

function dateFieldEvents() {
    /**
     * If today's date is the last day of the current month, then set 
     * the earliest selectable date to be the first day of the next month
     * 100/101 years ago
     **/ 
    if (dateToday.getDate() >= new Date(dateToday.getFullYear(), dateToday.getMonth(), 0)) {
        if (monthEarliest >= 11) {  // If today's date = Dec 31st, then move earliest date to Jan 1st of next year
            yearEarliest += 1;
            monthEarliest = 0;
        } else {
            monthEarliest += 1;     // Otherwise, just move to next month of the same year
        }

        dayEarliest = 1;            // Set to first day of next month
    } else {      // Otherwise, increment to next day of current month
        dayEarliest = dateToday.getDate() + 1;
    }

    dateEarliest = new Date(yearEarliest, monthEarliest, dayEarliest);

    inputDoB.addEventListener("focus", function () {
        this.type = "date";
        this.placeholder = "Date of Birth";
    });

    inputDoB.addEventListener("blur", function () {
        if (!this.value) {
            this.type = "text";
            this.placeholder = "Date of Birth";
        }
    });

    window.addEventListener("DOMContentLoaded", function () {
        inputDoB.setAttribute("min", dateEarliest.toISOString().slice(0, 10));
        inputDoB.setAttribute("max", dateToday.toISOString().slice(0, 10));
    });
}

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

function updateField() {
    // Text field and form submit button interactions (error messages/button disabling); 
    // primarily occurs whenever a field receives a value/input

    // Event listener for when the role is changed to 'student'
    // This will re-evaluate the form submission criteria
    document.getElementById("student").addEventListener("change", function() {
        selectedRole = this.value;
        toggleGradeField();
        updateFieldState(); // Update the state of the form based on the new role
        console.log(selectedRole)
    });
    // Event listener for when the role is changed to 'teacher'
    document.getElementById("teacher").addEventListener("change", function() {
        selectedRole = this.value;
        toggleGradeField();
        updateFieldState(); // Update the state of the form based on the new role
        console.log(selectedRole)
    });

    inputFields.forEach((inputField) => {
        if (inputField.classList.contains("register-form-date")) {
            ;["blur", "change"].forEach((event) => {
                inputField.addEventListener(event, () => {
                    if (inputField.value && inputField.value != "") {
                        updateFieldAux(inputField);
                    } else {
                        inputSubmit.classList.remove("clickable");
                        inputSubmit.disabled = true;
                    }
                });
            });
        } else {
            ;["input", "change"].forEach((event) => {
                inputField.addEventListener(event, () => {
                    updateFieldAux(inputField);
                });
            });
        }
    });

    // ;["input", "change"].forEach((event) => {
    //     selectField.addEventListener(event, () => {
    //         updateFieldAux(selectField);
    //     });
    // });
}

function updateFieldState() {
    inputFields.forEach((inputField) => {
        updateFieldAux(inputField); // Seperate function to check each field to update the form submission status (was causing errors with new roles)
    });
}

function updateFieldAux(inputField) {
    let errorField = inputField.nextElementSibling;
        
    // Remove error messages and highlighting from the input box, if any
    inputField.classList.remove("show-error");
    errorField.classList.remove("show-error");

    // Check if the grade field is required based on the selected role
    let isGradeRequired = selectedRole === "student";
    
    // Check if all required fields are non-empty.
    // If the selected role is 'teacher', the grade field is not considered necessary.
    let fieldsContent = Array.from(inputFields).map(field => {
        if (field.id === "form-grade") {
            return isGradeRequired ? field.value.trim() !== "" : true;
        }
        return field.value.trim() !== ""; // Check if the field is non-empty
    });
    
    console.log(fieldsContent)

    // Enable form submission if all required fields are filled.
    // If the selected role is 'teacher', the grade field can be ignored.
    if (fieldsContent.every((fieldState) => fieldState)) {
        inputSubmit.classList.add("clickable");
        inputSubmit.disabled = false;
    } else {
        inputSubmit.classList.remove("clickable");
        inputSubmit.disabled = true;
    }
}

function retainFieldInfo() {
    /**
     * QoL feature: 
     *    If the user fails the registration process and is brought back to the sign up page,
     *    then a majority of the info they entered will be retained before the page reloads through
     *    sessionStorage and automatically be restored in the text field after redirection.
     *    No sensitive data (e.g. passwords, date) will be stored.
     *    
     *    Note that since sessionStorage is being used instead of localStorage, any data 
     *    stored will be automatically wiped after the user session ends (e.g. closing browser tab).
     **/

    window.addEventListener("DOMContentLoaded", () => {
        let savedFields = Array.from(inputFields).slice(0, 2).concat(selectField, Array.from(inputFields)[3]);
        let storedData = JSON.parse(sessionStorage.getItem("signUpInfo"));

        if (!["null", null].includes(storedData)) {
            objKeys.forEach((category, index) => {
                if (!["null", null].includes(storedData[category])) {
                    savedFields[index].value = storedData[category];
                }
            });

            // Restore the selected role (student or teacher) if it's saved
            if (storedData.selectedRole) {
                document.getElementById(storedData.selectedRole).checked = true;
                selectedRole = storedData.selectedRole;
                toggleGradeField(); // Ensure correct display of the grade field based on the restored role
            }
            
        }

        sessionStorage.removeItem("signUpInfo");
    });

    formRegister.addEventListener("submit", (event) => {
        let savedFields = Array.from(inputFields).slice(0, 2).concat(selectField, Array.from(inputFields)[3]);
        let obj = {};

        savedFields.forEach((htmlNode, index) => {
            obj[objKeys[index]] = htmlNode.value; 
        });

        // Save the selected role (student/teacher)
        obj.selectedRole = selectedRole;
        
        sessionStorage.setItem("signUpInfo", JSON.stringify(obj));
    });
}

function toggleGradeField() {
    const gradeField = document.getElementById("form-grade");
    if (selectedRole === "teacher") {
        gradeField.style.display = "none";
        gradeField.removeAttribute("required"); // Remove the 'required' attribute for teacher role
    } else {
        gradeField.style.display = "block";
        gradeField.setAttribute("required", ""); // Set the 'required' attribute for student role
    }
}

function main() {
    renderError();
    dateFieldEvents();
    updateField();
    retainFieldInfo();
}

main();