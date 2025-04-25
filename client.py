import socket

CLIENT_NAME = "Client of Elvis Ramirez"
SERVER_HOST = "localhost"
SERVER_PORT = 65432

def main():
    # Get number from user to send to server
    number  = input("Enter a number between 1 and 100:")
    if number.isdigit() and 1 <= int(number) <= 100:
        number = int(number)
    else:
        print("Invalid input. Please enter a number between 1 and 100.")
        return
    # Create a socket
    print(f"{CLIENT_NAME} is starting...")
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as c:
        c.connect((SERVER_HOST, SERVER_PORT))
        print(f"{CLIENT_NAME} connected to server at {SERVER_HOST}:{SERVER_PORT}")
        # Send the Client name and number to the server
        c.sendall(f"{CLIENT_NAME} {number}".encode())
        print(f"{CLIENT_NAME} sent: {number}")
        # Receive the result from the server
        data = c.recv(1024)
        print(f"{CLIENT_NAME} received: {data.decode()}")
        # Close the connection
        c.close()
        print(f"{CLIENT_NAME} closed the connection.")
if __name__ == "__main__":
    main()