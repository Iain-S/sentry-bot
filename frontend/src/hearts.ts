function fire_hearts() {
    // Call the frame function to start the animation
    callFunctionMultipleTimes(30);
    // var id = setInterval(frame, 10);
    clearInterval(id);
    frame();
}

var id;

function frame() {
    var current = Date.now();
    var deltaTime = current - before;
    before = current;
    id = setInterval(frame, 3);
    for (i in hearts) {
        var heart = hearts[i];
        heart.time -= deltaTime;

        if (heart.time > 0) {

            // Add random movement
            var randomX = Math.floor(Math.random() * 20) - 10;
            var randomY = Math.floor(Math.random() * 20) - 10;

            // Adjust the multiplier for x-direction movement
            var xMovementMultiplier = 0.5; // Modify this value to control the swinging motion
            //
            heart.y -= speed;
            heart.style.top = heart.y + "px";
            heart.style.left = heart.x + heart.direction * heart.bound * Math.sin(heart.y * heart.scale / 30) / heart.y * 200 + "px";

            // Add swinging motion
            var rotationAngle = Math.sin(heart.y * heart.scale / 100) * 20; // *20 Adjust this value to control the swinging amplitude
            heart.style.transform = "scale(" + heart.scale + "," + heart.scale + ") rotate(" + rotationAngle + "deg)";
        }
        else {
            heart.parentNode.removeChild(heart);
            hearts.splice(i, 1);
        }
    }
}