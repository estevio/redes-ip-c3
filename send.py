import socket
from router import PaqueteIP, create_packet


destino = input("Direccion router de destino: ")
msg = input("Mensaje: ")
envio = input("Direccion router de envio: ")

try:
    ip_destino, puerto_destino = destino.split(" ")
    puerto_destino = int(puerto_destino)
    ip_envio, puerto_envio = envio.split(" ")
    puerto_envio = int(puerto_envio)
except:
    print("Error al parsear dirección de destino/envio\nUtilice el formato [IP] [puerto]")
    print("Ejemplo: \"127.0.0.1 8882\"")

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

pack = create_packet(PaqueteIP(ip_destino, puerto_destino, msg))
sock.sendto(pack, (ip_envio, puerto_envio))