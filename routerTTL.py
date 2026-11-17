import sys
import socket

class PaqueteIP():

    def __init__(self, ip: str, puerto: int, msg: str, ttl: int = 255):
        self.ip = ip
        self.puerto = puerto
        self.ttl = ttl
        self.msg = msg

def parse_packet(ip_packet: bytes):
    """
    Parsea un paquete de bytes que contiene una dirección ip y puerto.
    El paquete debe contener al menos 7 bytes, 
    donde los primeros cuatro representan la dirección ip,
    los siguientes 2 el puerto asociado
    y el último representa el TTL (time to live).

    Args:
        ip_packet (bytes): el paquete en bytes

    Returns:
        PaqueteIP: estructura que contiene una dirección ip y un puerto
    """

    if len(ip_packet) < 7:
        print("paquete no tiene el tamaño adecuado")
        return

    ip_numbers = []
    for i in range(4):
        ip_numbers.append(str(ip_packet[i]))

    ip = ".".join(ip_numbers)
    puerto = int.from_bytes(ip_packet[4:6])
    ttl = ip_packet[6]
    msg = ip_packet[7:].decode()

    return PaqueteIP(ip, puerto, msg, ttl)


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
    res += data.ttl.to_bytes()
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
        ips_posibles = []
        while row:

            try:
                ip_destino, i, j, ip_salto, puerto_salto = row.split(" ")
                puerto_salto = int(puerto_salto)
                ip_destino = ip_destino.split("/")[0]
            except:
                print("error al leer linea")
                return

            if (ip_destino == destination_address[0] and int(i) <= destination_address[1] <= int(j)):
                ips_posibles.append((ip_salto, int(puerto_salto)))
                #print(f"puerto salto: {puerto_salto}\tpuerto destino: {destination_address[1]}\n")
                if ip_salto == destination_address[0] and puerto_salto == destination_address[1]:
                    return (ip_salto, puerto_salto)
            
            row = tabla.readline()

        if not ips_posibles:
            return None

        # ips posibles que no estan dentro de cola ips
        # no_visitadas = filter(lambda x: x not in cola_ips, ips_posibles)
        no_visitadas = [x for x in ips_posibles if x not in cola_ips]
        if no_visitadas:
            return no_visitadas[0]
        # ips posibles que estan en la cola de ips
        visitadas = [x for x in cola_ips if x in ips_posibles]
        if visitadas:
            return visitadas.pop(0)


if __name__ == "__main__":

    if len(sys.argv) != 4:
        sys.exit("Modo de uso: router.py [router_IP] [router_puerto] [router_rutas].txt")

    ip = sys.argv[1]
    puerto = int(sys.argv[2])
    rutas = sys.argv[3]
    buff_size = 32
    #global cola_ips
    cola_ips = []

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    try:
        sock.bind((ip, puerto))
    except Exception as e:
        print(f"error en bind: {e}")

    while True:
        try:
            bts, ip_paquete = sock.recvfrom(buff_size)
            data = parse_packet(bts)
            # el paquete es para mi?
            if data.ip == ip and data.puerto == puerto:
                print(data.msg)
            else:
                next_addr = check_routes(rutas, (data.ip, data.puerto))
                if next_addr:
                    # print(f"redirigiendo paquete {ip_paquete} con destino final {data.ip}:{data.puerto} " +
                    #       f"desde {ip}:{puerto} hacia {next_addr[0]}:{next_addr[1]}")
                    print(f"redirigiendo paquete con destino final {data.puerto} " +
                            f"desde {puerto} hacia {next_addr[1]}")
                    if next_addr in cola_ips:
                        cola_ips.remove(next_addr)
                    cola_ips.append(next_addr)
                    sock.sendto(bts, next_addr)
                else:
                    print(f"No hay rutas hacia {ip}:{puerto} para paquete {ip_paquete}")

        except KeyboardInterrupt:
            sys.exit()
    