import flet as ft
from app.supabase_client import supabase


def obtener_eventos():

    response = supabase.table("paquetes") \
        .select("id, direccion, nombre_destinatario, estatus, motivo_no_entrega, fecha_asignacion") \
        .order("fecha_asignacion", desc=True) \
        .limit(10) \
        .execute()

    return response.data


def tabla_eventos():

    eventos = obtener_eventos()

    rows = []

    for e in eventos:

        motivo = e.get("motivo_no_entrega") or ""

        rows.append(
            ft.DataRow(
                cells=[
                    ft.DataCell(ft.Text(str(e["direccion"]))),
                    ft.DataCell(ft.Text(str(e["nombre_destinatario"]))),
                    ft.DataCell(ft.Text(str(e["estatus"]))),
                    ft.DataCell(ft.Text(str(motivo))),
                ]
            )
        )

    return ft.DataTable(

        columns=[

            ft.DataColumn(ft.Text("Dirección")),

            ft.DataColumn(ft.Text("Destinatario")),

            ft.DataColumn(ft.Text("Estatus")),

            ft.DataColumn(ft.Text("Motivo"))

        ],

        rows=rows

    )


def eventos_recientes_view():

    return ft.Column(

        [

            ft.Text(
                "Actividad reciente de paquetes",
                size=20,
                weight="bold"
            ),

            tabla_eventos()

        ]

    )