import flet as ft
from app.supabase_client import supabase
import webbrowser
import tempfile


def ruta_repartidor_view(page: ft.Page):

    # cargar repartidores
    rep_query = supabase.table("repartidores") \
        .select("id,nombre") \
        .execute()

    repartidores = rep_query.data

    opciones = [
        ft.dropdown.Option(r["id"], r["nombre"])
        for r in repartidores
    ]

    repartidor = ft.Dropdown(
        label="Seleccionar repartidor",
        options=opciones,
        width=300
    )

    mensaje = ft.Text()

    def ver_ruta(e):

        rid = repartidor.value

        if not rid:
            mensaje.value = "Seleccione un repartidor"
            page.update()
            return

        query = supabase.table("ubicaciones") \
            .select("*") \
            .eq("repartidor_id", rid) \
            .order("timestamp") \
            .execute()

        ubicaciones = query.data

        if not ubicaciones:
            mensaje.value = "No hay datos de GPS"
            page.update()
            return

        coords = [
            [u["latitud"], u["longitud"]]
            for u in ubicaciones
        ]

        # centro del mapa
        lat = coords[0][0]
        lon = coords[0][1]

        polyline = str(coords)

        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
        <meta charset="utf-8"/>
        <title>Ruta del Repartidor</title>

        <link rel="stylesheet"
        href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"/>

        <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>

        <style>
        #map {{ height: 100vh; }}
        </style>

        </head>

        <body>

        <div id="map"></div>

        <script>

        var map = L.map('map').setView([{lat}, {lon}], 13);

        L.tileLayer(
        'https://tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png',
        {{
            maxZoom: 19
        }}
        ).addTo(map);

        var coords = {polyline};

        var polyline = L.polyline(coords, {{
            color: 'blue'
        }}).addTo(map);

        map.fitBounds(polyline.getBounds());

        </script>

        </body>
        </html>
        """

        f = tempfile.NamedTemporaryFile(delete=False, suffix=".html")

        f.write(html.encode())
        f.close()

        webbrowser.open(f.name)

    return ft.Column(

        [

            ft.Text(
                "Ruta del Repartidor",
                size=28,
                weight="bold"
            ),

            repartidor,

            ft.ElevatedButton(
                "Ver ruta en mapa",
                on_click=ver_ruta
            ),

            mensaje

        ],

        width=400

    )