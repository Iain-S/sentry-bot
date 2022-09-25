interface MyObject {
  theDate: string;
}

window.onload = () => {
  const button = document.querySelector(
    "#update-time"
  ) as HTMLButtonElement | null;

  if (button == null) {
    console.log("Could not find update-time");
    return;
  }

  button.addEventListener("click", (e: Event) => {
    const req = new XMLHttpRequest();
    req.addEventListener("load", (event: ProgressEvent) => {
      const input = document.querySelector(
        "#the-time"
      ) as HTMLInputElement | null;
      if (input == null) {
        console.log("Could not find the-time");
        return;
      }

      const obj: MyObject = JSON.parse(req.response);

      input.value = obj.theDate;
    });
    req.open("GET", "/ajax-data");
    req.send();
  });
};
