import paramiko
import socket

def get_high_cpu_process(hostname, username, password):
    try:
        # SSH into the NetScaler appliance
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(hostname, username=username, password=password)

        # Execute the shell command to get the process consuming high CPU
        command = "show system cpu"
        stdin, stdout, stderr = ssh.exec_command(command)

        # Read the output and find the process with the highest CPU
        output = stdout.read().decode()
        print("Command output:\n", output)  # Debugging line

        process_lines = output.strip().split('\n')[1:]  # Skip the header line
        if not process_lines:
            raise ValueError("No process lines found in the command output.")

        process_cpu = {}

        for line in process_lines:
            process_info = line.split()
            process_cpu[process_info[0]] = float(process_info[1])

        high_cpu_process = max(process_cpu, key=process_cpu.get)
        cpu_usage = process_cpu[high_cpu_process]

        # Close the SSH connection
        ssh.close()

        return high_cpu_process, cpu_usage

    except paramiko.AuthenticationException:
        print("Authentication failed. Please check the credentials.")
    except paramiko.SSHException as ssh_exception:
        print("SSH connection failed:", str(ssh_exception))
    except socket.gaierror as gai_exception:
        print("Hostname resolution failed:", str(gai_exception))
    except ValueError as value_error:
        print("Error processing command output:", str(value_error))
    except Exception as e:
        print("An error occurred:", str(e))

    return None, None


# Usage example
hostname = "10.110.23.4"
username = "nsroot"
password = "vM1234"

process, cpu = get_high_cpu_process(hostname, username, password)
if process is not None and cpu is not None:
    print(f"Process consuming high CPU: {process}")
    print(f"CPU Usage: {cpu}%")
else:
    print("Failed to retrieve CPU usage information.")
