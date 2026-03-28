import flet as ft
from app.supabase_client import supabase


def paquetes_view(page: ft.Page):

    direccion = ft.TextField(label="Dirección", width=400)

    destinatario = ft.TextField(
        label="Nombre destinatario",
        width=400
    )

    # ------------------------------------
    # CARGAR REPARTIDORES
    # ------------------------------------

    rep_query = supabase.table("repartidores") \
        .select("id,nombre") \
        .execute()

    repartidores = rep_query.data

    opciones_repartidores = [
        ft.dropdown.Option(r["id"], r["nombre"])
        for r in repartidores
    ]

    repartidor = ft.Dropdown(
        label="Asignar repartidor",
        options=opciones_repartidores,
        width=400
    )

    mensaje = ft.Text()

    tabla = ft.DataTable(

        columns=[

            ft.DataColumn(ft.Text("ID")),
            ft.DataColumn(ft.Text("Dirección")),
            ft.DataColumn(ft.Text("Destinatario")),
            ft.DataColumn(ft.Text("Repartidor")),
            ft.DataColumn(ft.Text("Estatus"))

        ],

        rows=[]

    )

    # ------------------------------------
    # CREAR PAQUETE
    # ------------------------------------

    def crear_paquete(e):

        supabase.table("paquetes").insert({

            "direccion": direccion.value,
            "nombre_destinatario": destinatario.value,
            "repartidor_id": repartidor.value,
            "estatus": "ASIGNADO"

        }).execute()

        mensaje.value = "Paquete creado correctamente"

        cargar_paquetes()

        page.update()

    # ------------------------------------
    # CARGAR TABLA
    # ------------------------------------

    def cargar_paquetes():

        query = supabase.table("paquetes") \
            .select("*") \
            .order("id", desc=True) \
            .execute()

        paquetes = query.data

        tabla.rows.clear()

        for p in paquetes:

            tabla.rows.append(

                ft.DataRow(

                    cells=[

                        ft.DataCell(ft.Text(str(p["id"]))),

                        ft.DataCell(ft.Text(p["direccion"])),

                        ft.DataCell(ft.Text(p["nombre_destinatario"])),

                        ft.DataCell(ft.Text(str(p["repartidor_id"]))),

                        ft.DataCell(ft.Text(p["estatus"]))

                    ]

                )

            )

    cargar_paquetes()

    return ft.Column(

        [

            ft.Text(
                "Gestión de Paquetes",
                size=28,
                weight="bold"
            ),

            ft.Divider(),

            direccion,
            destinatario,
            repartidor,

            ft.ElevatedButton(
                "Crear paquete",
                on_click=crear_paquete
            ),

            mensaje,

            ft.Divider(),

            tabla

        ],

        expand=True,
        scroll=ft.ScrollMode.AUTO

    )