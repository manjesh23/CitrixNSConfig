import os

lbvip = os.popen(
    "awk '/^add lb vserver/{printf \"%s|%s|%s|%s\\n\\n\", $4, $5, $6, $7}' shell/ns_running_config.conf").read().strip()
print(lbvip)

for i in lbvip.split():
    lbvip_service = os.popen("awk '/^bind lb vserver "+i.split("|")[
                             0]+"/{printf \"%s %s\\n\\n\", $4, $5}' shell/ns_running_config.conf").read().strip()
    print(lbvip_service)
