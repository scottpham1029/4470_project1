import socket
import threading
import json
import sys


# store connections
connections = []  

def listen_for_connect(s):
    while True:
        connection_socket, address = s.accept()

        # add connection to list
        connections.append({"socket": connection_socket, "address": address[0], "port": address[1]})

        thread = threading.Thread(target=listen_to_peer, args=(connection_socket, address[0], address[1]), daemon=True)
        thread.start()

def remove_connection(sock):
    # Find and remove the connection
    for peer in connections[:]:
        if peer["socket"] is sock:
            connections.remove(peer)
            break

    # Close the socket
    try:
        sock.shutdown(socket.SHUT_RDWR)
    except OSError:
        pass

    sock.close()

def listen_to_peer(sock, addr, port):

    #byte literal
    buffer = b""

    try:
        while True:
            #receive data from connected peer
            data = sock.recv(1024)

            if not data:
                break

            buffer += data

            #process newline messages in buffer then store in line
            while b"\n" in buffer:

                #split at most 1 \n
                #store everything before \n into line and 
                #remainder in buffer
                line, buffer = buffer.split(b"\n", 1)

                try:
                    packet = json.loads(line.decode("utf-8"))

                    message = packet["message"]
                    sender_port = packet["port"]

                    print(f"\nMessage receved from {addr}")
                    print(f"Sender's port: {sender_port}")
                    print(f'Message: "{message}"')

                except(ValueError, TypeError, KeyError):
                    print("Error: Invalid Message Received")

    except OSError as e:
        print(f"Connection error with {addr}: {e}")

    finally:
        remove_connection(sock)
        print(f"\nPeer disconnected: {addr}")



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
        sock.connect((user_input[1], int(user_input[2])))

        # add connection to list
        connections.append({"socket": sock, "address": user_input[1], "port": user_input[2]})

        thread = threading.Thread(target=listen_to_peer, args=(sock, user_input[1], user_input[2]), daemon=True)
        thread.start()
    elif user_cmd == "send":

        if len(user_input) != 3:
            print("Usage: send <connection id> <message>")
            return

        try:
            connection_id = int(user_input[1])
        except ValueError:
            print("Invalid connection ID")
            return

        message = user_input[2]

        if not 1 <= connection_id <= len(connections):
            print("Connection does not exist")
            return

        if len(message) > 100:
            print("Message exceeds 100 characters")
            return

        peer = connections[connection_id - 1]

        packet = {
            "port": int(sys.argv[1]),
            "message": message
        }

        try:
            data = json.dumps(packet) + "\n"
            peer["socket"].sendall(data.encode("utf-8"))
            print(f"Message sent to {connection_id}")

        except OSError as e:
            print(f"Error sending message: {e}")

    elif user_cmd == "exit":
        print("Closing all connections...")

        # Copy the list before modifying it
        for peer in connections[:]:
            remove_connection(peer["socket"])

        print("Exiting chat application.")
        return False


def main():
    # listening socket
    s = socket.socket()

    # bind to port
    port = int(sys.argv[1])

    #allow socket addy to be reused during runtime
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    s.bind(("", port))

    # listen to port
    s.listen(10)
    thread = threading.Thread(target=listen_for_connect, args=(s,), daemon=True)
    thread.start()

    # while True:
    #     # look for user input
    #     command = input(">>> ")
    #     handle_command(command)

    try:
        while True:
            command = input(">>> ")

            if handle_command(command) is False:
                break

    except (KeyboardInterrupt, EOFError):
        print("\nProgram interrupted.")

    finally:
        # Close the listening socket
        s.close()

        # Clean up any remaining peer connections
        for peer in connections[:]:
            remove_connection(peer["socket"])



if __name__ == "__main__":
    main()
