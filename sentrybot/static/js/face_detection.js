import { handleMouseMove, handleMouseClick } from "./mouse.js";
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
    box.onmousemove = (event) => {
        return handleMouseMove(event, xPos, yPos);
    };
    box.onclick = (event) => {
        return handleMouseClick(event, "click");
    };
    box.onmousedown = (event) => {
        return handleMouseClick(event, "down");
    };
};
