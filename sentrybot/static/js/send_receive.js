"use strict";
window.onload = () => {
    const button = document.querySelector("#update-time");
    if (button == null) {
        console.log("Could not find update-time");
        return;
    }
    button.addEventListener("click", (e) => {
        const req = new XMLHttpRequest();
        req.addEventListener("load", (event) => {
            const input = document.querySelector("#the-time");
            if (input == null) {
                console.log("Could not find the-time");
                return;
            }
            const obj = JSON.parse(req.response);
            input.value = obj.theDate;
        });
        req.open("GET", "/ajax-data");
        req.send();
    });
};
