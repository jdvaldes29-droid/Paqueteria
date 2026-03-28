import flet as ft
from app.supabase_client import supabase
from datetime import datetime, timezone


def repartidores_activos_view(page: ft.Page):

    tabla = ft.DataTable(
        columns=[
            ft.DataColumn(ft.Text("Repartidor")),
            ft.DataColumn(ft.Text("Latitud")),
            ft.DataColumn(ft.Text("Longitud")),
            ft.DataColumn(ft.Text("Última actualización")),
            ft.DataColumn(ft.Text("Estado"))
        ],
        rows=[]
    )

    def cargar():

        # Obtener nombres de repartidores
        rep_query = supabase.table("repartidores") \
            .select("id,nombre") \
            .execute()

        nombres = {
            r["id"]: r["nombre"]
            for r in rep_query.data
        }

        # Obtener ubicaciones (ordenadas por timestamp)
        query = supabase.table("ubicaciones") \
            .select("*") \
            .order("timestamp", desc=True) \
            .execute()

        ubicaciones = query.data

        tabla.rows.clear()

        vistos = set()

        ahora = datetime.now(timezone.utc)

        for u in ubicaciones:

            rid = u["repartidor_id"]

            # solo la última ubicación de cada repartidor
            if rid in vistos:
                continue

            vistos.add(rid)

            lat = u["latitud"]
            lon = u["longitud"]
            ts = u["timestamp"]

            try:
                ultima = datetime.fromisoformat(
                    ts.replace("Z", "+00:00")
                )

                minutos = (ahora - ultima).total_seconds() / 60

            except:
                minutos = 999

            # determinar estado

            if minutos <= 2:
                estado = "ACTIVO"
                color = "green"

            elif minutos <= 10:
                estado = "INACTIVO"
                color = "orange"

            else:
                estado = "DESCONECTADO"
                color = "red"

            tabla.rows.append(

                ft.DataRow(

                    cells=[

                        ft.DataCell(
                            ft.Text(nombres.get(rid, "Desconocido"))
                        ),

                        ft.DataCell(ft.Text(str(lat))),

                        ft.DataCell(ft.Text(str(lon))),

                        ft.DataCell(ft.Text(ts)),

                        ft.DataCell(

                            ft.Container(

                                content=ft.Text(
                                    estado,
                                    color="white"
                                ),

                                bgcolor=color,
                                padding=5,
                                border_radius=5

                            )

                        )

                    ]

                )

            )

        page.update()

    # cargar al abrir
    cargar()

    return ft.Column(

        [

            ft.Text(
                "Monitor de Repartidores",
                size=28,
                weight="bold"
            ),

            ft.Divider(),

            tabla,

            ft.ElevatedButton(
                "Actualizar",
                on_click=lambda e: cargar()
            )

        ],

        expand=True,
        scroll=ft.ScrollMode.AUTO

    )