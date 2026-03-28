import threading
from supabase import create_client
import os
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# Diccionario con última ubicación por repartidor
ubicaciones_repartidores = {}

def iniciar_listener(callback):

    def escuchar():

        channel = supabase.channel("ubicaciones_realtime")

        channel.on(
            "postgres_changes",
            {
                "event": "INSERT",
                "schema": "public",
                "table": "ubicaciones",
            },
            lambda payload: procesar_evento(payload, callback)
        )

        channel.subscribe()

    hilo = threading.Thread(target=escuchar)
    hilo.daemon = True
    hilo.start()


def procesar_evento(payload, callback):

    data = payload["new"]

    repartidor_id = data["repartidor_id"]
    lat = data["latitud"]
    lon = data["longitud"]

    ubicaciones_repartidores[repartidor_id] = (lat, lon)

    if callback:
        callback(repartidor_id, lat, lon)