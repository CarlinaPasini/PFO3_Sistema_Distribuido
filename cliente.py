import socket
import json

HOST = '127.0.0.1'
PORT = 6000

def enviar_solicitud_sistema():
    # Inicializamos el socket TCP del cliente
    cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    try:
        cliente.connect((HOST, PORT))
        print(f"[CONECTADO] Enlace establecido con el sistema en {HOST}:{PORT}")
        
        # Estructuramos una tarea de prueba (ejemplo: procesamiento de imagen médica)
        peticion_distribuida = {
            "cliente_id": "APLICACION_WEB_01",
            "tarea": {
                "id": 505,
                "nombre": "Procesamiento y Filtrado de Imagen Médica",
                "prioridad": "CRÍTICA"
            }
        }
        
        print(f"[ENVÍO] Enviando Tarea ID {peticion_distribuida['tarea']['id']} por la red...")
        # Serializamos a JSON y enviamos los bytes por el socket
        cliente.send(json.dumps(peticion_distribuida).encode('utf-8'))
        
        print("[ESPERA] Aguardando respuesta del pool de procesamiento remoto...")
        # Bloqueamos el flujo hasta recibir la respuesta del servidor
        bytes_recibidos = cliente.recv(1024).decode('utf-8')
        
        if bytes_recibidos:
            respuesta_servidor = json.loads(bytes_recibidos)
            print("\n[RESULTADO RECIBIDO DESDE EL SERVIDOR WORKER]:")
            print(json.dumps(respuesta_servidor, indent=4, ensure_ascii=False))
            
    except Exception as e:
        print(f"[FALLO DE RED] Error al intentar comunicar con la infraestructura: {e}")
    finally:
        cliente.close()
        print("\n[DESCONECTADO] Socket de cliente cerrado de forma segura.")

if __name__ == "__main__":
    enviar_solicitud_sistema()