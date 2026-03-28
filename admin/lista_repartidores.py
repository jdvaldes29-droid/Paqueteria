import flet as ft
from app.supabase_client import supabase


def lista_repartidores_view(page: ft.Page):

    tabla = ft.DataTable(

        columns=[

            ft.DataColumn(ft.Text("Nombre")),
            ft.DataColumn(ft.Text("Teléfono")),
            ft.DataColumn(ft.Text("Correo"))

        ],

        rows=[]

    )

    query = supabase.table("repartidores") \
        .select("*") \
        .execute()

    repartidores = query.data

    for r in repartidores:

        tabla.rows.append(

            ft.DataRow(

                cells=[

                    ft.DataCell(ft.Text(r["nombre"])),

                    ft.DataCell(ft.Text(r["telefono"])),

                    ft.DataCell(ft.Text(r["correo"]))

                ]

            )

        )

    return ft.Column(

        [

            ft.Text(
                "Repartidores",
                size=28,
                weight="bold"
            ),

            ft.Divider(),

            tabla

        ],

        expand=True

    )