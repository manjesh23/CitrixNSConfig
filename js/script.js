function openTab(evt, tabName) {
    var i, tabcontent, tablinks;
    tabcontent = document.getElementsByClassName("tabcontent");
    for (i = 0; i < tabcontent.length; i++) {
        tabcontent[i].style.display = "none";
    }
    tablinks = document.getElementsByClassName("tablinks");
    for (i = 0; i < tablinks.length; i++) {
        tablinks[i].className = tablinks[i].className.replace(" active", "");
    }
    document.getElementById(tabName).style.display = "block";
    evt.currentTarget.className += " active";
}


function analyze() {
    let nsconf = document.getElementById('nsconf').files[0]
    let reader = new FileReader()
    reader.onload = function() {
        let rawnsconfig = this.result.split("/r/n");
        for (var line = 0; line < rawnsconfig.length; line++) {
            let linenscount = rawnsconfig[line]
            if (linenscount.length > 2) {
                //rawnsconfig output here //
                document.getElementById("nsconfigout").style.display = 'block'
                document.getElementById("nsconfigout").innerText = rawnsconfig
                    //basicnsconfig output here
                document.getElementById("basicnsconfigout").style.display = 'block'
                document.getElementById("basicnsconfigout").innerText = rawnsconfig.match("/Build/g")
            } else {
                alert("Invalid ns.conf file")
            }
        }
    }
    reader.readAsText(nsconf)
    reader.onerror = (event) => {
        alert(event.target.error.name);
    }
}