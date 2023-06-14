"use strict";
function streamImages() {
    const cameraImage = document.getElementById("latest-image-id");
    const req = new XMLHttpRequest();
    req.addEventListener("load", (event) => {
        console.log("Image request successfully received");
        console.log(event);
        if (event.target != null) {
            const target = event.target;
            const response = target.response;
            var reader = new FileReader();
            reader.onloadend = function () {
                if (cameraImage != null) {
                    cameraImage.src = "" + reader.result;
                }
            };
            reader.readAsDataURL(response);
        }
    });
    req.responseType = "blob";
    req.open("GET", "/latest-image.jpg");
    req.setRequestHeader("Content-type", "application/json; charset=utf-8");
    req.send();
    setTimeout(streamImages, 1.0);
}
window.onload = () => {
    streamImages();
};
