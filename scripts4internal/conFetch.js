function hideDiv() {
    var x = document.getElementById("divElement");
    if (x.style.display === "none") {
        x.style.display = "block";
    } else {
        x.style.display = "none";
    }
}