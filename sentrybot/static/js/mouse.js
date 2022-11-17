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
    document.body.appendChild(dot);
    if (event.currentTarget != null) {
        const currentTarget = event.currentTarget;
        const boundingRect = currentTarget.getBoundingClientRect();
        // Write the positions to the text boxes
        xPos.value = (x - boundingRect.x).toString();
        yPos.value = (y - boundingRect.y).toString();
        // Send the co-ordinates to the server
        const req = new XMLHttpRequest();
        req.addEventListener("load", (event) => {
            console.log("Mouse movements received");
        });
        req.open("POST", "/ajax-data");
        const params = JSON.stringify({
            xPos: x - boundingRect.x,
            yPos: y - boundingRect.y,
        });
        req.setRequestHeader("Content-type", "application/json; charset=utf-8");
        req.send(params);
        console.log("Mouse movements sent");
    }
    else {
        console.log("Could not determine event target.");
    }
}
