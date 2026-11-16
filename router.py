import sys
import socket

class PaqueteIP():

    def __init__(self, ip: str, puerto: int):
        self.ip = ip
        self.puerto = puerto

def parse_packet(ip_packet: bytes):
    """
    Parsea un paquete de bytes que contiene una dirección ip y puerto.
    El paquete debe ser de 6 bytes, donde los primeros cuatro representan la dirección ip
    y los últimos 2 el puerto asociado.

    Args:
        ip_packet (bytes): el paquete en bytes

    Returns:
        PaqueteIP: estructura que contiene una dirección ip y un puerto
    """

    if len(ip_packet) != 6:
        print("paquete no tiene el tamaño adecuado")
        return

    ip_numbers = []
    for i in range(4):
        ip_numbers.append(str(ip_packet[i]))

    ip = ".".join(ip_numbers)
    puerto = int.from_bytes(ip_packet[4:])

    return PaqueteIP(ip, puerto)


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

    return res


if __name__ == "__main__":

    if len(sys.argv) != 4:
        sys.exit("Modo de uso: router.py [router_IP] [router_puerto] [router_rutas].txt")

    ip = sys.argv[1]
    puerto = int(sys.argv[2])
    rutas = sys.argv[3]

    print(f"direccion IP:\t{ip}\tpuerto:\t{puerto}\ttabla de rutas:\t{rutas}\t")

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    buff_size = 32

    data = PaqueteIP(ip, puerto)
    p = create_packet(data)
    print(f"create_packet: {p}\tp[0]: {p[0]}\n")
    parsed = parse_packet(p)
    print(f"parse_packet:\t{parsed.ip}:{parsed.puerto}")

    try:
        sock.bind((ip, puerto))
    except Exception as e:
        print(f"error en bind: {e}")

    # while True:
    #     try:
    #         sock.recvfrom(buff_size)
    #     except KeyboardInterrupt:
    #         sys.exit()
    