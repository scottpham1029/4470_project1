import socket
import threading

# store connections
connections = []  

def listen_for_connect(s):
    while True:
        connection_socket, address = s.accept()

        # add connection to list
        connections.append({"socket": connection_socket, "address": address[0], "port": address[1]})

        thread = threading.Thread(target=listen_to_peer, args=(connection_socket, address[0], address[1]), daemon=True)
        thread.start()

def listen_to_peer(sock, addr, port):
    while True:
        # ??
        data = sock.recv(1024)

def handle_command(command):
    # store user input
    user_input = command.split(maxsplit=2)

    if len(user_input) == 0:
        return

    # extract command and normalize string
    user_cmd = user_input[0].lower()

    # insert all the commands here




    # connect <destination> <port no>

    # This command establishes a new TCP connection to the specified <destination> at the specified <port no>. 
    # The <destination> is the IP address of the computer. 
    # Any attempt to connect to an invalid IP should be rejected and suitable error message should be displayed. Success or
    # failure in connections between two peers should be indicated by both the peers using suitable messages.
    # Self-connections and duplicate connections should be flagged with suitable error messages.
    if user_cmd == "connect":
        # create socket
        sock = socket.socket()
        sock.connect((user_input[1], user_input[2]))

        # add connection to list
        connections.append({"socket": sock, "address": user_input[1], "port": user_input[2]})

        thread = threading.Thread(target=listen_to_peer, args=(sock, user_input[1], user_input[2]), daemon=True)
        thread.start()


def main():
    # listening socket
    s = socket.socket()

    # bind to port
    port = 1234
    s.bind(("", port))

    # listen to port
    s.listen(10)
    thread = threading.Thread(target=listen_for_connect, args=(s,), daemon=True)
    thread.start()

    while True:
        # look for user input
        command = input(">>> ")
        handle_command(command)



main()
