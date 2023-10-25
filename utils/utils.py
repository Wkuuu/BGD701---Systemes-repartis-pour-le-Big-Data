# Importation des bibliothèques nécessaires
from collections import defaultdict
import hashlib
import os
from .messages import recv_one_message, send_one_message


def get_machines():
    """
    Récupère la liste des machines à partir d'un fichier nommé 'machines.txt'.

    Returns:
    - list: Liste des noms des machines.

    Note:
    Cette fonction ignore la première ligne du fichier, qui pourrait être un en-tête.
    """
    machines = []  # Initialiser une liste vide pour les machines
    # Ouvrir et lire le fichier
    with open('./machines.txt', 'r', encoding='utf-8') as f:
        for line in f:
            machines.append(line.strip())
    # Supprimer le premier élément (peut-être un en-tête ou une ligne non désirée)
    machines.pop(0)
    return machines


def calcul_worker(key, workers_list_initial):
    """
    Calcule le worker associé à une clé donnée.

    Args:
    - key (str): Clé pour laquelle le worker doit être calculé.
    - workers_list_initial (list): Liste des workers.

    Returns:
    - str: Nom du worker associé à la clé.
    """
    # Hacher la clé
    hashed_key = hashlib.sha256(key.encode()).hexdigest()
    # Convertir la clé hachée en entier
    integer_key = int(hashed_key, 16)
    # Trouver l'index du worker en utilisant le modulo
    index = integer_key % len(workers_list_initial)
    return workers_list_initial[index]


def words_count(filename, workers_list_initial):
    """
    Compte les occurrences de mots dans un fichier et groupe les résultats par machine.

    Args:
    - filename (str): Nom du fichier à traiter.
    - workers_list_initial (list): Liste des workers.

    Returns:
    - dict: Dictionnaire groupant les mots et leurs occurrences par machine.
    """
    folder_path = './splits/'
    file_path = os.path.join(folder_path, filename)
    # Ouvrir et lire le fichier
    with open(file_path, 'r', encoding='utf-8') as f:
        text = f.read()
    # Diviser le texte en mots et nettoyer chaque mot
    mots = text.lower().split()
    mots = [''.join(e for e in mot if e.isalnum()) for mot in mots]

    dictionnaire = {}
    # Compter les occurrences de chaque mot
    for mot in mots:
        if mot not in dictionnaire:
            worker = calcul_worker(mot, workers_list_initial)
            dictionnaire[mot] = (1, worker)
        else:
            count, _ = dictionnaire[mot]
            dictionnaire[mot] = (count + 1, _)

    # Initialiser un nouveau dictionnaire pour regrouper les résultats par machine
    grouped_by_machine = defaultdict(list)

    # Grouper les résultats par machine
    for mot, (count, machine) in dictionnaire.items():
        grouped_by_machine[machine].append((mot, count))

    return dict(grouped_by_machine)


def receive_file(client_socket):
    """
    Reçoit un fichier à travers le socket spécifié.

    Args:
    - client_socket (socket): Le socket à travers lequel le fichier est reçu.

    Cette fonction lit le nom et la taille du fichier à recevoir, puis reçoit 
    le fichier en morceaux et le stocke localement.
    """
    # Recevoir le nom et la taille du fichier
    filename = recv_one_message(client_socket).decode().strip()
    filesize = int(recv_one_message(client_socket).decode().strip())
    # Écrire les données reçues dans un fichier
    with open(filename, 'wb') as f:
        remaining_bytes = filesize
        while remaining_bytes > 0:
            data = recv_one_message(client_socket)
            if not data:
                break
            f.write(data)
            remaining_bytes -= len(data)
    # Envoyer une confirmation de réception
    send_one_message(client_socket, b'File received')


def sum_tuples(data):
    """
    Somme les tuples contenant des mots et leurs occurrences.

    Args:
    - data (list): Liste contenant des sous-listes de tuples (mot, count).

    Returns:
    - dict: Dictionnaire avec des mots comme clés et leurs sommes cumulées comme valeurs.
    """
    result = defaultdict(int)
    # Parcourir chaque sous-liste et ajouter les valeurs pour chaque mot
    for sublist in data:
        for key, value in sublist:
            result[key] += value
    return dict(result)
