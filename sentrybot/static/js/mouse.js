export function handleMouseMove(event, xPos, yPos) {
    // On a MouseEvent, draw a dot where the cursor is if it is inside the listening element.
    //
    // Write the x and y coordinates to xPos and yPos.
    let dot, pageX, pageY;
    event = event || window.event; // IE-ism
    // If pageX/Y aren't available and clientX/Y
    // are, calculate pageX/Y - logic taken from jQuery
    if (event.pageX != null && event.pageY != null) {
        pageX = event.pageX;
        pageY = event.pageY;
    }
    else {
        return;
    }
    // Add a dot to follow the cursor
    dot = document.createElement("div");
    dot.className = "dot";
    dot.style.left = pageX + "px";
    dot.style.top = pageY + "px";
    document.body.appendChild(dot);
    if (event.currentTarget != null) {
        const currentTarget = event.currentTarget;
        const boundingRect = currentTarget.getBoundingClientRect();
        if (xPos != null && yPos != null) {
            // Write the positions
            xPos.value = (boundingRect.x - pageX).toString();
            yPos.value = (boundingRect.y - pageY).toString();
        }
    }
}
