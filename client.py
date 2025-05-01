import socket
import sys
import re

CLIENT_NAME = "Client of Elvis Ramirez"
SERVER_PORT = 65432
DEFAULT_HOST = "localhost"

def is_valid_ip(ip):
    # Regular expression pattern for IPv4 address validation
    pattern = r'^(\d{1,3})\.(\d{1,3})\.(\d{1,3})\.(\d{1,3})$'
    match = re.match(pattern, ip)
    
    if not match:
        return False
    
    # Check if each octet is between 0 and 255
    for octet in match.groups():
        if int(octet) > 255:
            return False
            
    return True

def main():
    # Process command line arguments
    if len(sys.argv) > 1:
        HOST = sys.argv[1]
        # Validate IP if it's not a hostname
        if HOST != "localhost" and not is_valid_ip(HOST):
            print(f"Error: Invalid IP address format: {HOST}")
            print("Please use a valid IPv4 address (e.g., 192.168.1.1) or 'localhost'")
            return
    else:
        HOST = DEFAULT_HOST
    
    # Get number from user to send to server
    number = input("Enter a number between 1 and 100, or -1: ")
    if number == "-1" or (number.isdigit() and 1 <= int(number) <= 100):
        number = int(number)
    else:
        print("Invalid input. Please enter a number between 1 and 100, or -1.")
        return
    
    print(f"Starting connection to server at {HOST}:{SERVER_PORT}...")
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as c:
        try:
            c.connect((HOST, SERVER_PORT))
            print(f"Connected successfully")
            
            # Send the Client name and number to the server
            message = f"{CLIENT_NAME} {number}"
            c.sendall(message.encode())
            print(f"Sent: {message}")
            
            if number == -1:
                print("Closing connection (sent exit code -1)")
                return
            
            # Receive the result from the server
            data = c.recv(1024)
            server_response = data.decode()
            print(f"Received from server: {server_response}")

            # Check if response starts with "ERROR"
            if server_response.startswith("ERROR:"):
                print(f"Server error: {server_response}")
            else:
                try:
                    num_from_server = int(server_response.split(" ")[-1])
                    print(f"Calculation: {number} + {num_from_server} = {number + num_from_server}")
                except ValueError as e:
                    print(f"Failed to parse server response: {e}")
            
        except ConnectionRefusedError:
            print(f"Error: Could not connect to server at {HOST}:{SERVER_PORT}")
        except socket.gaierror:
            print(f"Error: Could not resolve hostname or IP address: {HOST}")
        except Exception as e:
            print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()