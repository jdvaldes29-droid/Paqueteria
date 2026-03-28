import flet as ft
from app.supabase_client import supabase
from datetime import datetime


def estadisticas_view(page: ft.Page):

    hoy = datetime.now().date()

    paquetes = supabase.table("paquetes") \
        .select("*") \
        .execute()

    paquetes = paquetes.data

    asignados = 0
    entregados = 0
    incidencias = 0
    devueltos = 0

    for p in paquetes:

        if p["estatus"] == "ASIGNADO":
            asignados += 1

        elif p["estatus"] == "ENTREGADO":
            entregados += 1

        elif p["estatus"] == "NO_ENTREGADO":
            incidencias += 1

        elif p["estatus"] == "DEVUELTO_BODEGA":
            devueltos += 1

    total = entregados + incidencias

    cumplimiento = 0

    if total > 0:
        cumplimiento = round((entregados / total) * 100, 2)

    # ------------------------------------
    # TARJETAS KPI
    # ------------------------------------

    kpis = ft.Row(

        [

            tarjeta("Asignados", asignados, "📦"),

            tarjeta("Entregados", entregados, "✅"),

            tarjeta("Incidencias", incidencias, "⚠"),

            tarjeta("Devueltos", devueltos, "↩"),

        ],

        spacing=20

    )

    cumplimiento_txt = ft.Text(
        f"Cumplimiento del día: {cumplimiento} %",
        size=18,
        weight="bold"
    )

    # ------------------------------------
    # EFICIENCIA POR REPARTIDOR
    # ------------------------------------

    rep_query = supabase.table("repartidores") \
        .select("id,nombre") \
        .execute()

    repartidores = {
        r["id"]: r["nombre"]
        for r in rep_query.data
    }

    eficiencia = {}

    for p in paquetes:

        rid = p["repartidor_id"]

        if rid not in eficiencia:

            eficiencia[rid] = {
                "entregados": 0,
                "fallidos": 0
            }

        if p["estatus"] == "ENTREGADO":
            eficiencia[rid]["entregados"] += 1

        elif p["estatus"] == "NO_ENTREGADO":
            eficiencia[rid]["fallidos"] += 1

    rows = []

    for rid, stats in eficiencia.items():

        total = stats["entregados"] + stats["fallidos"]

        eficiencia_pct = 0

        if total > 0:
            eficiencia_pct = round(
                (stats["entregados"] / total) * 100,
                2
            )

        rows.append(

            ft.DataRow(

                cells=[

                    ft.DataCell(
                        ft.Text(
                            repartidores.get(rid, "Desconocido")
                        )
                    ),

                    ft.DataCell(
                        ft.Text(str(stats["entregados"]))
                    ),

                    ft.DataCell(
                        ft.Text(str(stats["fallidos"]))
                    ),

                    ft.DataCell(
                        ft.Text(f"{eficiencia_pct}%")
                    )

                ]

            )

        )

    tabla_eficiencia = ft.DataTable(

        columns=[

            ft.DataColumn(ft.Text("Repartidor")),

            ft.DataColumn(ft.Text("Entregados")),

            ft.DataColumn(ft.Text("Fallidos")),

            ft.DataColumn(ft.Text("Eficiencia"))

        ],

        rows=rows

    )

    return ft.Column(

        [

            ft.Text(
                "Estadísticas Operativas",
                size=28,
                weight="bold"
            ),

            ft.Divider(),

            kpis,

            ft.Divider(),

            cumplimiento_txt,

            ft.Divider(),

            ft.Text(
                "Eficiencia por repartidor",
                size=22,
                weight="bold"
            ),

            tabla_eficiencia

        ],

        expand=True,
        scroll=ft.ScrollMode.AUTO

    )


def tarjeta(titulo, valor, icono):

    return ft.Container(

        content=ft.Column(

            [

                ft.Text(icono, size=30),

                ft.Text(titulo),

                ft.Text(
                    str(valor),
                    size=28,
                    weight="bold"
                )

            ],

            horizontal_alignment="center"

        ),

        padding=20,

        border_radius=10,

        bgcolor="#f2f5f8",

        width=150

    )