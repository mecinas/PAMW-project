
//Mój własny sleep
// const sleep = ms => new Promise(res => setTimeout(res, ms))
const startString = "Zmiana statusu paczki: "
const endString = " na status: "
loadNotifications();

async function loadNotifications() {
    var xhr = new XMLHttpRequest();
    xhr.onreadystatechange = function () {
        var DONE = 4;
        var OK = 200;
        if (xhr.readyState == DONE) {
            if (xhr.status == OK) {
                var ul = document.getElementById("list");
                var li = document.createElement("li");
                li.appendChild(document.createTextNode(JSON.parse(xhr.response)["notification"]));
                ul.appendChild(li);
                loadNotifications()
            }
        }
    }
    xhr.open("GET", "/sender/notifications/update", true)
    xhr.timeout = 15000
    xhr.ontimeout = function () { console.error("Timeout"); setTimeout(loadNotifications, 1000) };
    xhr.send()
}
