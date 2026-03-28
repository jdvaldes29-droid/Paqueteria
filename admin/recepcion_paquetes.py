import flet as ft
from app.supabase_client import supabase
from datetime import datetime


def recepcion_view(page: ft.Page):

    codigo = ft.TextField(
        label="Escanear código",
        autofocus=True
    )

    lista = ft.Column(scroll=ft.ScrollMode.AUTO)

    def registrar(e):

        if not codigo.value:
            return

        try:

            supabase.table("paquetes").insert({

                "codigo": codigo.value,
                "estatus": "EN_BODEGA",
                "fecha_recepcion": datetime.now().isoformat()

            }).execute()

            lista.controls.insert(

                0,

                ft.Text(
                    f"📦 {codigo.value}"
                )

            )

            codigo.value = ""

            page.update()

        except Exception as ex:

            page.snack_bar = ft.SnackBar(
                ft.Text(str(ex))
            )

            page.snack_bar.open = True
            page.update()

    codigo.on_submit = registrar

    return ft.Column(

        [

            ft.Text(
                "Recepción de Paquetes",
                size=24,
                weight="bold"
            ),

            codigo,

            ft.Divider(),

            lista

        ],

        expand=True

    )