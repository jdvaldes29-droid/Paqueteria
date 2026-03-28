import flet as ft
import flet.map as map
from app.supabase_client import supabase


def mapa_view():

    # obtener última ubicación de cada repartidor
    res = supabase.rpc("ultima_ubicacion_repartidores").execute()

    markers = []

    for r in res.data:

        markers.append(
            map.Marker(
                content=ft.Icon(ft.Icons.LOCATION_ON, color="red"),
                coordinates=map.MapLatitudeLongitude(
                    r["latitud"],
                    r["longitud"]
                ),
                tooltip=r["nombre"]
            )
        )

    return map.Map(
        expand=True,
        initial_center=map.MapLatitudeLongitude(19.4326, -99.1332),
        initial_zoom=12,
        layers=[
            map.TileLayer(
                url_template="https://tile.openstreetmap.org/{z}/{x}/{y}.png"
            ),
            map.MarkerLayer(markers)
        ]
    )