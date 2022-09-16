import { sum } from "./sum.js";
window.onload = () => {
    console.log(sum(5, 4));
    const xPos = document.querySelector("#xpos");
    const yPos = document.querySelector("#ypos");
    if (yPos == null || xPos == null) {
        console.log("Could not find one or more of xPos and yPos");
    }
    const box = document.querySelector(".etch-a-sketch");
    if (box == null) {
        console.log("Could not find etch-a-sketch element");
        return;
    }
    box.onmousemove = handleMouseMove;
    function handleMouseMove(event) {
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
        if (box != null) {
            const boundingRect = box.getBoundingClientRect();
            if (xPos != null && yPos != null) {
                // Write the positions
                xPos.value = (boundingRect.x - pageX).toString();
                yPos.value = (boundingRect.y - pageY).toString();
            }
        }
    }
};
