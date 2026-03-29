import flet as ft

# ------------------------------
# IMPORTAR MODULOS
# ------------------------------

from admin.dashboard_logistico import dashboard_view
from admin.recepcion_asignacion import recepcion_asignacion_view
from admin.lista_repartidores import lista_repartidores_view
from admin.paquetes import paquetes_view
from admin.monitor_logistico import monitor_view
from admin.estadisticas import estadisticas_view
from admin.reporte_logistico import reporte_view

# ------------------------------
# APP PRINCIPAL
# ------------------------------

def main(page: ft.Page):

    page.title = "Sistema Logístico"
    page.window_width = 1400
    page.window_height = 900

    page.theme_mode = ft.ThemeMode.LIGHT

    page.theme = ft.Theme(
        color_scheme_seed=ft.Colors.BLUE
    )

    # --------------------------------
    # CONTENEDOR CENTRAL
    # --------------------------------

    contenido = ft.Container(
        expand=True,
        padding=20
    )

    # --------------------------------
    # CAMBIAR VISTA
    # --------------------------------

    def cambiar_vista(e):

        index = rail.selected_index

        if index == 0:
            contenido.content = dashboard_view(page)

        elif index == 1:
            contenido.content = recepcion_asignacion_view(page)

        elif index == 2:
            contenido.content = lista_repartidores_view(page)

        elif index == 3:
            contenido.content = paquetes_view(page)

        elif index == 4:
            contenido.content = monitor_view(page)

        elif index == 5:
            contenido.content = estadisticas_view(page)
        
        elif index == 6:
            contenido.content = reporte_view(page)

        page.update()

    # --------------------------------
    # MENU LATERAL
    # --------------------------------

    rail = ft.NavigationRail(

        selected_index=0,

        label_type=ft.NavigationRailLabelType.ALL,

        min_width=100,

        min_extended_width=200,

        group_alignment=-0.9,

        destinations=[

            ft.NavigationRailDestination(
                icon=ft.Icons.DASHBOARD,
                label="Dashboard"
            ),

            ft.NavigationRailDestination(
                icon=ft.Icons.INVENTORY,
                label="Recepción y Asignación"
            ),

           
            ft.NavigationRailDestination(
                icon=ft.Icons.PEOPLE,
                label="Repartidores"
            ),

            ft.NavigationRailDestination(
                icon=ft.Icons.LOCAL_SHIPPING,
                label="Paquetes"
            ),

            ft.NavigationRailDestination(
                icon=ft.Icons.MAP,
                label="Monitor"
            ),

            ft.NavigationRailDestination(
                icon=ft.Icons.ANALYTICS,
                label="Estadísticas"
            ),

        ],

        on_change=cambiar_vista,

    )

    # --------------------------------
    # HEADER
    # --------------------------------

    header = ft.Container(

        content=ft.Row(

            [

                ft.Text(
                    "Centro de Control Logístico",
                    size=26,
                    weight="bold"
                ),

                ft.Container(expand=True),

                ft.Icon(ft.Icons.ACCOUNT_CIRCLE, size=32),

                ft.Text("Administrador")

            ]

        ),

        padding=10

    )

    # --------------------------------
    # CARGAR DASHBOARD INICIAL
    # --------------------------------

    contenido.content = dashboard_view(page)

    # --------------------------------
    # LAYOUT PRINCIPAL
    # --------------------------------

    page.add(

        ft.Column(

            [

                header,

                ft.Row(

                    [

                        rail,

                        ft.VerticalDivider(width=1),

                        contenido

                    ],

                    expand=True

                )

            ],

            expand=True

        )

    )


# --------------------------------
# EJECUTAR APP
# --------------------------------

#if __name__ == "__main__":
    ft.app(target=main)