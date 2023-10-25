import socket
import traceback
from utils.messages import send_one_message, recv_one_message


def main():
    """
    Point d'entrée principal pour le client. 
    Établit une connexion avec le serveur, envoie un message 
    et reçoit une réponse du serveur.
    """

    # Adresse IP ou nom d'hôte du serveur
    host = 'tp-1a252-17.enst.fr'

    # Numéro de port du serveur
    port = 65044

    try:
        # Crée un nouveau socket pour la communication
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Établit une connexion avec le serveur
        client_socket.connect((host, port))

        # Envoie un message "master_start" au serveur
        send_one_message(client_socket, b"master_start")

        # Attends et reçoit une réponse du serveur
        response = recv_one_message(client_socket).decode()
        print(f'Received response: {response}')

        # Envoie un message "Bye" pour signifier la fin de la communication
        message = 'Bye'
        send_one_message(client_socket, message.encode())

        # Ferme la connexion
        client_socket.close()
    except Exception as e:
        # Si une erreur se produit, elle est affichée
        print(f'Error : {e}')
        # Traceback fournit des détails sur l'origine de l'erreur
        traceback.print_exc()


# Assure que le code est exécuté uniquement si ce fichier est exécuté en tant que script principal
if __name__ == '__main__':
    main()
