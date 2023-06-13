function formatParams(params) {
    return ("?" +
        Object.keys(params)
            .map(function (key) {
            return key + "=" + encodeURIComponent(params[key]);
        })
            .join("&"));
}
export function handleMouseClick() {
    // Send the mouse click to the server
    const req = new XMLHttpRequest();
    req.addEventListener("load", (event) => {
        console.log("Mouse click successfully sent");
    });
    req.open("GET", "/ajax-data" + formatParams({ shouldFire: true }));
    req.setRequestHeader("Content-type", "application/json; charset=utf-8");
    req.send();
    console.log("Sending Mouse click");
}
export function handleMouseMove(event, xPos, yPos) {
    // On a MouseEvent, draw a dot where the cursor is.
    let x, y, pageX, pageY;
    if (event.ctrlKey != true) {
        return;
    }
    event = event || window.event; // IE-ism
    if (event.x != null &&
        event.y != null &&
        event.pageX != null &&
        event.pageY != null) {
        x = event.x;
        y = event.y;
        pageX = event.pageX;
        pageY = event.pageY;
    }
    else {
        console.log("Could not determine event location.");
        return;
    }
    // Add a dot to follow the cursor
    let dot = document.createElement("div");
    dot.className = "dot";
    dot.style.left = pageX + "px";
    dot.style.top = pageY + "px";
    //  document.body.appendChild(dot);
    if (event.currentTarget != null) {
        const currentTarget = event.currentTarget;
        const boundingRect = currentTarget.getBoundingClientRect();
        // Write the positions to the text boxes
        let xNew = x - (boundingRect.x + boundingRect.width / 2);
        xNew = xNew / (boundingRect.width / 2);
        xNew = xNew * -1.0;
        let yNew = y - (boundingRect.y + boundingRect.height / 2);
        yNew = yNew / (boundingRect.height / 2);
        xPos.value = xNew.toString();
        yPos.value = yNew.toString();
        // Send the co-ordinates to the server
        const req = new XMLHttpRequest();
        req.addEventListener("load", (event) => {
            console.log("Mouse movements successfully sent");
        });
        req.open("GET", "/ajax-data" + formatParams({ xPos: xNew, yPos: yNew }));
        req.setRequestHeader("Content-type", "application/json; charset=utf-8");
        req.send();
        console.log("Sending mouse movements");
    }
    else {
        console.log("Could not determine event target.");
    }
}
window.onload = () => {
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
    console.log("Sending Mouse click");
};
