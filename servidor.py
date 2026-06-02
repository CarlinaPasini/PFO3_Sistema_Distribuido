import socket
import json
from concurrent.futures import ThreadPoolExecutor
import time

# Configuración del servidor central de sockets
HOST = '127.0.0.1'
PORT = 6000
MAX_WORKERS = 3  # Tamaño definido para el Pool de Hilos (Workers)

def procesar_tarea_worker(tarea, cliente_id):
    """
    Función asignada a los hilos del Worker Pool.
    Simula el procesamiento distribuido y la interacción con la infraestructura.
    """
    print(f"\n[WORKER] Iniciando procesamiento de Tarea ID: {tarea['id']} para el {cliente_id}...")
    
    # Simulación de pasos de la arquitectura del diagrama:
    # 1. Conexión y persistencia de metadatos en PostgreSQL.
    # 2. Coordinación de eventos secundarios en la cola RabbitMQ.
    # 3. Subida de binarios pesados o imágenes médicas a Amazon S3.
    time.sleep(2)  
    
    resultado = {
        "status": "COMPLETED",
        "tarea_id": tarea["id"],
        "mensaje": f"La tarea '{tarea['nombre']}' fue procesada con éxito por el Pool de Workers.",
        "timestamp_finalizacion": time.time()
    }
    print(f"[WORKER] Finalizada Tarea ID: {tarea['id']}.")
    return resultado

def manejar_conexion_cliente(conn, addr):
    """
    Administra el ciclo de vida de la conexión por socket del cliente.
    """
    print(f"[NUEVA CONEXIÓN] Cliente conectado desde la dirección: {addr}")
    
    # Inicializamos el Pool de Hilos para distribuir el trabajo
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        try:
            while True:
                # Recibimos el paquete de datos del socket
                datos_recibidos = conn.recv(1024).decode('utf-8')
                if not datos_recibidos:
                    break # Si no hay datos, el cliente se desconectó
                
                # Deserializamos la petición estructurada
                peticion = json.loads(datos_recibidos)
                tarea = peticion.get("tarea")
                cliente_id = peticion.get("cliente_id")
                
                print(f"[ORQUESTADOR] Distribuyendo Tarea {tarea['id']} enviada por {cliente_id} al pool...")
                
                # ASIGNACIÓN ASÍNCRONA: El orquestador delega la tarea al pool de hilos
                futuro_trabajo = executor.submit(procesar_tarea_worker, tarea, cliente_id)
                
                # Obtenemos el resultado una vez que el hilo termina su ejecución
                resultado_worker = futuro_trabajo.result()
                
                # Enviamos la respuesta de éxito de vuelta al cliente mediante el socket
                conn.send(json.dumps(resultado_worker).encode('utf-8'))
                
        except Exception as e:
            print(f"[ERROR] Ocurrió un fallo con el cliente {addr}: {e}")
        finally:
            conn.close()
            print(f"[CONEXIÓN CERRADA] Cliente {addr} desconectado.")

def iniciar_orquestador():
    # Configuración del Socket TCP nativo
    servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    servidor.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) # Evita puerto bloqueado
    servidor.bind((HOST, PORT))
    servidor.listen()
    
    print(f"[SISTEMA DISTRIBUIDO] Servidor listo y escuchando en {HOST}:{PORT}")
    print(f"[INFRAESTRUCTURA] Pool de Workers configurado con un límite de {MAX_WORKERS} hilos.")

    try:
        while True:
            # Aceptamos conexiones entrantes
            conn, addr = servidor.accept()
            manejar_conexion_cliente(conn, addr)
    except KeyboardInterrupt:
        print("\n[APAGANDO] Servidor Orquestador detenido de forma segura.")
    finally:
        servidor.close()

if __name__ == "__main__":
    iniciar_orquestador()