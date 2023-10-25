import socket
import threading
import traceback
from utils.master import master_functions
from utils.messages import recv_one_message
from utils.utils import receive_file
from utils.workers import workers_functions


def handle_client(client_socket, address):
    """
    Gère les interactions avec un client connecté.

    :param client_socket: Socket du client.
    :param address: Adresse du client.
    """
    try:
        while True:
            # Récupère un message du client
            data = recv_one_message(client_socket)
            if not data:
                break
            message = data.decode().strip().lower()
            splited_message = message.split("_")

            # Traitement basé sur le message reçu
            if message == 'file':
                receive_file(client_socket)
            elif splited_message[0] == 'master':
                master_functions(client_socket)
            elif splited_message[0] == 'workers':
                workers_functions(client_socket, message, address)
            elif message == 'bye':
                break
    except Exception as e:
        print(f'{socket.gethostname()} Error handling client {address}: {e}')
        traceback.print_exc()
    finally:
        # Fermer la connexion au client
        client_socket.close()


def start_server(port):
    """
    Démarre le serveur pour écouter les connexions des clients.

    :param port: Port sur lequel le serveur écoute.
    """
    try:
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind(('0.0.0.0', port))
        server_socket.listen()
        print(f'{socket.gethostname()} Server listening on port {port}')

        # Attente continue des connexions des clients
        while True:
            client_socket, address = server_socket.accept()
            # Pour chaque client connecté, démarrer un nouveau thread pour le gérer
            client_thread = threading.Thread(
                target=handle_client, args=(client_socket, address))
            client_thread.start()
    except Exception as e:
        print(f'{socket.gethostname()} Error starting server: {e}')
        traceback.print_exc()
    finally:
        # Fermer le socket du serveur
        server_socket.close()


if __name__ == '__main__':
    port = 65044  # Choisissez un port libre de votre choix qui n'est pas utilisé par d'autres étudiants
    start_server(port)
