import sys, socket, select, os, time
import subprocess
def initiate_sudo():
    commandsud = "sudo clear"
    subprocess.run(commandsud, shell=True)
initiate_sudo()
RESETCOLOR = "\x1b[0m"
RED = "\x1b[31m"
GREEN = "\x1b[32m"
YELLOW = "\x1b[33m"

HOST = '' 
SOCKET_LIST = []
RECV_BUFFER = 4096 
PORT = 9009
ROOM_CAPACITY = 3  # Maximum number of users in the room

# User credentials
users = {
    "user1": "1234",
    "user2": "1234",
}

users_sockets = {}

def process_command(command, sock):
    if command == "commands":
        response = YELLOW + """\nAvailable commands: $$[commands] - List available commands
        \n$$[hsr]      - Hard server reset (Warning: This will restart the server computer!)
        \n$$[serversh] - Server shutdown (Warning: This will SHUTDOWN the server computer!)
        \n$$[svicesh]  - Server service shutdown (This will shutdown the server service)
        \n$$[sviceres] - Server service restart (This operation is under development and might not work)
        """ + RESETCOLOR
        sock.send(response.encode())
    elif command == "hsr":
        response = RED + "\nATTENTION. THE SERVER COMPUTER WILL RESTART. YOU CANNOT UNDO. RESTARTING IN 10 SECONDS." + RESETCOLOR
        time.sleep(10)
        sock.send(response.encode())
        os.system("reboot")
    elif command == "svicesh":
        response = YELLOW + "\nShutting down the service in 5 seconds" + RESETCOLOR
        sock.send(response.encode())
        time.sleep(5)
        os._exit(1)
    elif command == "serversh":
        response = RED + "\n WARNING. THE SERVER WILL SHUTDOWN WITH THE SERVICE IN 15 SECONDS. GOING DOWN." + RESETCOLOR
        time.sleep(10)
        def initiate_shudown():
            print(RED + "\nOff in 5..." + RESETCOLOR)
            time.sleep(1)
            print(RED + "\nOff in 4..." + RESETCOLOR)
            time.sleep(1)
            print(RED + "\nOff in 3..." + RESETCOLOR)
            time.sleep(1)
            print(RED + "\nOff in 2..." + RESETCOLOR)
            time.sleep(1)
            print(RED + "\nOff in 1..." + RESETCOLOR)
            time.sleep(1)
            command = "sudo shutdown -h now"
            subprocess.run(command, shell=True)
        sock.send(response.encode())
        initiate_shudown()


    else:
        response = "Unknown command: " + command
        sock.send(response.encode())

def authenticate(sock):
    sock.send("Enter username: ".encode())
    username = sock.recv(RECV_BUFFER).decode().strip()
    sock.send("Enter password: ".encode())
    password = sock.recv(RECV_BUFFER).decode().strip()
    
    if username in users and users[username] == password:
        return username
    else:
        sock.send("Authentication failed. Disconnecting...".encode())
        sock.close()
        return None

def chat_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((HOST, PORT))
    server_socket.listen(10)
 
    SOCKET_LIST.append(server_socket)
 
    print("Chat server started on port", str(PORT))
 
    while True:
        ready_to_read, ready_to_write, in_error = select.select(SOCKET_LIST, [], [], 0)
      
        for sock in ready_to_read:
            if sock == server_socket: 
                sockfd, addr = server_socket.accept()
                SOCKET_LIST.append(sockfd)
                print("Client (%s, %s) connected" % addr)
                 
                if len(SOCKET_LIST) <= ROOM_CAPACITY:
                    username = authenticate(sockfd)
                    if username:
                        users_sockets[username] = sockfd
                        broadcast(server_socket, sockfd, "[%s] entered our chatting room\n" % username)
                    else:
                        SOCKET_LIST.remove(sockfd)
                        continue
                else:
                    sockfd.send("Room is full. Disconnecting...".encode())
                    sockfd.close()
                    SOCKET_LIST.remove(sockfd)
             
            else:
                try:
                    data = sock.recv(RECV_BUFFER)
                    if data:
                        message = data.decode().strip()
                        if message.startswith("$$"):
                            command = message[3:-1].lower()
                            process_command(command, sock)
                        else:
                            username = get_username(sock)
                            broadcast(server_socket, sock, "\r" + '[' + username + '] ' + data.decode())  
                    else:
                        if sock in SOCKET_LIST:
                            username = get_username(sock)
                            del users_sockets[username]
                            SOCKET_LIST.remove(sock)
                            broadcast(server_socket, sock, "[%s] is offline\n" % username)
                            
                except:
                    username = get_username(sock)
                    del users_sockets[username]
                    broadcast(server_socket, sock, "[%s] is offline\n" % username)
                    continue

    server_socket.close()

def get_username(sock):
    for username, user_sock in users_sockets.items():
        if user_sock == sock:
            return username
    return "Unknown User"
    
def broadcast(server_socket, sock, message):
    for socket in SOCKET_LIST:
        if socket != server_socket and socket != sock:
            try:
                socket.send(message.encode())
            except:
                socket.close()
                if socket in SOCKET_LIST:
                    SOCKET_LIST.remove(socket)
 
if __name__ == "__main__":
    sys.exit(chat_server())
