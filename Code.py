import socket
import subprocess
import os
import signal
import time

def kill_existing_process(port):
    """Kill the process running on the specified port."""
    try:
        result = subprocess.run(
            ["lsof", "-ti", f":{port}"],
            capture_output=True,
            text=True
        )
        pids = result.stdout.strip().splitlines()
        
        for pid in pids:
            os.kill(int(pid), signal.SIGTERM)  # Terminate the process
            print(f"Killed process with PID: {pid} on port: {port}")
            time.sleep(1)  # Wait for the process to terminate
            if os.path.exists(f"/proc/{pid}"):
                os.kill(int(pid), signal.SIGKILL)  # Force kill if still running
                print(f"Forcefully killed process with PID: {pid} on port: {port}")

    except Exception as e:
        print(f"Error killing process on port {port}: {e}")

def is_port_open(port):
    """Check if the specified port is open."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) == 0

def start_service(port, service_name):
    """Start a simple TCP server that pretends to run the specified service."""
    while is_port_open(port):
        print(f"Waiting for port {port} to be free...")
        time.sleep(1)  # Wait for a second before checking again

    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(('0.0.0.0', port))
            s.listen(1)
            print(f"{service_name} is now running on port {port}...")

            try:
                while True:
                    conn, addr = s.accept()
                    with conn:
                        # Only show the connection establishment message
                        print(f"Connection from {addr} established.")
                        
                        # Send a fake banner to the client based on service
                        if service_name.lower() == "http":
                            banner = ("HTTP/1.1 200 OK\r\n"
                                      "Server: Apache/2.4.41 (Ubuntu)\r\n"
                                      "Date: Sat, 29 Sep 2024 12:00:00 GMT\r\n"
                                      "Content-Type: text/html; charset=UTF-8\r\n"
                                      "Content-Length: 71\r\n"
                                      "Connection: close\r\n\r\n"
                                      "<html><body><h1>Welcome to the Fake HTTP Server!</h1></body></html>")
                        elif service_name.lower() == "ftp":
                            banner = "220 (vsFTPd 3.0.3)\r\n"
                        elif service_name.lower() == "smtp":
                            banner = "220 mail.example.com ESMTP Postfix (Ubuntu)\r\n"
                        elif service_name.lower() == "ssh":
                            banner = "SSH-2.0-OpenSSH_8.4\r\n"
                        else:
                            banner = "Unknown service\r\n"

                        conn.sendall(banner.encode())
                        
                        # Wait for a short period to allow the client to receive the banner
                        time.sleep(0.5)

                        # Close the connection to prevent further interaction
                        conn.close()
            except KeyboardInterrupt:
                print("Service stopped.")
    except OSError as e:
        print(f"Error starting service on port {port}: {e}")

def main():
    print("         _                                  _                        ")
    print("        | |                                | |                       ")
    print("   ___  | |__     __ _   _ __ ___     ___  | |   ___    ___    _ __  ")
    print("  / __| | '_ \   / _` | | '_ ` _ \   / _ \ | |  / _ \  / _ \  | '_ \ ")
    print(" | (__  | | | | | (_| | | | | | | | |  __/ | | |  __/ | (_) | | | | |")
    print("  \___| |_| |_|  \__,_| |_| |_| |_|  \___| |_|  \___|  \___/  |_| |_|")
    print("                                                                     ")
    print("Configuring...")
    time.sleep(5)
    # Get user input for port number
    port = int(input("Enter the port number: "))

    # Display service options
    print("Choose a service to simulate:")
    print("1. HTTP")
    print("2. FTP")
    print("3. SMTP")
    print("4. SSH")
    
    # Map user's choice to service name
    service_choice = input("Enter the number of the service you want to simulate: ")
    
    if service_choice == '1':
        service_name = "HTTP"
    elif service_choice == '2':
        service_name = "FTP"
    elif service_choice == '3':
        service_name = "SMTP"
    elif service_choice == '4':
        service_name = "SSH"
    else:
        print("Invalid choice, defaulting to HTTP.")
        service_name = "HTTP"
    
    # Kill existing process on the port if necessary
    kill_existing_process(port)

    # Start the spoofed service
    start_service(port, service_name)

if __name__ == "__main__":
    main()
