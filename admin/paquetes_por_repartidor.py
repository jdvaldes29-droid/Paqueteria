import flet as ft
from app.supabase_client import supabase


def paquetes_por_repartidor_view(page: ft.Page):

    titulo = ft.Text(
        "Paquetes por Repartidor",
        size=26,
        weight="bold"
    )

    lista = ft.Column(
        expand=True,
        scroll=ft.ScrollMode.AUTO
    )

    page.add(
        titulo,
        ft.Divider(),
        lista
    )

    cargar_repartidores(lista, page)


def cargar_repartidores(lista, page):

    lista.controls.clear()

    response = supabase.table("repartidores") \
        .select("*") \
        .execute()

    repartidores = response.data

    for r in repartidores:

        bloque = bloque_repartidor(r, page)

        lista.controls.append(bloque)

    lista.update()


def bloque_repartidor(repartidor, page):

    nombre = repartidor["nombre"]
    repartidor_id = repartidor["id"]

    titulo = ft.Text(
        f"Repartidor: {nombre}",
        size=20,
        weight="bold"
    )

    tabla = tabla_paquetes(repartidor_id, page)

    card = ft.Card(

        content=ft.Container(

            content=ft.Column(

                [
                    titulo,
                    tabla
                ]

            ),

            padding=15

        )

    )

    return card


def tabla_paquetes(repartidor_id, page):

    response = supabase.table("paquetes") \
        .select("*") \
        .eq("repartidor_id", repartidor_id) \
        .execute()

    paquetes = response.data

    rows = []

    for p in paquetes:

        estatus = p["estatus"]

        motivo = p.get("motivo_no_entrega") or ""

        comentario = p.get("comentario_no_entrega") or ""

        info_motivo = ""

        if estatus == "NO_ENTREGADO":

            info_motivo = f"{motivo} {comentario}"

        boton = ft.Text("")

        if estatus == "NO_ENTREGADO":

            boton = ft.ElevatedButton(

                "DEVUELTO A BODEGA",

                on_click=lambda e, pid=p["id"]: marcar_devuelto(pid, page)

            )

        row = ft.DataRow(

            cells=[

                ft.DataCell(ft.Text(p["direccion"])),

                ft.DataCell(ft.Text(p["nombre_destinatario"])),

                ft.DataCell(ft.Text(estatus)),

                ft.DataCell(ft.Text(info_motivo)),

                ft.DataCell(boton)

            ]

        )

        rows.append(row)

    tabla = ft.DataTable(

        columns=[

            ft.DataColumn(ft.Text("Dirección")),

            ft.DataColumn(ft.Text("Destinatario")),

            ft.DataColumn(ft.Text("Estatus")),

            ft.DataColumn(ft.Text("Motivo")),

            ft.DataColumn(ft.Text("Acción"))

        ],

        rows=rows

    )

    return tabla


def marcar_devuelto(paquete_id, page):

    supabase.table("paquetes") \
        .update({
            "estatus": "DEVUELTO_BODEGA"
        }) \
        .eq("id", paquete_id) \
        .execute()

    page.snack_bar = ft.SnackBar(
        ft.Text("Paquete marcado como DEVUELTO A BODEGA")
    )

    page.snack_bar.open = True
    page.update()