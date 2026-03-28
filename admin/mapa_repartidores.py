import flet as ft
from supabase import create_client
import os
import threading
import time
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

tabla = None


def obtener_ubicaciones():

    response = supabase.table("ubicaciones") \
        .select("*") \
        .order("timestamp", desc=True) \
        .limit(20) \
        .execute()

    return response.data


def actualizar_tabla():

    global tabla

    ubicaciones = obtener_ubicaciones()

    filas = []

    for u in ubicaciones:

        fila = ft.DataRow(
            cells=[
                ft.DataCell(ft.Text(str(u["repartidor_id"]))),
                ft.DataCell(ft.Text(str(u["latitud"]))),
                ft.DataCell(ft.Text(str(u["longitud"]))),
                ft.DataCell(ft.Text(str(u["timestamp"]))),
            ]
        )

        filas.append(fila)

    tabla.rows = filas
    tabla.update()


def loop_actualizacion():

    while True:

        try:
            actualizar_tabla()
        except Exception as e:
            print("Error actualizando ubicaciones:", e)

        time.sleep(5)


def mapa_repartidores_view(page: ft.Page):

    global tabla

    titulo = ft.Text(
        "Seguimiento de Repartidores",
        size=24,
        weight="bold"
    )

    tabla = ft.DataTable(
        columns=[
            ft.DataColumn(ft.Text("Repartidor")),
            ft.DataColumn(ft.Text("Latitud")),
            ft.DataColumn(ft.Text("Longitud")),
            ft.DataColumn(ft.Text("Timestamp")),
        ],
        rows=[]
    )

    threading.Thread(
        target=loop_actualizacion,
        daemon=True
    ).start()

    return ft.Column([
        titulo,
        ft.Divider(),
        tabla
    ])