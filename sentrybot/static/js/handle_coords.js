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

function toggle_mode(){
    console.log('Toggle auto/manual')
    const button = document.querySelectorAll(".mode");
    const currentSymbol = button.innerHTML;
    console.log(currentSymbol)
    // Define the symbols for toggle
    const symbol1 = '&#128663;'; // Hex code for a checkmark symbol
    const symbol2 = '&#129302;'; // Hex code for a cross symbol

    // Toggle the symbol
    if (currentSymbol === symbol1) {
        button.innerHTML = symbol2;
    } else {
        button.innerHTML = symbol1;
    }
    console.log(currentSymbol)
}


var widescreen = true;
function enlarge() {
    const selector = '.videocontainer img';
    const width = widescreen ? '150vmin' : '70vmin';
    const elements = document.querySelectorAll(selector);
    elements.forEach(element => {
        element.style.width = width;
    });
    widescreen = !widescreen;
}
