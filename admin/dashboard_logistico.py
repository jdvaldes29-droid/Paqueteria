import flet as ft
from app.supabase_client import supabase


def dashboard_view(page: ft.Page):

    paquetes = supabase.table("paquetes").select("*").execute().data

    total = len(paquetes)

    en_bodega = len([p for p in paquetes if p["estatus"] == "EN_BODEGA"])

    asignados = len([p for p in paquetes if p["estatus"] == "ASIGNADO"])

    en_ruta = len([p for p in paquetes if p["estatus"] == "EN_RUTA"])

    entregados = len([p for p in paquetes if p["estatus"] == "ENTREGADO"])

    incidencias = len([p for p in paquetes if p["estatus"] == "NO_ENTREGADO"])

    devueltos = len([p for p in paquetes if p["estatus"] == "DEVUELTO_BODEGA"])

    eficiencia = 0

    if total > 0:
        eficiencia = round((entregados / total) * 100)

    def card(titulo, valor, color):

        return ft.Container(

            content=ft.Column(

                [

                    ft.Text(titulo, size=14),

                    ft.Text(
                        str(valor),
                        size=30,
                        weight="bold"
                    )

                ],

                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER

            ),

            bgcolor=color,
            padding=20,
            border_radius=10,
            width=200

        )

    kpis = ft.Row(

        [

            card("Total Recibidos", total, "#e3f2fd"),

            card("En Bodega", en_bodega, "#fff9c4"),

            card("Asignados", asignados, "#bbdefb"),

            card("En Ruta", en_ruta, "#90caf9"),

            card("Entregados", entregados, "#c8e6c9"),

            card("Incidencias", incidencias, "#ffcdd2"),

            card("Devueltos", devueltos, "#ffe0b2"),

            card("Eficiencia %", eficiencia, "#d1c4e9")

        ],

        wrap=True

    )

    return ft.Column(

        [

            ft.Text(
                "Dashboard Logístico",
                size=28,
                weight="bold"
            ),

            ft.Divider(),

            kpis

        ],

        expand=True

    )