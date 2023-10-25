import struct


def send_one_message(sock, data):
    """
    Envoie un seul message à travers le socket donné.

    Args:
    - sock (socket): Le socket à travers lequel le message sera envoyé.
    - data (bytes): Les données à envoyer.

    Cette fonction envoie d'abord la longueur des données sous la forme d'un entier de 4 octets,
    puis les données elles-mêmes.
    """
    length = len(data)
    # Emballez la longueur des données sous la forme d'un entier de 4 octets
    sock.sendall(struct.pack('!I', length))
    # Envoyez les données elles-mêmes
    sock.sendall(data)


def recvall(sock, count):
    """
    Reçoit une quantité exacte d'octets du socket donné.

    Args:
    - sock (socket): Le socket à partir duquel les octets seront reçus.
    - count (int): Le nombre d'octets à recevoir.

    Returns:
    - bytes: Les octets reçus, ou None si la fin de la connexion est atteinte avant que tous les octets ne soient reçus.
    """
    fragments = []
    while count:
        # Recevez jusqu'à 'count' octets
        chunk = sock.recv(count)
        if not chunk:
            # Si aucun octet n'est reçu, retournez None
            return None
        fragments.append(chunk)
        count -= len(chunk)

    # Combinez tous les fragments en un seul objet bytes et retournez-le
    arr = b''.join(fragments)
    return arr


def recv_one_message(sock):
    """
    Reçoit un seul message du socket donné.

    Args:
    - sock (socket): Le socket à partir duquel le message sera reçu.

    Returns:
    - bytes: Le message reçu.

    Raises:
    - ValueError: Si le message n'est pas reçu correctement.

    Cette fonction lit d'abord la longueur du message attendu, puis le message lui-même.
    """
    # Reçoit la longueur du message
    lengthbuf = recvall(sock, 4)
    if lengthbuf is None:
        raise ValueError("Failed to receive message length")

    # Décoder la longueur du message
    length, = struct.unpack('!I', lengthbuf)

    # Reçoit le message lui-même
    message = recvall(sock, length)
    if message is None:
        raise ValueError("Failed to receive message body")

    return message
