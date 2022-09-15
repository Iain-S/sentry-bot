"use strict";
window.onload = function () {
    var box = document.querySelector(".etch-a-sketch");
    if (box == null) {
        console.log("Could not find etch-a-sketch element");
        return;
    }
    box.onmousemove = handleMouseMove;
    function handleMouseMove(event) {
        var dot, eventDoc, doc, body, pageX, pageY;
        event = event || window.event; // IE-ism
        // If pageX/Y aren't available and clientX/Y
        // are, calculate pageX/Y - logic taken from jQuery
        if (event.pageX != null && event.pageY != null) {
            pageX = event.pageX;
            pageY = event.pageY;
        }
        else if (event.clientX != null && event.clientY != null) {
            //         eventDoc = (event.target && event.target.ownerDocument) || document;
            eventDoc = document;
            doc = eventDoc.documentElement;
            body = eventDoc.body;
            pageX =
                event.clientX +
                    ((doc && doc.scrollLeft) || (body && body.scrollLeft) || 0) -
                    ((doc && doc.clientLeft) || (body && body.clientLeft) || 0);
            pageY =
                event.clientY +
                    ((doc && doc.scrollTop) || (body && body.scrollTop) || 0) -
                    ((doc && doc.clientTop) || (body && body.clientTop) || 0);
        }
        else {
            return;
        }
        // Add a dot to follow the cursor
        dot = document.createElement("div");
        dot.className = "dot";
        dot.style.left = pageX + "px";
        dot.style.top = pageY + "px";
        document.body.appendChild(dot);
    }
};
