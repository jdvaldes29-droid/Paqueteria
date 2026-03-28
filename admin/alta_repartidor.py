import flet as ft
from admin.supabase_admin import supabase_admin
import uuid

def alta_repartidor_view(page: ft.Page):

    nombre = ft.TextField(label="Nombre completo")
    telefono = ft.TextField(label="Teléfono")
    correo = ft.TextField(label="Correo electrónico")
    password = ft.TextField(label="Contraseña inicial", password=True)

    mensaje = ft.Text()

    def guardar(e):
        try:
            # 1️⃣ Crear repartidor
            rep = supabase_admin.table("repartidores").insert({
                "nombre": nombre.value,
                "telefono": telefono.value,
                "correo": correo.value,
                "activo": True
            }).execute()

            repartidor_id = rep.data[0]["id"]

            # 2️⃣ Crear usuario Auth
            auth_user = supabase_admin.auth.admin.create_user({
                "email": correo.value,
                "password": password.value,
                "email_confirm": True
            })

            auth_user_id = auth_user.user.id

            # 3️⃣ Crear vínculo en usuarios
            supabase_admin.table("usuarios").insert({
                "auth_user_id": auth_user_id,
                "email": correo.value,
                "rol": "REPARTIDOR",
                "repartidor_id": repartidor_id
            }).execute()

            mensaje.value = "✅ Repartidor creado correctamente"
            mensaje.color = "green"

            nombre.value = telefono.value = correo.value = password.value = ""

        except Exception as ex:
            mensaje.value = f"❌ Error: {ex}"
            mensaje.color = "red"

        page.update()

    return ft.Column(
        [
            ft.Text("Alta de Repartidor", size=20, weight="bold"),
            nombre,
            telefono,
            correo,
            password,
            ft.ElevatedButton("Crear repartidor", on_click=guardar),
            mensaje
        ],
        width=400
    )