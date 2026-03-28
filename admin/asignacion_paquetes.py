import flet as ft
from app.supabase_client import supabase


def asignacion_view(page: ft.Page):

    repartidores = supabase.table("repartidores") \
        .select("*") \
        .eq("activo", True) \
        .execute().data

    opciones = [

        ft.dropdown.Option(
            r["id"],
            r["nombre"]
        )

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

    lista = ft.Column(
        scroll=ft.ScrollMode.AUTO,
        expand=True
    )

    # ----------------------------------------
    # ASIGNAR PAQUETE
    # ----------------------------------------

    def asignar(e):

        if not codigo.value or not repartidor.value:
            return

        try:

            res = supabase.table("paquetes") \
                .select("*") \
                .eq("codigo", codigo.value) \
                .execute()

            if not res.data:

                page.snack_bar = ft.SnackBar(
                    ft.Text("Paquete no encontrado")
                )

                page.snack_bar.open = True
                page.update()

                codigo.value = ""
                return

            paquete = res.data[0]

            supabase.table("paquetes") \
                .update({

                    "repartidor_id": repartidor.value,
                    "estatus": "ASIGNADO"

                }) \
                .eq("id", paquete["id"]) \
                .execute()

            lista.controls.insert(

                0,

                ft.Text(
                    f"📦 {codigo.value}"
                )

            )

            codigo.value = ""

            page.update()

        except Exception as ex:

            page.snack_bar = ft.SnackBar(
                ft.Text(str(ex))
            )

            page.snack_bar.open = True
            page.update()

    codigo.on_submit = asignar

    return ft.Column(

        [

            ft.Text(
                "Asignación de Paquetes",
                size=24,
                weight="bold"
            ),

            repartidor,

            codigo,

            ft.Divider(),

            lista

        ],

        expand=True

    )