import socket
import asyncio
import time
import logging
import sys
from collections import defaultdict

# Configuration
HOST = '0.0.0.0'
PORT = 65432
NUM = 99
SERVER_NAME = 'Server of Elvis Ramirez'
MAX_MSG_SIZE = 40            # Maximum message size in characters
MAX_CONNECTIONS = 100        # Maximum simultaneous connections
CONN_TIMEOUT = 30            # Connection timeout in seconds
MAX_CONN_PER_IP = 5          # Maximum connections per IP
RATE_LIMIT_WINDOW = 60       # Rate limiting window in seconds
RATE_LIMIT_COUNT = 10        # Maximum connections per IP in the window

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger('server')

# Connection tracking
active_connections = 0
ip_connections = defaultdict(int)
connection_history = defaultdict(list)

async def handle_client(reader, writer):
    global active_connections
    
    addr = writer.get_extra_info('peername')
    client_ip = addr[0]
    client_port = addr[1]
    
    # Check connection limits
    if active_connections >= MAX_CONNECTIONS:
        logger.warning(f'Connection rejected from {client_ip}:{client_port} - server at capacity')
        writer.close()
        return
        
    # Rate limiting
    current_time = time.time()
    connection_history[client_ip] = [t for t in connection_history[client_ip] 
                                    if current_time - t < RATE_LIMIT_WINDOW]
    connection_history[client_ip].append(current_time)
    
    if len(connection_history[client_ip]) > RATE_LIMIT_COUNT:
        logger.warning(f'Rate limit exceeded for {client_ip}')
        writer.write("ERROR: Rate limit exceeded. Try again later.".encode())
        await writer.drain()
        writer.close()
        return
    
    # Connection tracking
    active_connections += 1
    ip_connections[client_ip] += 1
    
    if ip_connections[client_ip] > MAX_CONN_PER_IP:
        logger.warning(f'Too many connections from {client_ip}')
        writer.write("ERROR: Too many connections from your IP.".encode())
        await writer.drain()
        writer.close()
        active_connections -= 1
        ip_connections[client_ip] -= 1
        return
    
    logger.info(f'Connection established from {client_ip}:{client_port} '
               f'[{active_connections}/{MAX_CONNECTIONS} active, {ip_connections[client_ip]} from this IP]')
    
    # Set a timeout
    timeout_handle = None
    
    def reset_timeout():
        nonlocal timeout_handle
        if timeout_handle:
            timeout_handle.cancel()
        timeout_handle = asyncio.create_task(handle_timeout(writer, client_ip, client_port))
    
    async def handle_timeout(writer, ip, port):
        logger.info(f'Connection timeout for {ip}:{port}')
        writer.write("ERROR: Connection timed out due to inactivity".encode())
        await writer.drain()
        writer.close()
    
    reset_timeout()
    
    try:
        while not writer.is_closing():
            # Set timeout for reading data
            try:
                data = await asyncio.wait_for(reader.read(1024), timeout=CONN_TIMEOUT)
                reset_timeout()
                
                if not data:
                    logger.info(f'Client disconnected from {client_ip}:{client_port}')
                    break
                
                message = data.decode(errors='replace')  # Handle malformed UTF-8
                
                # Check message length
                if len(message) > MAX_MSG_SIZE:
                    logger.warning(f'Message too long from {client_ip}: {len(message)} chars')
                    writer.write(f"ERROR: Message too long. Max {MAX_MSG_SIZE} characters allowed".encode())
                    await writer.drain()
                    break
                    
                logger.info(f'Received from {client_ip}: {message}')
                
                # Parse the client number safely
                try:
                    parts = message.split()
                    if len(parts) < 2:
                        raise ValueError("Message format incorrect")
                    
                    number_str = parts[-1]
                    
                    # Additional validation to prevent injection
                    if not (number_str.isdigit() or (number_str.startswith('-') and number_str[1:].isdigit())):
                        raise ValueError("Number must contain only digits")
                        
                    number_from_client = int(number_str)
                    
                    # Check if number is between 1 and 100
                    if number_from_client < 1 or number_from_client > 100:
                        logger.warning(f'Invalid number from {client_ip}: {number_from_client}')
                        writer.write("ERROR: Number must be between 1 and 100".encode())
                        await writer.drain()
                        break
                    else:
                        logger.info(f'Valid number from {client_ip}: {number_from_client}')
                        logger.info(f'Calculation: {number_from_client} + {NUM} = {number_from_client + NUM}')
                        
                        response = f"{SERVER_NAME} {NUM}"
                        logger.info(f'Sending to {client_ip}: {response}')
                        writer.write(response.encode())
                        await writer.drain()
                        
                except ValueError as e:
                    logger.warning(f'Invalid message format from {client_ip}: {str(e)}')
                    writer.write("ERROR: Invalid message format. Expected: 'ClientName Number'".encode())
                    await writer.drain()
                    break
                
            except asyncio.TimeoutError:
                logger.warning(f'Read timeout for {client_ip}:{client_port}')
                writer.write("ERROR: Read operation timed out".encode())
                await writer.drain()
                break
                
    except (ConnectionResetError, BrokenPipeError, asyncio.CancelledError) as e:
        logger.warning(f'Connection error with {client_ip}:{client_port}: {str(e)}')
    finally:
        if timeout_handle:
            timeout_handle.cancel()
        
        active_connections -= 1
        ip_connections[client_ip] -= 1
        if ip_connections[client_ip] <= 0:
            del ip_connections[client_ip]
            
        writer.close()
        try:
            await writer.wait_closed()
        except:
            pass
            
        logger.info(f'Connection closed with {client_ip}:{client_port} '
                  f'[{active_connections}/{MAX_CONNECTIONS} active]')

async def main():
    try:
        server = await asyncio.start_server(
            handle_client, 
            HOST, 
            PORT,
            reuse_address=True,
            start_serving=False  # Don't start immediately
        )
        
        logger.info(f'╔═══════════════════════════════════════════════╗')
        logger.info(f'║ {SERVER_NAME}                       ║')
        logger.info(f'║ Running on {HOST}:{PORT}                      ║')
        logger.info(f'║ Max connections: {MAX_CONNECTIONS}                          ║')
        logger.info(f'║ Max per IP: {MAX_CONN_PER_IP}                                 ║')
        logger.info(f'║ Connection timeout: {CONN_TIMEOUT}s                       ║')
        logger.info(f'╚═══════════════════════════════════════════════╝')
        
        async with server:
            await server.start_serving()
            await asyncio.Future()  # Run forever
    except asyncio.CancelledError:
        logger.info("Server shutdown initiated")
        # Let server close gracefully
        server.close()
        await server.wait_closed()
        logger.info("Server has shut down")

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("\nServer shutdown requested via keyboard interrupt")
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}", exc_info=True)

