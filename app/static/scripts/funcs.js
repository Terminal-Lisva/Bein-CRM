//функции для отправки данных на сервер
async function sendDataToServer(uri, method, dataToSend = "") {
    const response = await fetch(uri, {
        method: method,
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(dataToSend),
    });
    return response;
}

//экспорт
export { sendDataToServer };
