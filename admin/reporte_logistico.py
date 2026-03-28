import flet as ft
from app.supabase_client import supabase


def reporte_view(page: ft.Page):

    titulo = ft.Text(
        "Reporte Logístico",
        size=26,
        weight="bold"
    )

    repartidores = supabase.table("repartidores") \
        .select("*") \
        .execute().data

    rows = []

    for r in repartidores:

        paquetes = supabase.table("paquetes") \
            .select("*") \
            .eq("repartidor_id", r["id"]) \
            .execute().data

        asignados = len(paquetes)

        entregados = len([
            p for p in paquetes
            if p["estatus"] == "ENTREGADO"
        ])

        incidencias = len([
            p for p in paquetes
            if p["estatus"] == "NO_ENTREGADO"
        ])

        devueltos = len([
            p for p in paquetes
            if p["estatus"] == "DEVUELTO_BODEGA"
        ])

        eficiencia = 0

        if asignados > 0:
            eficiencia = round((entregados / asignados) * 100)

        rows.append(

            ft.DataRow(

                cells=[

                    ft.DataCell(ft.Text(r["nombre"])),

                    ft.DataCell(ft.Text(str(asignados))),

                    ft.DataCell(ft.Text(str(entregados))),

                    ft.DataCell(ft.Text(str(incidencias))),

                    ft.DataCell(ft.Text(str(devueltos))),

                    ft.DataCell(ft.Text(f"{eficiencia}%"))

                ]

            )

        )

    tabla = ft.DataTable(

        columns=[

            ft.DataColumn(ft.Text("Repartidor")),

            ft.DataColumn(ft.Text("Asignados")),

            ft.DataColumn(ft.Text("Entregados")),

            ft.DataColumn(ft.Text("Incidencias")),

            ft.DataColumn(ft.Text("Devueltos")),

            ft.DataColumn(ft.Text("Eficiencia"))

        ],

        rows=rows

    )

    return ft.Column(

        [

            titulo,

            ft.Divider(),

            tabla

        ],

        expand=True

    )