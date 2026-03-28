import flet as ft
from app.supabase_client import supabase


def mapa_ruta_view(page: ft.Page):

    texto = ft.Text("Ruta del repartidor", size=22, weight="bold")

    lista = ft.Column()

    def cargar_ruta():

        res = supabase.table("ubicaciones") \
            .select("*") \
            .order("timestamp") \
            .execute()

        ubicaciones = res.data

        lista.controls.clear()

        for u in ubicaciones:

            lista.controls.append(

                ft.Text(
                    f"{u['latitud']} , {u['longitud']} | {u['timestamp']}"
                )

            )

        page.update()

    cargar_ruta()

    return ft.Column(
        [
            texto,
            ft.Divider(),
            lista
        ],
        expand=True
    )