interface MyObject {
  aString: string;
  aNumber: number;
}

window.onload = () => {
  const req = new XMLHttpRequest();
  req.addEventListener("load", (event: ProgressEvent) => {
    const obj: MyObject = JSON.parse(req.response);
    console.log(obj.aString);
    console.log(obj.aNumber);
  });
  req.open("GET", "/ajax-data");
  req.send();
};
