export function handleMouseMove(
  event: MouseEvent,
  xPos: HTMLInputElement,
  yPos: HTMLInputElement
) {
  // On a MouseEvent, draw a dot where the cursor is if it is inside the listening element.
  let x, y, pageX, pageY;

  event = event || window.event; // IE-ism

  if (
    event.x != null &&
    event.y != null &&
    event.pageX != null &&
    event.pageY != null
  ) {
    x = event.x;
    y = event.y;
    pageX = event.pageX;
    pageY = event.pageY;
  } else {
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
    const currentTarget = event.currentTarget as HTMLElement;
    const boundingRect = currentTarget.getBoundingClientRect();
    if (xPos != null && yPos != null) {
      // Write the positions
      xPos.value = (x - boundingRect.x).toString();
      yPos.value = (y - boundingRect.y).toString();
    }
  } else {
    console.log("Could not determine event target.");
  }
}
