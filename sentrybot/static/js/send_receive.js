"use strict";
window.onload = () => {
    const req = new XMLHttpRequest();
    req.addEventListener("load", (event) => {
        const obj = JSON.parse(req.response);
        console.log(obj.aString);
        console.log(obj.aNumber);
    });
    req.open("GET", "/ajax-data");
    req.send();
};
