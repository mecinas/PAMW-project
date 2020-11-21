PL = 'ĄĆĘŁŃÓŚŹŻ';
pl = 'ąćęłńóśźż';

validName = false;
validLastname = false;
validLogin = false;
validPasswd = false;
validPasswd2 = false;
validFile = false;
setEventListeners()

function setEventListeners() {
    first_name = document.getElementById("name_input");
    last_name = document.getElementById("lastname_input");
    login = document.getElementById("login_input");
    password = document.getElementById("password_input");
    password2 = document.getElementById("password2_input");
    file = document.getElementById("file_input");

    first_name.addEventListener("input", (e) => validateName(first_name));
    last_name.addEventListener("input", (e) => validateLastname(last_name));
    login.addEventListener("input", (e) => validateLogin(login));
    password.addEventListener("input", (e) => validatePassword(password));
    password2.addEventListener("input", (e) => validateSecPassword(password, password2));
    file.addEventListener("input", (e) => validatePhoto(file));
}

function validateName(first_name) {
    const regex = /^[A-ZĄĆĘŁŃÓŚŹŻ][a-ząćęłńóśźż]+$/;
    if (first_name.value.match(regex)) {
        first_name.style.backgroundColor = "#00ff00";
        document.getElementById("name_err").style.display = "none"
        validName = true
    } else {
        first_name.style.backgroundColor = "#FF0000";
        document.getElementById("name_err").style.display = "initial"
        validName = false
    }
    validateSubmit()
}

function validateLastname(last_name) {
    const regex = /^[A-ZĄĆĘŁŃÓŚŹŻ][a-ząćęłńóśźż]+$/;
    if (last_name.value.match(regex)) {
        last_name.style.backgroundColor = "#00ff00";
        document.getElementById("surname_err").style.display = "none"
        validLastname = true
    } else {
        last_name.style.backgroundColor = "#FF0000";
        document.getElementById("surname_err").style.display = "initial"
        validLastname = false
    }
    validateSubmit()
}

function validateLogin(login) {
    const regex = /^[a-z]*$/;
    if (!login.value.match(regex)) {
        login.style.backgroundColor = "#FF0000";
        document.getElementById("log_taken_err").style.display = "none"
        document.getElementById("log_len_err").style.display = "none"
        document.getElementById("log_word_err").style.display = "initial"
        validLogin = false
        return
    } else if (login.value.length < 3 || login.value.length > 12) {
        login.style.backgroundColor = "#FF0000";
        document.getElementById("log_taken_err").style.display = "none"
        document.getElementById("log_word_err").style.display = "none"
        document.getElementById("log_len_err").style.display = "initial"
        validLogin = false
        return;
    } else {
        login.style.backgroundColor = "#00ff00";
        document.getElementById("log_taken_err").style.display = "none"
        document.getElementById("log_len_err").style.display = "none"
        document.getElementById("log_word_err").style.display = "none"
        validLogin = true
    }
    // var xhr = new XMLHttpRequest();
    // urlAdress = "https://infinite-hamlet-29399.herokuapp.com/check/" + login.value
    // xhr.open('GET', urlAdress);

    // xhr.onreadystatechange = function () {
    //     var DONE = 4;
    //     var OK = 200;
    //     if (xhr.readyState == DONE) {
    //         if (xhr.status == OK) {
    //             if (JSON.parse(xhr.response)[login.value] == "available") {
    //                 login.style.backgroundColor = "#00ff00";
    //                 document.getElementById("log_taken_err").style.display = "none"
    //                 document.getElementById("log_len_err").style.display = "none"
    //                 document.getElementById("log_word_err").style.display = "none"
    //                 validLogin = true
    //             } else {
    //                 login.style.backgroundColor = "#FF0000";
    //                 document.getElementById("log_word_err").style.display = "none"
    //                 document.getElementById("log_len_err").style.display = "none"
    //                 document.getElementById("log_taken_err").style.display = "initial"
    //                 validLogin = false
    //             }
    //         } else {
    //             alert("Wystąpił problem z bazą danych")
    //             validLogin = false
    //         }
    //     }
    // }
    // xhr.send(null);
    validateSubmit()
}

function validatePassword(password) {
    if (password.value.length < 8) {
        password.style.backgroundColor = "#FF0000";
        document.getElementById("passwd_err").style.display = "initial"
        validPasswd = false
    } else {
        password.style.backgroundColor = "#00ff00";
        document.getElementById("passwd_err").style.display = "none"
        validPasswd = true
    }//validatesecpasswd
    validateSubmit()
}

function validateSecPassword(password, password2) {
    if (password.value != password2.value) {
        password2.style.backgroundColor = "#FF0000";
        document.getElementById("passwd2_err").style.display = "initial"
        validPasswd2 = false
    } else {
        password2.style.backgroundColor = "#00ff00";
        document.getElementById("passwd2_err").style.display = "none"
        validPasswd2 = true
    }
    validateSubmit()
}

function validatePhoto(file) {
    file_name = file.files[0].name
    regex = /.(svg|png|jpg)$/i;
    if (file_name.match(regex)) {
        document.getElementById("photo_err").style.display = "none"
        validFile = true
    } else {
        document.getElementById("photo_err").style.display = "initial"
        validFile = false
    }
    validateSubmit()
}

function validateSubmit() {
    submit = document.getElementById("submit_button");
    if (validFile && validLastname && validLogin && validName && validPasswd && validPasswd2) {
        submit.style.cursor = "default";
        submit.style.pointerEvents = "initial";
    } else {
        submit.style.cursor = "not_allowed";
        submit.style.pointerEvents = "none";
    }
}
