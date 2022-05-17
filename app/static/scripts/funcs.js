//функции для отправки данных на сервер
async function sendDeleteRequest(uri) {
    const response = await fetch(uri, {
        method: "DELETE",
    });
    return response;
}

//экспорт
export { sendDeleteRequest };
