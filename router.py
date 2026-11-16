import sys
import socket

class PaqueteIP():

    def __init__(self, ip: str, puerto: int, msg: str):
        self.ip = ip
        self.puerto = puerto
        self.msg = msg

def parse_packet(ip_packet: bytes):
    """
    Parsea un paquete de bytes que contiene una dirección ip y puerto.
    El paquete debe contener al menos 6 bytes, 
    donde los primeros cuatro representan la dirección ip
    y los siguientes 2 el puerto asociado.

    Args:
        ip_packet (bytes): el paquete en bytes

    Returns:
        PaqueteIP: estructura que contiene una dirección ip y un puerto
    """

    if len(ip_packet) < 6:
        print("paquete no tiene el tamaño adecuado")
        return

    ip_numbers = []
    for i in range(4):
        ip_numbers.append(str(ip_packet[i]))

    ip = ".".join(ip_numbers)
    puerto = int.from_bytes(ip_packet[4:6])
    msg = ip_packet[6:].decode()

    return PaqueteIP(ip, puerto, msg)


def create_packet(data: PaqueteIP):
    """
    Crea un paquete de bytes a partir de un objeto PaqueteIP

    Args:
        data (PaqueteIP): la informacion del paquete
    
    Returns:
        bytes: el paquete de bytes
    """
    ip_numbers = data.ip.split(".")
    res = b""
    for n in ip_numbers:
        res += int(n).to_bytes()
    res += data.puerto.to_bytes(2)
    res += data.msg.encode()

    return res

def check_routes(routes_file_name: str, destination_address: tuple[str, int]):
    """
    Busca la dirección de destino destination_address en la tabla de rutas almacenada
    en el archivo txt routes_file_name

    Args: 
        routes_file_name (str): nombre del archivo de la tabla de rutas
        destination_address (tuple[str, int]): par que representa la dirección de destino (IP, puerto)

    Returns:
        tuple[str, int]: tupla que representa la dirección del siguiente salto
        None: si no se encuentra la dirección solicitada
    """

    with open(routes_file_name) as tabla:
        row = tabla.readline()
        while row:

            try:
                ip_destino, i, j, ip_salto, puerto_salto = row.split(" ")
                ip_destino = ip_destino.split("/")[0]
            except:
                print("error al leer linea")
                return

            if (ip_destino == destination_address[0] and int(i) <= destination_address[1] <= int(j)):
                return (ip_salto, int(puerto_salto))
            row = tabla.readline()

        return None


if __name__ == "__main__":

    if len(sys.argv) != 4:
        sys.exit("Modo de uso: router.py [router_IP] [router_puerto] [router_rutas].txt")

    ip = sys.argv[1]
    puerto = int(sys.argv[2])
    rutas = sys.argv[3]

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    buff_size = 32

    try:
        sock.bind((ip, puerto))
    except Exception as e:
        print(f"error en bind: {e}")

    while True:
        try:
            bts, _ = sock.recvfrom(buff_size)
            print(parse_packet(bts).msg)
            
        except KeyboardInterrupt:
            sys.exit()
    