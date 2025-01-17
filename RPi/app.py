import socket
import threading
import time
from LCD import LCD

# Global vars for use in methods/threads
client_socket = None
server_socket = None
server_thread = None
shutdown_flag = threading.Event() # see: https://docs.python.org/3/library/threading.html#event-objects

def setup_socket_server():
    global server_socket, server_thread, shutdown_flag
    # Socket setup
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # create a socket instance
    server_socket.bind(('0.0.0.0', 8500)) # bind on all available ip's (WiFi and LAN), on port 8500 (this can be anything between 1024 and 65535)
    server_socket.settimeout(0.2)  # Timeout for listening, needed for loop in thread, otherwise it's blocking
    server_socket.listen(1) # enable "listening" for requests / connections


    # Start the server thread
    server_thread = threading.Thread(target=accept_connections, args=(shutdown_flag,), daemon=True) # create the thread 
                                                                               # where you wait for incoming connection
    server_thread.start() # start the above thread

def accept_connections(shutdown_flag):
    global client_socket
    print("Accepting connections")
    while not shutdown_flag.is_set():  # as long as ctrl+c is not pressed
        try:
            client_socket, addr = server_socket.accept() # accept incoming requests, and return a reference to the client and it's IP
            print("Connected by", addr)
            client_thread = threading.Thread(target=handle_client, args=(client_socket, shutdown_flag,)) # thread 
            client_thread.start() # start the above thread; where we try to accept data
        except socket.timeout: # ignore timeout errors
            pass


def handle_client(sock, shutdown_flag):
    try:
        score_type = ""
        prev_data = -1
        while not shutdown_flag.is_set(): # as long as ctrl+c is not pressed
            data = sock.recv(1024) # try to receive 1024 bytes of data (maximum amount; can be less)
            if not data: # when no data is received, try again (and shutdown flag is checked again)
                break # go back to top
            data = data.decode()
            try:
                data = int(data)
            
                if score_type == "":
                    lcd.clear()
                    lcd.display_message(message="Score: ", line=lcd.LCD_LINE_1)
                    score_type = "Score"

                elif score_type == "Final score":
                    score_type = ""
                print("Received from client:", data) # print the received data, or do something with it
                if prev_data != data:
                    lcd.display_message(message = f"{data}%   ", line=lcd.LCD_LINE_2)
                prev_data = data
            except Exception:
                lcd.clear()
                lcd.display_message(message = data, line=lcd.LCD_LINE_1)
                if data == "Final score:":
                    score_type = "Final score"
                else:
                    score_type = ""
                prev_data = data


    except socket.timeout: # capture the timeouts 
        pass
    except Exception as e:
        print(f"Error: {e}")
    finally:
        lcd.clear()
        sock.close()


###### MAIN PART ######
try:
    lcd = LCD()
    lcd.setup()
    setup_socket_server()
    while True:
        time.sleep(10)

except KeyboardInterrupt:
    print("Server shutting down")
    shutdown_flag.set() # set the shutdown flag
finally:
    server_thread.join() # join the thread, so we wait for it to finish (gracefull exit)
    server_socket.close() # make sure to close any open connections