import { sendDataToServer } from "./funcs.js";

document.addEventListener("DOMContentLoaded", function () {
    //общие элементы
    const spinner = document.getElementById("Spinner");

    //кнопки меню
    const btnContentAuth = document.getElementById("BtnContentAuth");
    const btnContentReg = document.getElementById("BtnContentReg");
    const btnContentRestorePassword = document.getElementById(
        "BtnContentRestorePassword"
    );

    //элементы контента авторизация
    const contentAuth = document.getElementById("ContentAuth");
    const inputEmail = document.getElementById("InputEmail");
    const inputPassword = document.getElementById("InputPassword");
    const checkbox = document.getElementById("CheckBoxPassword");
    const btnAuth = document.getElementById("BtnAuth");
    let alertErrorAuth;

    //элементы контента регистрация
    const contentReg = document.getElementById("ContentReg");
    let alertSuccessReg;
    let alertErrorReg;
    let inputToken;
    let btnRequestUserData;
    let dataCard;
    let inputPassword1;
    let inputPassword2;
    let btnReg;

    //элементы контента восстановления пароля
    const contentRestorePassword = document.getElementById(
        "ContentRestorePassword"
    );
    let inputTokenForRestorePassword;
    let inputFIO;
    let inputNewPassword1;
    let inputNewPassword2;
    let btnRestorePassword;
    let alertSuccessRestorePassword;
    let alertErrorRestorePassword;

    //функции для создания контента
    function createsAlertError(textError) {
        const alert = document.createElement("div");
        alert.setAttribute("id", "AlertDanger");
        alert.setAttribute("class", "alert alert-danger mt-2");
        alert.setAttribute("role", "alert");
        alert.textContent = textError;
        return alert;
    }

    function createsAlertSuccess(textSuccess) {
        const alert = document.createElement("div");
        alert.setAttribute("id", "AlertSuccess");
        alert.setAttribute("class", "alert alert-success mt-2");
        alert.setAttribute("role", "alert");
        alert.textContent = textSuccess;
        return alert;
    }

    function createsInputElement(id, text) {
        const element = document.createElement("div");
        element.setAttribute("class", "form-floating mt-1");
        const input = document.createElement("input");
        input.setAttribute("id", id);
        input.setAttribute("class", "form-control");
        input.setAttribute("type", "text");
        input.setAttribute("placeholder", ".");
        element.appendChild(input);
        const label = document.createElement("label");
        label.setAttribute("for", id);
        label.textContent = text;
        element.appendChild(label);
        return element;
    }

    function createsTextButton(id, text) {
        const button = document.createElement("button");
        button.setAttribute("id", id);
        button.setAttribute("class", "btn btn-link");
        button.setAttribute("type", "button");
        button.textContent = text;
        return button;
    }

    function createsDataCard(listData) {
        const card = document.createElement("div");
        card.setAttribute("id", "Card");
        card.setAttribute("style", "text-align: start");
        const ul = document.createElement("ul");
        ul.setAttribute("class", "list-group list-group-flush");
        card.appendChild(ul);
        function createsLiElement(el) {
            var li = document.createElement("li");
            li.setAttribute("class", "list-group-item");
            li.textContent = el;
            ul.appendChild(li);
        }
        listData.forEach(createsLiElement);
        return card;
    }

    function createsInputElements(id1, id2) {
        const inputPassword1 = document.createElement("input");
        inputPassword1.setAttribute("id", id1);
        inputPassword1.setAttribute("class", "form-control mt-2");
        inputPassword1.setAttribute("type", "text");
        inputPassword1.setAttribute("placeholder", "Придумайте пароль");
        inputPassword1.setAttribute("aria-label", "default input example");
        inputPassword1.setAttribute(
            "style",
            "margin-bottom: -1px; border-bottom-right-radius: 0; border-bottom-left-radius: 0"
        );
        const inputPassword2 = document.createElement("input");
        inputPassword2.setAttribute("id", id2);
        inputPassword2.setAttribute("class", "form-control");
        inputPassword2.setAttribute("type", "password");
        inputPassword2.setAttribute("placeholder", "Повторите пароль");
        inputPassword2.setAttribute("aria-label", "default input example");
        inputPassword2.setAttribute(
            "style",
            "margin-bottom: 10px; border-bottom-right-radius: 0; border-bottom-left-radius: 0"
        );
        return [inputPassword1, inputPassword2];
    }

    function createsButton(id, text) {
        const button = document.createElement("button");
        button.setAttribute("id", id);
        button.setAttribute("class", "w-100 btn btn-lg btn-primary mt-3");
        button.setAttribute("type", "submit");
        button.textContent = text;
        return button;
    }

    //функции событий
    function showContentAuth() {
        document.title = "Вход в систему - Авторизация";
        //меняю состояние кнопок меню
        btnContentAuth.setAttribute(
            "class",
            "btn btn-lg btn-outline-secondary disabled"
        );
        btnContentReg.setAttribute("class", "btn btn-lg btn-secondary");
        //скрываю контент регистрации и восстановления пароля, открываю контент авторизации
        contentReg.setAttribute("class", "d-none");
        contentRestorePassword.setAttribute("class", "d-none");
        contentAuth.setAttribute("class", "");
    }

    function showContentReg() {
        document.title = "Вход в систему - Регистрация";
        if (inputToken === undefined) {
            //открываю контент регистрации первый раз
            inputToken = createsInputElement("InputToken", "Токен приглашения");
            contentReg.appendChild(inputToken);
            btnRequestUserData = createsTextButton(
                "BtnRequestUserData",
                "Запросить данные"
            );
            contentReg.appendChild(btnRequestUserData);
        } else {
            btnRequestUserData = document.getElementById("BtnRequestUserData");
            btnRequestUserData.removeEventListener("click", showUserData);
        }
        //меняю состояние кнопок меню
        btnContentReg.setAttribute(
            "class",
            "btn btn-lg btn-outline-secondary disabled"
        );
        btnContentAuth.setAttribute("class", "btn btn-lg btn-secondary");
        //скрываю контент авторизации и восстановления пароля, открываю контент регистрации
        contentAuth.setAttribute("class", "d-none");
        contentRestorePassword.setAttribute("class", "d-none");
        contentReg.setAttribute("class", "");
        //событие получения данных пользователя при нажатии кнопки
        btnRequestUserData.addEventListener("click", showUserData);
    }

    function showUserData() {
        //отключаю кнопки
        btnRequestUserData.disabled = true;
        btnContentAuth.disabled = true;
        //spinner на время выполнения события
        spinner.classList.remove("d-none");
        //удаляю соответствующие элементы
        if (alertSuccessReg !== undefined) {
            contentReg.removeChild(alertSuccessReg);
            alertSuccessReg = undefined;
        }
        if (alertErrorReg !== undefined) {
            contentReg.removeChild(alertErrorReg);
            alertErrorReg = undefined;
        }
        if (dataCard !== undefined) {
            contentReg.removeChild(dataCard);
            contentReg.removeChild(inputPassword1);
            contentReg.removeChild(inputPassword2);
            contentReg.removeChild(btnReg);
            dataCard = undefined;
            btnReg.removeEventListener("click", registersUser);
        }
        //отправляю запрос на сервер
        const valueInputToken = document.getElementById("InputToken").value;
        const dataToSend = {
            invitation_token: valueInputToken,
        };
        sendDataToServer("/data_for_user_registration", dataToSend)
            .then((response) => {
                return response.json();
            })
            .then((responseJson) => {
                if (responseJson.hasOwnProperty("error")) {
                    const textError = responseJson.error.name;
                    alertErrorReg = createsAlertError(textError);
                    contentReg.appendChild(alertErrorReg);
                }
                if (responseJson.hasOwnProperty("success")) {
                    const data = responseJson.success.value;
                    const fio = data[0] + " " + data[1] + " " + data[2];
                    const email = data[3];
                    const company = data[4];
                    dataCard = createsDataCard([fio, email, company]);
                    const inputsPassword = createsInputElements(
                        "InputPassword1",
                        "InputPassword2"
                    );
                    inputPassword1 = inputsPassword[0];
                    inputPassword2 = inputsPassword[1];
                    btnReg = createsButton("BtnReg", "Зарегистрироваться");
                    contentReg.appendChild(dataCard);
                    contentReg.appendChild(inputPassword1);
                    contentReg.appendChild(inputPassword2);
                    contentReg.appendChild(btnReg);
                    btnReg.addEventListener("click", registersUser);
                    btnReg.valueInputToken = valueInputToken;
                }
            })
            .finally(() => {
                btnRequestUserData.disabled = false;
                btnContentAuth.disabled = false;
                spinner.classList.add("d-none");
            });
    }

    function registersUser(evt) {
        //отключаю кнопки
        btnReg.disabled = true;
        btnRequestUserData.disabled = true;
        btnContentAuth.disabled = true;
        //spinner на время выполнения события
        spinner.classList.remove("d-none");
        //удаляю соответствующие элементы
        if (alertSuccessReg !== undefined) {
            contentReg.removeChild(alertSuccessReg);
            alertSuccessReg = undefined;
        }
        if (alertErrorReg !== undefined) {
            contentReg.removeChild(alertErrorReg);
            alertErrorReg = undefined;
        }
        //валидирую пароли
        const password = inputPassword2.value;
        if (password !== inputPassword1.value) {
            alertErrorReg = createsAlertError("Пароли не совпадают");
            contentReg.appendChild(alertErrorReg);
            btnReg.disabled = false;
            btnRequestUserData.disabled = false;
            btnContentAuth.disabled = false;
            spinner.classList.add("d-none");
            return;
        }
        //отправляю запрос на сервер
        const dataToSend = {
            invitation_token: evt.currentTarget.valueInputToken,
            password: password,
        };
        sendDataToServer("/user_registration", dataToSend)
            .then((response) => {
                return response.json();
            })
            .then((responseJson) => {
                if (responseJson.hasOwnProperty("error")) {
                    const textError = responseJson.error.name;
                    alertErrorReg = createsAlertError(textError);
                    contentReg.appendChild(alertErrorReg);
                }
                if (responseJson.hasOwnProperty("success")) {
                    const textSuccess = "Вы успешно зарегистрировались!";
                    alertSuccessReg = createsAlertSuccess(textSuccess);
                    contentReg.appendChild(alertSuccessReg);
                }
            })
            .finally(() => {
                btnReg.disabled = false;
                btnRequestUserData.disabled = false;
                btnContentAuth.disabled = false;
                spinner.classList.add("d-none");
            });
    }

    function showPassword() {
        if (checkbox.checked) {
            inputPassword.setAttribute("type", "text");
        } else {
            inputPassword.setAttribute("type", "password");
        }
    }

    function authorizesUser() {
        //отключаю кнопки
        btnAuth.disabled = true;
        btnContentReg.disabled = true;
        btnContentRestorePassword.disabled = true;
        //spinner на время выполнения события
        spinner.classList.remove("d-none");
        if (alertErrorAuth !== undefined) {
            contentAuth.removeChild(alertErrorAuth);
            alertErrorAuth = undefined;
        }
        //отправляю запрос на сервер
        const dataToSend = {
            email: inputEmail.value,
            password: inputPassword.value,
        };
        sendDataToServer("/", dataToSend)
            .then((response) => {
                return response.json();
            })
            .then((responseJson) => {
                if (responseJson.hasOwnProperty("error")) {
                    const textError = responseJson.error.name;
                    alertErrorAuth = createsAlertError(textError);
                    contentAuth.appendChild(alertErrorAuth);
                }
                if (responseJson.hasOwnProperty("success")) {
                    document.location.href = "/app";
                }
            })
            .finally(() => {
                btnAuth.disabled = false;
                btnContentReg.disabled = false;
                btnContentRestorePassword.disabled = false;
                spinner.classList.add("d-none");
            });
    }

    function showContentRestorePassword() {
        document.title = "Вход в систему - Восстановление пароля";
        if (inputTokenForRestorePassword === undefined) {
            //открываю контент восстановления пароля первый раз
            inputTokenForRestorePassword = createsInputElement(
                "InputTokenForRestorePassword",
                "Токен приглашения"
            );
            contentRestorePassword.appendChild(inputTokenForRestorePassword);
            inputFIO = createsInputElement("InputFIO", "ФИО");
            contentRestorePassword.appendChild(inputFIO);
            const inputsPassword = createsInputElements(
                "InputNewPassword1",
                "InputNewPassword2"
            );
            inputNewPassword1 = inputsPassword[0];
            inputNewPassword2 = inputsPassword[1];
            contentRestorePassword.appendChild(inputNewPassword1);
            contentRestorePassword.appendChild(inputNewPassword2);
            btnRestorePassword = createsButton(
                "BtnRestorePassword",
                "Восстановить пароль"
            );
            contentRestorePassword.appendChild(btnRestorePassword);
        } else {
            btnRestorePassword = document.getElementById("BtnRestorePassword");
            btnRestorePassword.removeEventListener("click", restoresPassword);
        }
        //меняю состояние кнопок меню
        btnContentAuth.setAttribute("class", "btn btn-lg btn-secondary");
        btnContentReg.setAttribute("class", "btn btn-lg btn-secondary");
        //скрываю контент регистрации и авторизации, открываю контент восстановления пароля
        contentReg.setAttribute("class", "d-none");
        contentAuth.setAttribute("class", "d-none");
        contentRestorePassword.setAttribute("class", "");
        btnRestorePassword.addEventListener("click", restoresPassword);
    }

    function restoresPassword() {
        //отключаю кнопку
        btnRestorePassword.disabled = true;
        btnContentAuth.disabled = true;
        btnContentReg.disabled = true;
        //spinner на время выполнения события
        spinner.classList.remove("d-none");
        //удаляю соответствующие элементы
        if (alertErrorRestorePassword !== undefined) {
            contentRestorePassword.removeChild(alertErrorRestorePassword);
            alertErrorRestorePassword = undefined;
        }
        if (alertSuccessRestorePassword !== undefined) {
            contentRestorePassword.removeChild(alertSuccessRestorePassword);
            alertSuccessRestorePassword = undefined;
        }
        //валидирую пароли
        const password = inputNewPassword2.value;
        if (password !== inputNewPassword1.value) {
            alertErrorRestorePassword = createsAlertError(
                "Пароли не совпадают"
            );
            contentRestorePassword.appendChild(alertErrorRestorePassword);
            btnRestorePassword.disabled = false;
            btnContentAuth.disabled = false;
            btnContentReg.disabled = false;
            spinner.classList.add("d-none");
            return;
        }
        //отправляю запрос на сервер
        const dataToSend = {
            invitation_token: document.getElementById(
                "InputTokenForRestorePassword"
            ).value,
            user_name: document.getElementById("InputFIO").value,
            new_password: password,
        };
        sendDataToServer("/restore_user_password", dataToSend)
            .then((response) => {
                return response.json();
            })
            .then((responseJson) => {
                if (responseJson.hasOwnProperty("error")) {
                    const textError = responseJson.error.name;
                    alertErrorRestorePassword = createsAlertError(textError);
                    contentRestorePassword.appendChild(
                        alertErrorRestorePassword
                    );
                }
                if (responseJson.hasOwnProperty("success")) {
                    const textSuccess = "Пароль успешно восстановлен!";
                    alertSuccessRestorePassword =
                        createsAlertSuccess(textSuccess);
                    contentRestorePassword.appendChild(
                        alertSuccessRestorePassword
                    );
                }
            })
            .finally(() => {
                btnRestorePassword.disabled = false;
                btnContentAuth.disabled = false;
                btnContentReg.disabled = false;
                spinner.classList.add("d-none");
            });
    }

    //возможные события после загрузки страницы
    btnContentAuth.addEventListener("click", showContentAuth);
    btnContentReg.addEventListener("click", showContentReg);
    checkbox.addEventListener("click", showPassword);
    btnAuth.addEventListener("click", authorizesUser);
    btnContentRestorePassword.addEventListener(
        "click",
        showContentRestorePassword
    );
});
