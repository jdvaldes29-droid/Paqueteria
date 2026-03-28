import flet as ft
from app.supabase_client import supabase
from datetime import date
import uuid
import os


def entrega_view(page: ft.Page, paquete):

    quien_recibe = ft.TextField(label="¿Quién recibe?", width=300)
    foto = ft.FilePicker()
    page.overlay.append(foto)

    foto_path = {"path": None}

    mensaje = ft.Text()

    def seleccionar_foto(e):
        foto.pick_files(allow_multiple=False)

    def on_result(e: ft.FilePickerResultEvent):
        if e.files:
            foto_path["path"] = e.files[0].path
            mensaje.value = "Foto seleccionada"
            page.update()

    foto.on_result = on_result

    def guardar_entrega(e):

        if not quien_recibe.value or not foto_path["path"]:
            mensaje.value = "Debes completar todos los campos"
            mensaje.color = "red"
            page.update()
            return

        # Generar nombre único
        nombre_archivo = f"{uuid.uuid4()}.jpg"

        with open(foto_path["path"], "rb") as f:
            contenido = f.read()

        # Subir a Storage
        supabase.storage.from_("evidencias").upload(
            nombre_archivo,
            contenido
        )

        # Obtener URL pública
        url = supabase.storage.from_("evidencias").get_public_url(nombre_archivo)

        # Insertar en entregas
        supabase.table("entregas").insert({
            "paquete_id": paquete["id"],
            "quien_recibe": quien_recibe.value,
            "foto_url": url,
            "fecha_entrega": date.today().isoformat()
        }).execute()

        # Actualizar estatus
        supabase.table("paquetes").update({
            "estatus": "ENTREGADO"
        }).eq("id", paquete["id"]).execute()

        mensaje.value = "Entrega registrada correctamente"
        mensaje.color = "green"
        page.update()

    return ft.Column(
        [
            ft.Text("📦 Registrar Entrega", size=22, weight="bold"),
            ft.Text(f"Dirección: {paquete['direccion']}"),
            quien_recibe,
            ft.ElevatedButton("📸 Seleccionar Foto", on_click=seleccionar_foto),
            ft.ElevatedButton("Guardar Entrega", on_click=guardar_entrega),
            mensaje,
        ],
        spacing=15
    )