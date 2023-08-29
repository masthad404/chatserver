import sys
import socket
import select
import os
import time

def interface():
    os.system('clear')
    print("----------------------------------------------------------------------")
    print("\n")
    print("\n")
    print("          _   _                             _ _         ")
    print("     /\  | | | |                           (_| |        ")
    print("    /  \ | |_| | ___  _ __ ___   ___  _ __  _| |_ _   _ ")
    print("   / /\ \| __| |/ _ \| '_ ` _ \ / _ \| '_ \| | __| | | |")
    print("  / ____ | |_| | (_) | | | | | | (_) | | | | | |_| |_| |")
    print(" /_/    \_\__|_|\___/|_| |_| |_|\___/|_| |_|_|\__|\__, |")
    print("                                                   __/ |")
    print("                                                  |___/ ")
    print("Local server communication with the base system by the Vogel projects")
    print("\n")
    print("\n")
    print("---------------------------------------------------------------------")

interface()

def chat_client():
    if len(sys.argv) < 3:
        print('Usage: python client.py hostname port ')
        sys.exit()

    host = sys.argv[1]
    port = int(sys.argv[2])
     
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(2)
     
    try:
        s.connect((host, port))
    except:
        print('Unable to connect')
        sys.exit()
     
    print('Connected to remote host. login:')
    sys.stdout.write('\n[Me] ')
    sys.stdout.flush()
     
    while True:
        socket_list = [sys.stdin, s]
         
        ready_to_read, ready_to_write, in_error = select.select(socket_list, [], [])
         
        for sock in ready_to_read:             
            if sock == s:
                data = sock.recv(4096)
                if not data:
                    print('\nDisconnected from chat server')
                    sys.exit()
                else:
                    sys.stdout.write(data.decode())
                    sys.stdout.write('\n[Me] ')
                    sys.stdout.flush()
            
            else:
                msg = sys.stdin.readline()
                if msg.strip().startswith("$$["):
                    s.send(msg.encode())  # Send the command
                else:
                    s.send(msg.encode())  # Send encoded message
                sys.stdout.write('\n[Me] ')
                sys.stdout.flush()

if __name__ == "__main__":
    chat_client()
