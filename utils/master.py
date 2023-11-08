import socket
import time
import os
from . import global_variables
from .messages import recv_one_message, send_one_message
from .utils import get_machines


def send_receive_master_to_workers(workers_machines, type):
    """
    Gère l'envoi et la réception de messages entre le maître et les workers.

    Args:
    - workers_machines (list): Liste des machines worker.
    - type (str): Type d'action à effectuer.

    Returns:
    - list: Liste des réponses des workers.
    """
    start_time = time.time()

    # Initialiser une liste pour stocker les sockets des clients
    client_sockets = []

    # Établissement des connexions aux machines workers
    for index, machine in enumerate(workers_machines):
        # Création d'un nouveau socket pour la communication
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Connexion au worker sur le port 65044
        client_socket.connect((machine, 65044))

        # Ajouter le socket à la liste des sockets clients
        client_sockets.append(client_socket)

    # Gestion des différents types d'actions à effectuer
    # Selon le type d'action, des messages différents sont envoyés aux workers
    if type == 'workers_liste_des_machines':
        print(f"\n----- Envoi de la liste des machines : en cours -----")
        for client_socket in client_sockets:
            # Envoi du type d'action aux workers
            send_one_message(client_socket, b'workers_liste_des_machines')
            # Envoi de la liste des machines aux workers
            send_one_message(client_socket, str.encode(str(workers_machines)))

    elif type == 'workers_go':
        print(f"\n----- Salutation des workers : en cours -----")
        for client_socket in client_sockets:
            # Envoyer un message de salutation aux workers
            send_one_message(client_socket, b'workers_go')

    elif type == 'workers_send_split_file':
        print('\n----- Envoi des fichiers splits aux workers : en cours -----')
        # Définir le chemin du dossier contenant les fichiers splits
        folder_path = './splits/'

        for index, client_socket in enumerate(client_sockets):
            # Générer le nom du fichier split à envoyer
            filename = f"S{index}.txt"
            # Combiner le chemin du dossier et le nom du fichier pour obtenir le chemin complet
            file_path = os.path.join(folder_path, filename)
            # Obtenir la taille du fichier (en octets)
            filesize = os.path.getsize(file_path)

            # Envoyer des informations sur le fichier aux workers
            send_one_message(client_socket, b'file')
            send_one_message(client_socket, filename.encode())
            send_one_message(client_socket, str(filesize).encode())

            # Lire et envoyer le contenu du fichier aux workers
            with open(file_path, 'rb') as f:
                data = f.read(1024)
                while data:
                    send_one_message(client_socket, data)
                    data = f.read(1024)

    # A VIRER
    # elif type == 'workers_start_map_shuffle':
    #    print('\n-----  Phase de MAP & SHUFFLE : en cours -----')
    #    for index, client_socket in enumerate(client_sockets):
    #        # Demander aux workers de démarrer la phase de MAP & SHUFFLE
    #        send_one_message(client_socket, b'workers_start_map_shuffle')
    #        filename = f"S{index}.txt"
    #        send_one_message(client_socket, filename.encode())
    elif type == 'workers_start_map':
        print('\n-----  Phase de MAP : en cours -----')
        for index, client_socket in enumerate(client_sockets):
            # Demander aux workers de démarrer la phase de MAP
            send_one_message(client_socket, b'workers_start_map')
            filename = f"S{index}.txt"
            send_one_message(client_socket, filename.encode())
    elif type == 'workers_start_shuffle':
        print('\n-----  Phase de SHUFFLE : en cours -----')
        for index, client_socket in enumerate(client_sockets):
            # Demander aux workers de démarrer la phase de SHUFFLE
            send_one_message(client_socket, b'workers_start_shuffle')
    elif type == 'workers_show_shuffle_results':
        print('\n-----  Affichage des listes de mots finales : en cours -----')
        time.sleep(0.2)
        for client_socket in client_sockets:
            # Demander aux workers d'afficher les résultats du shuffle
            send_one_message(client_socket, b'workers_show_shuffle_results')

    # Réception des réponses de chaque worker
    responses = []
    for client_socket in client_sockets:
        try:
            # Recevoir et décoder les réponses
            response = recv_one_message(client_socket)
        except ValueError:
            continue
        responses.append(response.decode())

    # Fermeture des sockets
    for client_socket in client_sockets:
        # Envoyer un message "Bye" pour signifier la fin de la communication
        send_one_message(client_socket, b'Bye')
    end_time = time.time()
    global_variables.timers[type] = round(end_time - start_time, 4)
    # print(f"==> Timer : {round(end_time - start_time,4)} secondes ")

    return responses


def master_functions(client_socket):
    """
    Exécute les fonctions principales du maître.

    Args:
    - client_socket (socket): Socket du client.
    """

    # Obtenir la liste des machines worker
    workers_machines = get_machines()

    # Envoyer la liste des machines aux workers et recevoir leurs réponses
    send_liste_machines_res = send_receive_master_to_workers(
        workers_machines, 'workers_liste_des_machines')

    # Si toutes les machines ont bien reçu la liste
    if (send_liste_machines_res.count('OK workers_liste_des_machines') == len(workers_machines)):
        print(f"----- Envoi de la liste des machines : terminé -----")

        # A VIRER
        # Attendre 4 secondes
        # time.sleep(4)

        # Saluer les workers
        send_receive_master_to_workers(workers_machines, 'workers_go')
        print(f"----- Salutation des workers : terminé -----")

        # A VIRER
        # time.sleep(4)

        # Envoyer les fichiers splits aux workers
        send_receive_master_to_workers(
            workers_machines, 'workers_send_split_file')
        print('----- Envoi des fichiers splits aux workers : terminé -----')

        # A VIRER
        # time.sleep(4)

        # A VIRER
        # Démarrer la phase de MAP & SHUFFLE
        # send_receive_master_to_workers(
        #    workers_machines, 'workers_start_map_shuffle')
        # print('-----  Phase de MAP & SHUFFLE : terminé -----')

        # time.sleep(4)

        # Démarrer la phase de MAP
        workers_start_map_res = send_receive_master_to_workers(
            workers_machines, 'workers_start_map')
        # Si toutes les machines ont bien terminé
        if (workers_start_map_res.count('OK workers_start_map') == len(workers_machines)):
            print('-----  Phase de MAP : terminé -----')

            # A VIRER
            # time.sleep(4)

            # Démarrer la phase de SHUFFLE
            workers_start_shuffle_res = send_receive_master_to_workers(
                workers_machines, 'workers_start_shuffle')
            # Si toutes les machines ont bien terminé
            if (workers_start_shuffle_res.count('OK workers_start_shuffle') == len(workers_machines)):
                print('-----  Phase de SHUFFLE : terminé -----')

                # A VIRER
                # time.sleep(4)
                # Afficher les résultats du shuffle
                send_receive_master_to_workers(
                    workers_machines, 'workers_show_shuffle_results')
                print('-----  Affichage des listes de mots finales : terminé -----')

                print(f"global_variables.timers : {global_variables.timers}")

                # A VIRER
                # time.sleep(4)

    # Signaler la fin du programme au client
    send_one_message(client_socket, b'Programme termine')
