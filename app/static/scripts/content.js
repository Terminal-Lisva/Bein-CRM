import { sendDeleteRequest } from "./funcs.js";

document.addEventListener("DOMContentLoaded", function () {
    //Открывает вкладку меню
    function openElementSubmenu() {
        const uri_path = document.location.pathname;
        const accordion = document.getElementById("accordion-submenu");
        const elementsSubmenu = accordion.querySelectorAll(".sidebar-submenu");
        elementsSubmenu.forEach((element) => {
            const items = element.querySelectorAll(".item-sidebar");
            items.forEach((item) => {
                const href = item.getAttribute("href");
                if (href === uri_path) {
                    element.classList.add("show");
                    item.style.backgroundColor = "rgb(33, 37, 41)";
                    return;
                }
            });
        });
    }
    openElementSubmenu();

    //Сбросывает авторизацию
    const btnExit = document.getElementById("btn-exit");
    function exit() {
        sendDeleteRequest("/remove_user_authorization")
            .then((response) => {
                return response.json();
            })
            .then((responseJson) => {
                console.log(responseJson);
                if (responseJson.hasOwnProperty("success")) {
                    document.location.href = "/";
                }
            });
    }
    btnExit.addEventListener("click", exit);
});
