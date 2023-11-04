# This is a NetScaler self healing daemon code and in poc stage

import psutil
from time import sleep
import subprocess as sp

nsmd_home = '/var/nsmd'

critical_services = ['httpdd']

def is_service_running(service_name):
    for process in psutil.process_iter(attrs=['name']):
        if service_name in process.info['name']:
            return True
    return False

def restart_service(service_name, start_command):
    if is_service_running(service_name):
        print(f"Stopping {service_name}...")
        sp.run(["service", service_name, "stop"])
        sleep(5)
    print(f"Starting {service_name}...")
    sp.run(start_command, shell=True)

def check_service():
    for service in critical_services:
        if not is_service_running(service):
            print(f"{service} is down. Restarting...")
            restart_service(service, '/bin/httpd -C /etc/httpd.conf')


def main():
    pass


while True:
    main()
    sleep(10)