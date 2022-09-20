import { handleMouseMove } from "./mouse";

window.onload = () => {
  const xPos = document.querySelector("#xpos") as HTMLInputElement | null;
  const yPos = document.querySelector("#ypos") as HTMLInputElement | null;

  if (yPos == null || xPos == null) {
    console.log("Could not find one or more of xPos and yPos");
    return;
  }

  const box = document.querySelector(".etch-a-sketch") as HTMLDivElement | null;

  if (box == null) {
    console.log("Could not find etch-a-sketch element");
    return;
  }
  box.onmousemove = (event: MouseEvent) => {
    return handleMouseMove(event, xPos, yPos);
  };
};
