import { sendDeleteRequest } from "./funcs.js";

document.addEventListener("DOMContentLoaded", function () {
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
