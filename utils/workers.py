import ast
import socket
import time
from . import global_variables
from .messages import recv_one_message, send_one_message
from .utils import sum_tuples, words_count

# Disable certain pylint warnings
# pylint: disable=redefined-outer-name


def send_receive_worker_to_other_workers(workers_list, type):
    """
    Envoie et reçoit des messages entre les workers.

    :param workers_list: Liste des machines workers.
    :param type: Type de message à envoyer.
    :return: Liste des réponses des workers.
    """

    # Récupère le nom de l'hôte actuel
    complete_hostname = f"{socket.gethostname()}.enst.fr"

    # Supprime le nom d'hôte actuel de la liste des workers
    workers_list.remove(complete_hostname)

    # Crée des sockets pour se connecter aux autres workers
    client_sockets = []
    for machine in workers_list:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((machine, 65044))
        client_sockets.append(client_socket)

    # Si le message est 'workers_bonjour', l'envoyer à tous les autres workers
    if type == 'workers_bonjour':
        for client_socket in client_sockets:
            send_one_message(client_socket, b'workers_bonjour')

    # Collecte les réponses des autres workers
    responses = []
    for client_socket in client_sockets:
        try:
            response = recv_one_message(client_socket)
        except ValueError:
            continue
        responses.append(response.decode())

    # A VIRER
    # Attendre avant de continuer
    # time.sleep(2)

    # Envoyer un message 'Bye' à tous les workers
    for client_socket in client_sockets:
        send_one_message(client_socket, b'Bye')

    # A VIRER
    # Attendre avant de terminer
    # time.sleep(2)

    return responses


def shuffle_to_other_workers(words_list_grp_worker):
    """
    Envoie des mots triés à d'autres workers.

    :param words_list_grp_worker: Dictionnaire de mots triés par worker.
    :return: Liste des réponses des workers.
    """

    # Récupère le nom de l'hôte actuel
    complete_hostname = f"{socket.gethostname()}.enst.fr"

    client_sockets = []
    machine_msgs = []
    for index, machine in enumerate(words_list_grp_worker):
        if machine != complete_hostname:
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.connect((machine, 65044))
            client_sockets.append(client_socket)
            machine_msgs.append(words_list_grp_worker[machine])
        else:
            # print(f"\n-------------------- AJOUT à ma propre liste {complete_hostname} -------------------\n")
            global_variables.my_words_list.append(
                words_list_grp_worker[machine])

    # Envoie des mots triés aux autres workers
    for index, client_socket in enumerate(client_sockets):
        send_one_message(client_socket, b'workers_shuffle_results')
        send_one_message(client_socket, str.encode(
            str(machine_msgs[index])))

    # Collecte les réponses des autres workers
    responses = []
    for client_socket in client_sockets:
        try:
            response = recv_one_message(client_socket)
        except ValueError:
            continue
        responses.append(response.decode())

    # A VIRER
    # Attendre avant de continuer
    # time.sleep(2)

    # Envoyer un message 'Bye' à tous les workers
    for client_socket in client_sockets:
        send_one_message(client_socket, b'Bye')

    # A VIRER
    # Attendre avant de terminer
    # time.sleep(2)

    return responses


def workers_functions(client_socket, message, address):
    """
    Traite les messages reçus des workers.

    :param client_socket: Socket du client.
    :param message: Message reçu.
    :param address: Adresse du client.
    """

    # Si le message est 'workers_liste_des_machines', récupère la liste des machines workers
    if message == 'workers_liste_des_machines':
        workers_list_str = recv_one_message(client_socket).decode().strip()
        global_variables.workers_list = ast.literal_eval(workers_list_str)
        global_variables.workers_list_initial = ast.literal_eval(
            workers_list_str)
        send_one_message(client_socket, b'OK workers_liste_des_machines')

    # Traite les autres types de messages
    elif message == 'workers_go':
        send_receive_worker_to_other_workers(
            global_variables.workers_list, 'workers_bonjour')
        send_one_message(client_socket, b'OK workers_go')
    elif message == 'workers_bonjour':
        send_one_message(client_socket, b'bonjour a toi aussi')
        print(f"Bonjour à toi aussi ami worker {address}")
    elif message == 'workers_start_map':
        filename = recv_one_message(client_socket).decode().strip()
        global_variables.words_list_grp_worker = words_count(
            filename, global_variables.workers_list_initial)
        send_one_message(client_socket, b'OK workers_start_map')
    elif message == 'workers_start_shuffle':
        shuffle_to_other_workers(global_variables.words_list_grp_worker)
        send_one_message(client_socket, b'OK workers_start_shuffle')
    elif message == 'workers_shuffle_results':
        workers_list_of_words = recv_one_message(
            client_socket).decode().strip()
        # print(f"\n------- workers_list_of_words --- {workers_list_of_words} par {socket.gethostname()} ------\n")
        global_variables.my_words_list.append(
            ast.literal_eval(workers_list_of_words))
        # print(f"\n------- Je suis {socket.gethostname()} et voici ma word_list_finale ------\n")
        send_one_message(client_socket, b'OK workers_shuffle_results')
    elif message == 'workers_show_shuffle_results':
        global_variables.my_words_list = sum_tuples(
            global_variables.my_words_list)
        print(
            f"------- {socket.gethostname()} - {global_variables.my_words_list} ------")
        send_one_message(
            client_socket, b'OK workers_show_shuffle_results')
