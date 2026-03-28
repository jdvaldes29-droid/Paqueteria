import flet as ft
from app.supabase_client import supabase
from datetime import date


def alta_paquete_view(page: ft.Page):

    direccion = ft.TextField(label="Dirección", width=400)
    nombre_cliente = ft.TextField(label="Nombre del cliente", width=300)

    repartidores = supabase.table("repartidores").select("id,nombre").execute().data

    dropdown = ft.Dropdown(
        label="Asignar a repartidor",
        width=300,
        options=[
            ft.dropdown.Option(r["id"], r["nombre"]) for r in repartidores
        ],
    )

    mensaje = ft.Text()

    def guardar_paquete(e):

        if not direccion.value or not dropdown.value:
            mensaje.value = "Completa los campos obligatorios"
            mensaje.color = "red"
            page.update()
            return

        response = supabase.table("paquetes").insert({
            "direccion": direccion.value,
            "nombre_destinatario": nombre_cliente.value,
            "estatus": "ASIGNADO",
            "repartidor_id": dropdown.value,
            "fecha_asignacion": date.today().isoformat()
        }).execute()

        if response.data:
            mensaje.value = "Paquete asignado correctamente"
            mensaje.color = "green"

            direccion.value = ""
            nombre_cliente.value = ""
            dropdown.value = None
        else:
            mensaje.value = "Error al guardar paquete"
            mensaje.color = "red"

        page.update()

    return ft.Column(
        [
            ft.Text("📦 Alta de Paquete", size=22, weight="bold"),
            direccion,
            nombre_cliente,
            dropdown,
            ft.ElevatedButton("Guardar", on_click=guardar_paquete),
            mensaje,
        ],
        spacing=15,
    )