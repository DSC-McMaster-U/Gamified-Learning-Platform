// DOM elements
const inputDoB = document.getElementById("form-dob");
const inputFields = document.querySelectorAll("form input");
const selectField = document.getElementById("form-grade");
const inputSubmit = document.getElementById("register-submit");
const formRegister = document.getElementById("register-form");

// Miscellaneous variables
const dateToday = new Date();     // Latest date = today  
let yearEarliest = dateToday.getFullYear() - 101;
let monthEarliest = dateToday.getMonth();
let dayEarliest, dateEarliest;

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

function updateField() {
        // Text field and form submit button interactions (error messages/button disabling); 
    // primarily occurs whenever a field receives a value/input
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

    ;["input", "change"].forEach((event) => {
        selectField.addEventListener(event, () => {
            updateFieldAux(selectField);
        });
    });
}

function updateFieldAux(inputField) {
    let errMsg = inputField.nextElementSibling;
        
    // Remove error messages and highlighting from the input box, if any
    inputField.classList.remove("show-error");
    errMsg.classList.remove("show-error");

    // Checks to see if this and all other text fields are empty (or bloated 
    // with whitespace); if not, then enables the form submit button
    let fieldsContent = Array.from(inputFields, (inputField) => inputField.value.trim() != "");
    fieldsContent = fieldsContent.concat([!["", null].includes(selectField.value)]);

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

        console.log(storedData);

        if (!["null", null].includes(storedData)) {
            console.log("Test 1")

            objKeys.forEach((category, index) => {
                console.log(storedData[category])
                if (!["null", null].includes(storedData[category])) {
                    savedFields[index].value = storedData[category];
                }
            });
        }

        sessionStorage.removeItem("signUpInfo");
    });

    formRegister.addEventListener("submit", (event) => {
        let savedFields = Array.from(inputFields).slice(0, 2).concat(selectField, Array.from(inputFields)[3]);
        let obj = {};

        savedFields.forEach((htmlNode, index) => {
            obj[objKeys[index]] = htmlNode.value; 
        });

        // console.log(obj)

        sessionStorage.setItem("signUpInfo", JSON.stringify(obj));
    });
}

function main() {
    dateFieldEvents();
    updateField();
    retainFieldInfo();
}

main();