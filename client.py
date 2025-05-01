import socket

CLIENT_NAME = "Client of Elvis Ramirez"
SERVER_HOST = "localhost"
SERVER_PORT = 65432

def main():
    # Get number from user to send to server
    number = input("Enter a number between 1 and 100, or -1: ")
    if number == "-1" or (number.isdigit() and 1 <= int(number) <= 100):
        number = int(number)
    else:
        print("Invalid input. Please enter a number between 1 and 100, or -1.")
        return
    
    print(f"Starting connection to server at {SERVER_HOST}:{SERVER_PORT}...")
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as c:
        try:
            c.connect((SERVER_HOST, SERVER_PORT))
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
            num_from_server = int(server_response.split(" ")[-1])
            print(f"Received from server: {server_response}")
            print(f"Calculation: {number} + {num_from_server} = {number + num_from_server}")
            
        except ConnectionRefusedError:
            print(f"Error: Could not connect to server at {SERVER_HOST}:{SERVER_PORT}")
        except Exception as e:
            print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()