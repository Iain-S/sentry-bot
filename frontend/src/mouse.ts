function formatParams(params: any): string {
  return (
    "?" +
    Object.keys(params)
      .map(function (key) {
        return key + "=" + encodeURIComponent(params[key]);
      })
      .join("&")
  );
}
export function handleMouseClick() {
  // Send the mouse click to the server
  const req = new XMLHttpRequest();
  req.addEventListener("load", (event: ProgressEvent) => {
    console.log("Mouse click successfully sent");
  });
  req.open("GET", "/ajax-data" + formatParams({ shouldFire: true }));

  req.setRequestHeader("Content-type", "application/json; charset=utf-8");

  req.send();
  console.log("Sending Mouse click");
}

export function handleMouseMove(
  event: MouseEvent,
  xPos: HTMLInputElement,
  yPos: HTMLInputElement
) {
  // On a MouseEvent, draw a dot where the cursor is.
  let x, y, pageX, pageY;

  if (event.ctrlKey != true) {
    return;
  }

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
  //  document.body.appendChild(dot);

  if (event.currentTarget != null) {
    const currentTarget = event.currentTarget as HTMLElement;
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
    req.addEventListener("load", (event: ProgressEvent) => {
      console.log("Mouse movements successfully sent");
    });
    req.open("GET", "/ajax-data" + formatParams({ xPos: xNew, yPos: yNew }));

    req.setRequestHeader("Content-type", "application/json; charset=utf-8");

    req.send();
    console.log("Sending mouse movements");
  } else {
    console.log("Could not determine event target.");
  }
}

export function handleKeyEvent(event: KeyboardEvent) {
  console.log("Key event", event);

  const req = new XMLHttpRequest();
  req.addEventListener("load", (event: ProgressEvent) => {
    console.log("Key press received by server");
  });

  let params = null;

  if (event.key == " ") {
    params = { shouldFire: true };
  } else if (event.key == "ArrowLeft") {
    params = {
      xNudge: -0.1,
      yNudge: 0.0,
    };
  } else if (event.key == "ArrowRight") {
    params = {
      xNudge: 0.1,
      yNudge: 0.0,
    };
  } else if (event.key == "ArrowUp") {
    params = {
      xNudge: 0.0,
      yNudge: -0.1,
    };
  } else if (event.key == "ArrowDown") {
    params = {
      xNudge: 0.0,
      yNudge: 0.1,
    };
  } else {
    return;
  }
  if (params == null) {
    return;
  }

  req.open("GET", "/ajax-data" + formatParams(params));
  req.setRequestHeader("Content-type", "application/json; charset=utf-8");

  req.send();
}
