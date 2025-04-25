import socket
import asyncio

HOST = 'localhost'
PORT = 65432
NUM = 99
SERVER_NAME = 'Server of Elvis Ramirez'

async def handle_client(reader, writer):
    while True:
        print(f'{SERVER_NAME} is waiting for data...')
        data = await reader.read(1024)
        if not data:
            print(f'{SERVER_NAME} received no data, closing connection.')
            writer.close()
            await writer.wait_closed()
            break
        else:
            print(f'{SERVER_NAME} received: {data.decode()}')
            number_from_client = int(data.decode().split(" ")[-1])
            # check if number is between 1 and 100
            if number_from_client < 1 or number_from_client > 100:
                print(f'{SERVER_NAME} received invalid number: {number_from_client}')
                writer.close()
                await writer.wait_closed()
                break
            else:
                print(f'{SERVER_NAME} received valid number: {number_from_client}')
                print(f'{SERVER_NAME} sending: {NUM}')
                print(f'Sum of {number_from_client} and {NUM} is {number_from_client + NUM}')
        writer.write(f"{SERVER_NAME} {NUM}".encode())
        await writer.drain()
async def main():
    print(f'{SERVER_NAME} is running on {HOST}:{PORT}')
    server = await asyncio.start_server(handle_client, HOST, PORT)
    print(f'Server started on {HOST}:{PORT}')
    async with server:
        print(f'{SERVER_NAME} is waiting for connections...')
        await server.serve_forever()
if __name__ == '__main__':
    asyncio.run(main())
