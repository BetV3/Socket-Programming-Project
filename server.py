import socket
import asyncio

HOST = '0.0.0.0'
PORT = 65432
NUM = 99
SERVER_NAME = 'Server of Elvis Ramirez'

async def handle_client(reader, writer):
    addr = writer.get_extra_info('peername')
    print(f'Connection established from {addr[0]}:{addr[1]}')
    
    while True:
        data = await reader.read(1024)
        if not data:
            print(f'Client disconnected from {addr[0]}:{addr[1]}')
            writer.close()
            await writer.wait_closed()
            break
        else:
            message = data.decode()
            print(f'Received: {message}')
            
            number_from_client = int(message.split(" ")[-1])
            
            # check if number is between 1 and 100
            if number_from_client < 1 or number_from_client > 100:
                print(f'⚠️ Invalid number received: {number_from_client}. Connection will be closed.')
                writer.close()
                await writer.wait_closed()
                break
            else:
                print(f'✓ Valid number received: {number_from_client}')
                print(f'Calculation: {number_from_client} + {NUM} = {number_from_client + NUM}')
                
        response = f"{SERVER_NAME} {NUM}"
        print(f'Sending response: {response}')
        writer.write(response.encode())
        await writer.drain()

async def main():
    server = await asyncio.start_server(handle_client, HOST, PORT)
    
    print(f'╔═══════════════════════════════════════╗')
    print(f'║ {SERVER_NAME}               ║')
    print(f'║ Running on {HOST}:{PORT}            ║')
    print(f'╚═══════════════════════════════════════╝')
    
    async with server:
        await server.serve_forever()

if __name__ == '__main__':
    asyncio.run(main())
