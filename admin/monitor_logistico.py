import flet as ft
from app.supabase_client import supabase
import os
import webbrowser
from collections import defaultdict


def monitor_view(page: ft.Page):

    estado = ft.Text()
    html_path = os.path.join(os.getcwd(), "monitor_logistico.html")

    def generar_mapa():

        # ---------------------------
        # UBICACIONES (ruta GPS)
        # ---------------------------
        ubicaciones = supabase.table("ubicaciones") \
            .select("*") \
            .order("timestamp") \
            .execute().data

        if not ubicaciones:
            estado.value = "No hay datos GPS"
            page.update()
            return

        # ---------------------------
        # ENTREGAS
        # ---------------------------
        entregas = supabase.table("entregas") \
            .select("*") \
            .execute().data

        # ---------------------------
        # INCIDENCIAS
        # ---------------------------
        incidencias = supabase.table("paquetes") \
            .select("*") \
            .eq("estatus", "NO_ENTREGADO") \
            .execute().data

        # ---------------------------
        # REPARTIDORES
        # ---------------------------
        repartidores = supabase.table("repartidores") \
            .select("*") \
            .execute().data

        nombres = {r["id"]: r["nombre"] for r in repartidores}

        # Agrupar puntos por repartidor para dibujar rutas
        rutas = defaultdict(list)

        for u in ubicaciones:
            rutas[u["repartidor_id"]].append((u["latitud"], u["longitud"]))

        js_rutas = []
        js_markers = []

        # ---------------------------
        # RUTAS POR REPARTIDOR
        # ---------------------------
        for rid, puntos in rutas.items():

            nombre = nombres.get(rid, "Repartidor")

            # ruta
            puntos_js = ",".join([f"[{p[0]},{p[1]}]" for p in puntos])

            js_rutas.append(f"""
            var ruta_{rid.replace('-','')} = L.polyline([{puntos_js}], {{
                color: 'blue',
                weight: 4
            }}).addTo(map);
            """)

            # última ubicación
            lat, lon = puntos[-1]

            js_markers.append(f"""
            L.circleMarker([{lat},{lon}], {{
                radius:10,
                color:'blue',
                fillColor:'blue',
                fillOpacity:0.8
            }}).addTo(map)
            .bindPopup("{nombre} - ubicación actual");
            """)

        # ---------------------------
        # ENTREGAS
        # ---------------------------
        for e in entregas:

            lat = e.get("latitud")
            lon = e.get("longitud")

            if lat and lon:

                js_markers.append(f"""
                L.circleMarker([{lat},{lon}], {{
                    radius:8,
                    color:'green',
                    fillColor:'green',
                    fillOpacity:0.8
                }}).addTo(map)
                .bindPopup("Entrega realizada");
                """)

        # ---------------------------
        # INCIDENCIAS
        # ---------------------------
        for i in incidencias:

            lat = i.get("latitud")
            lon = i.get("longitud")

            if lat and lon:

                js_markers.append(f"""
                L.circleMarker([{lat},{lon}], {{
                    radius:8,
                    color:'red',
                    fillColor:'red',
                    fillOpacity:0.8
                }}).addTo(map)
                .bindPopup("Incidencia");
                """)

        rutas_js = "\n".join(js_rutas)
        markers_js = "\n".join(js_markers)

        lat0 = ubicaciones[-1]["latitud"]
        lon0 = ubicaciones[-1]["longitud"]

        html = f"""
<!DOCTYPE html>
<html>

<head>
<meta charset="utf-8">

<link rel="stylesheet"
href="https://cdn.jsdelivr.net/npm/leaflet@1.9.4/dist/leaflet.css"/>

<script src="https://cdn.jsdelivr.net/npm/leaflet@1.9.4/dist/leaflet.js"></script>

<style>
#map {{
height:100vh;
}}
</style>

</head>

<body>

<div id="map"></div>

<script>

var map = L.map('map').setView([{lat0},{lon0}], 13);

L.tileLayer(
'https://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png',
{{maxZoom:19}}
).addTo(map);

{rutas_js}

{markers_js}

// auto refresh cada 15 segundos
setTimeout(function(){{
location.reload();
}},15000);

</script>

</body>

</html>
"""

        with open(html_path, "w", encoding="utf8") as f:
            f.write(html)

    def abrir_monitor(e):

        estado.value = "Generando monitor logístico..."
        page.update()

        generar_mapa()

        webbrowser.open(f"file:///{html_path}")

        estado.value = "Monitor abierto (auto actualización activa)"
        page.update()

    return ft.Column(

        [

            ft.Text(
                "Centro de Monitoreo Logístico",
                size=26,
                weight="bold"
            ),

            ft.ElevatedButton(
                "Abrir monitor logístico",
                on_click=abrir_monitor
            ),

            estado

        ],

        expand=True

    )