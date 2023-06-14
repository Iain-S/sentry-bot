import { handleMouseMove, handleMouseClick, handleKeyEvent } from "./mouse.js";
window.onload = () => {
    const xPos = document.querySelector("#xpos");
    const yPos = document.querySelector("#ypos");
    if (yPos == null || xPos == null) {
        console.log("Could not find one or more of xPos and yPos");
        return;
    }
    const box = document.querySelector(".etch-a-sketch");
    if (box == null) {
        console.log("Could not find etch-a-sketch element");
        return;
    }
    let enableHandler = false;
    window.setInterval(() => {
        enableHandler = true;
    }, 100);
    box.onmousemove = (event) => {
        if (enableHandler) {
            handleMouseMove(event, xPos, yPos);
            // Don't handle any more mouse movements until re-enabled
            enableHandler = false;
        }
    };
    box.onclick = () => {
        return handleMouseClick();
    };
    // Key presses
    window.addEventListener("keydown", handleKeyEvent);
};
