# CREDITS TO https://github.com/TiagoValdrich/python-socket-chat

# JULY 17 CHANGED BY SAMIP REGMI samTime101




import socket, threading
from datetime import datetime
connections = []

def readfile(file):
    try:
        with open(f"{file}.csv") as f:
            return f.read()
    except Exception as e:
        return f'Data not found for date {file}'


def is_valid_date(date_str: str) -> bool:
    try:
        datetime.strptime(date_str, '%Y-%m-%d')
        return True
    except ValueError:
        return False

def handle_user_connection(connection: socket.socket, address: str) -> None:
    while True:
        try:
            msg = connection.recv(1024)

            if msg:
                decoded = msg.decode().strip()

                print(f'{address[0]}:{address[1]} - {decoded}')
                if is_valid_date(decoded):
                    # readfile(decoded)
                    connection.send(f"\n-----\n[*] FROM 2FA \n{readfile(decoded)}\n-----\n".encode())
                elif decoded == '2fa':
                    connection.send(f"\n-----\n[*] FROM 2FA \n{readfile(decoded)}\n-----\n".encode())
                elif decoded == 'help':
                    connection.send("FROM 2FA > made by 2FA 2025\n".encode())
                else:
                    connection.send("Unknown command. Exiting.".encode())
                    remove_connection(connection)
                    break

                #JULY 17 SAMIP REGMI EDITED ---- 
                # Broadcast message to other users (optional)
                # msg_to_send = f'From {address[0]}:{address[1]} - {decoded}'
                # broadcast(msg_to_send, connection)

            else:
                remove_connection(connection)
                break

        except Exception as e:
            print(f'Error to handle user connection: {e}')
            remove_connection(connection)
            break



def remove_connection(conn: socket.socket) -> None:
    '''
        Remove specified connection from connections list
    '''

    # Check if connection exists on connections list
    if conn in connections:
        conn.close()
        connections.remove(conn)


def server() -> None:
    '''
        Main process that receive client's connections and start a new thread
        to handle their messages
    '''

    LISTENING_PORT = 12000
    
    try:
        # Create server and specifying that it can only handle 4 connections by time!
        socket_instance = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        socket_instance.bind(('', LISTENING_PORT))
        socket_instance.listen(4)

        print('Server running!')
        
        while True:

            # Accept client connection
            socket_connection, address = socket_instance.accept()
            # Add client connection to connections list
            connections.append(socket_connection)
            # Start a new thread to handle client connection and receive it's messages
            # in order to send to others connections
            threading.Thread(target=handle_user_connection, args=[socket_connection, address]).start()

    except Exception as e:
        print(f'An error has occurred when instancing socket: {e}')
    finally:
        # In case of any problem we clean all connections and close the server connection
        if len(connections) > 0:
            for conn in connections:
                remove_connection(conn)

        socket_instance.close()


if __name__ == "__main__":
    server()