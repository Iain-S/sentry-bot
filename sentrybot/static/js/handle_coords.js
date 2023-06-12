function testFunc() {
    xpos = document.getElementById("xpos").value
    ypos = document.getElementById("ypos").value
    var params = new URLSearchParams();
    params.append('xPos', xpos);
    params.append('yPos', ypos);
    var url = '/set_desired_coords?' + params.toString();
    fetch(url)
    .then(response => response.text())
    .then(text => console.log(text))
}