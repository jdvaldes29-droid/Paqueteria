import flet as ft
from app.supabase_client import supabase


def recepcion_asignacion_view(page: ft.Page):

    repartidores = supabase.table("repartidores") \
        .select("*") \
        .eq("activo", True) \
        .execute().data

    opciones = [

        ft.dropdown.Option(r["id"], r["nombre"])

        for r in repartidores

    ]

    repartidor = ft.Dropdown(
        label="Seleccionar repartidor",
        options=opciones
    )

    codigo = ft.TextField(
        label="Escanear código",
        autofocus=True
    )

    direccion = ft.TextField(
        label="Dirección (opcional)"
    )

    destinatario = ft.TextField(
        label="Destinatario (opcional)"
    )

    lista = ft.Column(scroll=ft.ScrollMode.AUTO, expand=True)

    def registrar(e):

        if not codigo.value or not repartidor.value:
            return

        try:

            res = supabase.table("paquetes") \
                .select("*") \
                .eq("codigo", codigo.value) \
                .execute()

            if res.data:

                paquete = res.data[0]

                supabase.table("paquetes") \
                    .update({

                        "repartidor_id": repartidor.value,
                        "estatus": "EN_RUTA"

                    }) \
                    .eq("id", paquete["id"]) \
                    .execute()

            else:

                supabase.table("paquetes").insert({

                    "codigo": codigo.value,
                    "direccion": direccion.value,
                    "nombre_destinatario": destinatario.value,
                    "repartidor_id": repartidor.value,
                    "estatus": "EN_RUTA"

                }).execute()

            lista.controls.insert(
                0,
                ft.Text(f"📦 {codigo.value}")
            )

            codigo.value = ""
            direccion.value = ""
            destinatario.value = ""

            codigo.focus()

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
                "Recepción y Asignación",
                size=26,
                weight="bold"
            ),

            repartidor,

            codigo,

            direccion,

            destinatario,

            ft.Divider(),

            lista

        ],

        expand=True

    )