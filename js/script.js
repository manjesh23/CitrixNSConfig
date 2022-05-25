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
    document.getElementById("nsconfmenu").style.display = 'block'
    let nsconf = document.getElementById('nsconf').files[0]
    let reader = new FileReader()
    reader.onload = function() {
        let rawnsconfig = this.result.split("/r/n")
        for (var line = 0; line < rawnsconfig.length; line++) {
            let originalnsconf = rawnsconfig[line]
            if (originalnsconf.length > 2) {
                //rawnsconfig output here //
                document.getElementById("nsconfigout").innerText = originalnsconf
                    //basicnsconfig output here
                    //system details
                document.getElementById("nsversion").innerText = originalnsconf.match(/NS.+Build.+/g)[0]
                document.getElementById("nsip").innerText = originalnsconf.match(/ns\sconfig\s.IPAddress.+/g)[0].split(" ")[3] + " / " + originalnsconf.match(/ns\sconfig\s.IPAddress.+/g)[0].split(" ")[5]
                document.getElementById("nsfeatures").innerText = originalnsconf.match(/\sfeature.+/g)[0].split(" ").slice(2)
                document.getElementById("nsmode").innerText = originalnsconf.match(/ns\smode.+/g)[0].split(" ").slice(2)
                document.getElementById("nshostname").innerText = originalnsconf.match(/ns\shostName.+/g)[0].split(" ")[2]
                if (originalnsconf.match(/HA\snode.+/g) != null) {
                    document.getElementById("nshanode").innerText = originalnsconf.match(/HA\snode.+/g)[0].split(" ")[3]
                }
                document.getElementById("nstimezone").innerText = originalnsconf.match(/-timezone.+/g)[0].split(" ")[1]
                    //load balancing realted details
                    // loadbalancing virtual server info
                let rawlbvserver = originalnsconf.match(/add\slb\svserver.+/g)
                if (rawlbvserver.length > 0) {
                    var lbvservertable = ""
                    for (var lbvserver = 0; lbvserver < rawlbvserver.length; lbvserver++) {
                        let lbpersistence = rawlbvserver[lbvserver].match(new RegExp("persistenceType" + '\\s(\\w+)'))
                        if (lbpersistence != null) {
                            lbpersistence = lbpersistence[1]
                        }
                        let lblbmethod = rawlbvserver[lbvserver].match(new RegExp("lbMethod" + '\\s(\\w+)'))
                        if (lblbmethod != null) {
                            lblbmethod = lblbmethod[1]
                        }
                        let lbbackupLBMethod = rawlbvserver[lbvserver].match(new RegExp("backupLBMethod" + '\\s(\\w+)'))
                        if (lbbackupLBMethod != null) {
                            lbbackupLBMethod = lbbackupLBMethod[1]
                        }
                        lbvservertable += rawlbvserver[lbvserver].split(" ")[3] + "</td><td>" + rawlbvserver[lbvserver].split(" ")[4] + "</td><td>" + rawlbvserver[lbvserver].split(" ")[5] + "</td><td>" + rawlbvserver[lbvserver].split(" ")[6] + "</td><td>" + lbpersistence + "</td><td>" + lblbmethod + "</td><td>" + lbbackupLBMethod + "</td></tr><td>"
                    }
                    document.getElementById("lbvserver").innerHTML += "<br><br><table><tr><th>LB vServer Name</th><th>Protocol</th><th>LB VIP</th><th>VIP Port</th><th>persistenceType</th><th>lbMethod</th><th>backupLBMethod</th></tr><tr><td>" + lbvservertable + "</table>"
                }
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