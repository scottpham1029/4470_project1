import socket
import threading
import json
import sys


# store connections
connections = []  

def listen_for_connect(s):

    print("[DEBUG] Listening for incoming TCP connections...")
    
    while True:
        try:
            connection_socket, address = s.accept()
        except OSError:
            break

        print(f"\n[DEBUG] Connection accepted from {address}")
        print(f"[DEBUG] Socket: {connection_socket}")

        # add connection to list
        connections.append({"socket": connection_socket, "address": address[0], "port": int(address[1])})

        print(f"[DEBUG] Total connections: {len(connections)}")

        thread = threading.Thread(target=listen_to_peer, args=(connection_socket, address[0], int(address[1])), daemon=True)
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

                    if message == "INIT_LISTEN_PACKET":
                        for peer in connections:
                            if peer["socket"] is sock:
                                peer["port"] = sender_port
                                break
                    else :
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


'''
def get_my_ip()
----------------
returns ip address
'''
def get_my_ip():
    temp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    try:
        temp.connect(("8.8.8.8", 80))
        ip = temp.getsockname()[0]

    except OSError:
        ip = "127.0.0.1"

    finally:
        temp.close()

    return ip

global_my_ip = get_my_ip()

'''
def help_command():
--------------------
prints out list of commands 
'''
def help_command():
    print("\n" + "=" * 70)
    print("\t\t\t\tCOMMANDS")
    print("=" * 70)
          
    print("The following  are the commands that can be"
          " used on line text with their use case:\n")

    print("help : \n\tShows all the commands.") #DONE
    
    print("myip :\n\tDisplay the IP address of this process.")
    
    print("myport :\n\tDisplays the port on which this process is listening for incoming connections.")
    
    print("connect <destubation> <port no> :\n\t\tTries to  establishes new"
          " TCP connection to a local IP") #DONE
    
    print("list :\n\tPrints out all connected IP address and what port each is listening to.") #DONE
    
    print("terminate <connection id> :\n\t\tterminates a connection based on the ID placed on them.")
    
    print("send <connection id> :\n\t\tSend a message to ones ID as well as a confirmation if message sent.") #DONE
    
    print("exit :\n\tExit from program.") #DONE

    print("\n" + "=" * 70)

def myip_command():
    print(global_my_ip)

def myport_command():
    port = int(sys.argv[1])
    print(f"Listening port: {port}")
    
def handle_command(command):
    # store user input
    user_input = command.split(maxsplit=2)

    if len(user_input) == 0:
        return

    # extract command and normalize string
    user_cmd = user_input[0].lower()

    # connect <destination> <port no>

    # This command establishes a new TCP connection to the specified <destination> at the specified <port no>. 
    # The <destination> is the IP address of the computer. 
    # Any attempt to connect to an invalid IP should be rejected and suitable error message should be displayed. Success or
    # failure in connections between two peers should be indicated by both the peers using suitable messages.
    # Self-connections and duplicate connections should be flagged with suitable error messages.

    if user_cmd == "connect":
        # error check
        if len(user_input) != 3:
            print("Usage: connect <destination> <port no>")
            return

        
        try:
            destination = user_input[1]
            destination_port = int(user_input[2])

        except ValueError:
            print("Error: port must be an integer")
            return

        if destination == global_my_ip and destination_port == int(sys.argv[1]):
            print("Error: Cannot connect to self")
            return
        
        for peer in connections:
            if peer["address"] == destination and peer["port"] == destination_port:
                print("Error: Already connected to this peer")
                return

            
        # create socket
        sock = socket.socket()

        try:
            sock.connect((destination, destination_port))

        except (OSError) as e:
            print(f"Connection failed: {e}")
            sock.close()
            return

        # add connection to list
        connections.append({"socket": sock, "address": user_input[1], "port": int(user_input[2])})

        # tell the peer what port WE are listening on
        init_packet = {
            "message": "INIT_LISTEN_PACKET",
            "port": int(sys.argv[1])
        }

        # send da packet
        data = json.dumps(init_packet) + "\n"
        sock.sendall(data.encode("utf-8"))

        thread = threading.Thread(target=listen_to_peer, args=(sock, user_input[1], int(user_input[2])), daemon=True)
        thread.start()

        print(f"Successfully connected to {destination}:{destination_port}")
    elif user_cmd == "list":

        if len(connections) == 0:
            print("No active connections.")
            return

        print("id: IP address\tPort No.")

        for i, peer in enumerate(connections, start=1):
            print(f"{i}: {peer['address']}\t{peer['port']}")
        
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

    elif user_cmd == "terminate":
        if len(connections) == 0:
            print("No active connections.")
            return
        else:
            if len(user_input) != 2:
                print("Usage: terminate <connection id> ")
                return
            else:
                try:
                    connection_id = int(user_input[1])
                except ValueError:
                    print("Invalid connection ID.")
                    return

                #check whether connection ID exists
                if not 1 <= connection_id <= len(connections):
                    print("Connection does not exist.")
                    return

                #retrieve peer from connections list
                peer = connections[connection_id - 1]

                #remove connection using its socket
                remove_connection(peer["socket"])

                print(f"Connection {connection_id} terminated.")

        

    elif user_cmd == "exit":
        print("Closing all connections...")

        # Copy the list before modifying it
        for peer in connections[:]:
            remove_connection(peer["socket"])

        print("Exiting chat application.")
        return False

    elif user_cmd == "help":
        help_command()

    elif user_cmd == "myip":
        myip_command()

    elif user_cmd == "myport":
        myport_command()



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
    print("\nWelcome to the chat application!\n--------------------------------")
    print("\nEnter a command (type 'help' for a list of commands):")
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
