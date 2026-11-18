import sys
import socket
from routerTTL import PaqueteIP, create_packet

if len(sys.argv) != 4:
    sys.exit("Modo de uso: prueba_router.py [IP_destino];[Puerto_destino];[TTL] " +
             "[IP_router_inicial] [puerto_router_inicial]")

headers, ip_inicial, puerto_inicial = sys.argv[1:]
headers = headers.split(";")

archivo = input("Ruta del archivo txt a enviar: ")

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

with open(archivo) as txt:
    line = txt.readline()
    while line:
        pack = create_packet(PaqueteIP(headers[0], int(headers[1]), line, int(headers[2])))
        sock.sendto(pack, (ip_inicial, int(puerto_inicial)))
        line = txt.readline()

sock.close()