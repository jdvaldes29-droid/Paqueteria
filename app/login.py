import flet as ft
from app.supabase_client import supabase


def login_view(page: ft.Page, on_success):

    email = ft.TextField(label="Correo", width=300)
    password = ft.TextField(label="Contraseña", password=True, width=300)
    error_text = ft.Text(color="red")

    def do_login(e):

        try:

            res = supabase.auth.sign_in_with_password({

                "email": email.value,
                "password": password.value

            })

            # buscar usuario en tabla usuarios usando email

            user_db = supabase.table("usuarios") \
                .select("*") \
                .eq("email", email.value) \
                .single() \
                .execute()

            usuario = user_db.data

            repartidor_id = usuario["repartidor_id"]

            # obtener nombre del repartidor

            rep = supabase.table("repartidores") \
                .select("nombre") \
                .eq("id", repartidor_id) \
                .single() \
                .execute()

            repartidor = rep.data

            usuario_app = {

                "repartidor_id": repartidor_id,
                "nombre": repartidor["nombre"],
                "email": email.value

            }

            on_success(usuario_app)

        except Exception as ex:

            print(ex)

            error_text.value = "Credenciales incorrectas"
            page.update()

    return ft.Column(

        [

            ft.Text(
                "Ingreso Repartidor",
                size=22,
                weight="bold"
            ),

            email,

            password,

            ft.ElevatedButton(
                "Entrar",
                on_click=do_login
            ),

            error_text,

        ],

        alignment=ft.MainAxisAlignment.CENTER,

        horizontal_alignment=ft.CrossAxisAlignment.CENTER

    )