import flet as ft

def mapa_view(lat=19.4326, lon=-99.1332):
    url = f"https://www.openstreetmap.org/?mlat={lat}&mlon={lon}#map=14/{lat}/{lon}"
    return ft.Container(
        content=ft.WebView(url=url),
        expand=True,
        border_radius=8,
    )

