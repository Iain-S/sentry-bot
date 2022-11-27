import { handleMouseMove, handleMouseClick } from "./mouse";

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

  let enableHandler: Boolean = false;
  window.setInterval(() => {
    enableHandler = true;
  }, 100);
  box.onmousemove = (event: MouseEvent) => {
    if (enableHandler) {
      handleMouseMove(event, xPos, yPos);
      // Don't handle any more mouse movements until re-enabled
      enableHandler = false;
    }
  };
  box.onclick = () => {
    return handleMouseClick();
  };
};
