import flet as ft
from app.login import login_view
from app.paquetes import paquetes_view
from app.scan_mode import vista_scan, cargar_paquetes_cache
from app.supabase_client import supabase

import threading
import random
from datetime import datetime




# -------------------------------------------------
# GPS (NO BLOQUEANTE - PRO)
# -------------------------------------------------

def obtener_ubicacion():
    lat = 19.4326 + random.uniform(-0.01, 0.01)
    lon = -99.1332 + random.uniform(-0.01, 0.01)
    return lat, lon


def iniciar_envio_gps(usuario):

    repartidor_id = usuario["repartidor_id"]

    def loop():
        while True:
            try:
                lat, lon = obtener_ubicacion()

                supabase.table("ubicaciones").insert({
                    "repartidor_id": repartidor_id,
                    "latitud": lat,
                    "longitud": lon,
                    "timestamp": datetime.now().isoformat()
                }).execute()

                print(f"GPS enviado: {lat}, {lon}")

            except Exception as e:
                print("Error enviando GPS:", e)

            import time
            time.sleep(60)

    threading.Thread(target=loop, daemon=True).start()

# -------------------------------------------------
# APP PRINCIPAL
# -------------------------------------------------

def main(page: ft.Page):

    
    # ---------------- UI BASE ----------------

    page.title = "Paquetería Express"
    page.add (ft.Text("Panel Repartidor"))
    page.assets_dir = "assets"
    page.window_width = 420
    page.window_height = 720

    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.vertical_alignment = ft.MainAxisAlignment.START

    page.theme = ft.Theme(
        color_scheme=ft.ColorScheme(
            primary=ft.Colors.BLUE_700  # ✅ corregido
        )
    )

    # ---------------- FILE PICKER ----------------

    file_picker = ft.FilePicker()
    page.overlay.append(file_picker)
    page.file_picker = file_picker

    # ---------------- ESTADO GLOBAL ----------------

    usuario_actual = None

    # -------------------------------------------------
    # NAVEGACIÓN (ESTABLE)
    # -------------------------------------------------

    def ir_menu():

        page.clean()

        page.add(
            ft.Column(
                [
                    ft.Image(
                        src="assets/logo.png",
                        width=120,
                        fit=ft.ImageFit.CONTAIN
                    ),

                    ft.Text(
                        "Panel Repartidor",
                        size=22,
                        weight="bold"
                    ),

                    ft.ElevatedButton(
                        "📷 Modo Escaneo",
                        on_click=lambda e: ir_scan(),
                        width=250
                    ),

                    ft.ElevatedButton(
                        "📦 Ver Paquetes",
                        on_click=lambda e: ir_paquetes(),
                        width=250
                    ),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER
            )
        )

    def ir_paquetes():

        if not usuario_actual:
            print("Usuario no cargado")
            return

        page.clean()
        page.add(paquetes_view(page, usuario_actual, ir_menu))

    def ir_scan():

        if not usuario_actual:
            print("Usuario no cargado")
            return

        page.clean()
        page.add(vista_scan(page, usuario_actual, ir_menu))

    # -------------------------------------------------
    # LOGIN EXITOSO
    # -------------------------------------------------

    def on_login_success(usuario):

        nonlocal usuario_actual
        usuario_actual = usuario

        print("Usuario autenticado:", usuario)

        # 🔥 cache
        cargar_paquetes_cache(usuario["repartidor_id"])

        # 🔥 GPS (no bloqueante)
        iniciar_envio_gps(usuario)

        # 🔥 ir a menú
        ir_menu()



    def ir_paquetes():
        page.clean()
        page.add(paquetes_view(page, usuario_actual, ir_menu))

    # -------------------------------------------------
    # INICIO APP
    # -------------------------------------------------

    page.add(
        login_view(page, on_login_success)
    )


# -------------------------------------------------
# EJECUCIÓN
# -------------------------------------------------

ft.app(target=main)