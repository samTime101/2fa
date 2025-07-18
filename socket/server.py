# CREDITS TO https://github.com/TiagoValdrich/python-socket-chat

# JULY 17 CHANGED BY SAMIP REGMI samTime101

# TODO: JULY 17

# connection.send(b"")
# connection.recv(somebytes).decode().strip

# check credentials 
# if not ok
# conn..send('invalid')
# remove_connection(conn)

# else
# succkess
# go to while loop


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




username = '2fa'
password = '2fa'
def handle_user_connection(connection: socket.socket, address: str) -> None:
    try:
        # SERVER SENDS MESSAGE JULY 17
        connection.send(b"USERNAME >>:")
        user_username = connection.recv(1024).decode().strip()
        connection.send(b"PASSOWORD >>:")
        user_password = connection.recv(1024).decode().strip()
        if user_password != username and user_password !=  password or not user_password or not user_password:
            connection.send(b"INVALID LOGIN")
            remove_connection(connection)
            return
        connection.send(b"WELCOME ADMIN\n")

        while True:
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
        return



def remove_connection(conn: socket.socket) -> None:

    if conn in connections:
        conn.close()
        connections.remove(conn)


def server() -> None:

    LISTENING_PORT = 12000
    
    try:
        socket_instance = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        socket_instance.bind(('', LISTENING_PORT))
        socket_instance.listen(4)

        print('Server running!')
        
        while True:

            socket_connection, address = socket_instance.accept()
            connections.append(socket_connection)

            threading.Thread(target=handle_user_connection, args=[socket_connection, address]).start()

    except Exception as e:
        print(f'An error has occurred when instancing socket: {e}')
    finally:
        if len(connections) > 0:
            for conn in connections:
                remove_connection(conn)

        socket_instance.close()


if __name__ == "__main__":
    server()