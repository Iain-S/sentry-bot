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

function fire() {
    console.log('Fire on target!')
    xpos = document.getElementById("xpos").value
    ypos = document.getElementById("ypos").value
    var params = new URLSearchParams();
    params.append('xPos', xpos);
    params.append('yPos', ypos);
    params.append('shouldFire', true)
    var url = '/set_desired_coords?' + params.toString();
    fetch(url)
        .then(response => response.text())
        .then(text => console.log(text))
}

function hideDiv() {
    const elementToHide = document.querySelector('.top');
    if (elementToHide.style.display == 'block') {
        elementToHide.style.display = 'none';
    } else {
        elementToHide.style.display = 'block';
    }

}

function enlarge() {
    const image = document.querySelector('.videocontainer img');
    console.log(image.style.width)
    if (image.style.width != "70vmin") {
        image.style.width = "70vmin";
    } else {
        image.style.width = "150vmin";
    }
    console.log(image.style.width)
    console.log("end")
}
