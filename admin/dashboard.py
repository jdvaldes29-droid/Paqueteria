import flet as ft
import threading
import time
from app.supabase_client import supabase


def dashboard_view(page: ft.Page):

    contenido = ft.Column(
        expand=True,
        scroll=ft.ScrollMode.AUTO
    )

    def construir_dashboard():

        stats = obtener_estadisticas()

        sla = calcular_sla()  # 🔥 NUEVO

        cumplimiento = calcular_cumplimiento(stats)

        eficiencia = eficiencia_repartidores()

        contenido.controls = [

            ft.Text(
                "Centro de Control Logístico",
                size=32,
                weight="bold"
            ),

            ft.Divider(),

            fila_tarjetas(stats),

            ft.Divider(),

            fila_sla(sla),  # 🔥 NUEVO

            ft.Divider(),

            ft.Text(
                f"Cumplimiento del día: {cumplimiento} %",
                size=18,
                weight="bold"
            ),

            ft.Divider(),

            ft.Text(
                "Eficiencia de Repartidores",
                size=22,
                weight="bold"
            ),

            tabla_eficiencia(eficiencia),

            ft.Divider(),

            repartidores_activos(),

            ft.Divider(),

            eventos_recientes()

        ]

        page.update()

    construir_dashboard()

    def auto_refresh():

        while True:

            try:
                construir_dashboard()
            except Exception as e:
                print("Error refrescando dashboard:", e)

            time.sleep(5)

    threading.Thread(
        target=auto_refresh,
        daemon=True
    ).start()

    return contenido


# ---------------------------
# TARJETAS PRINCIPALES
# ---------------------------

def fila_tarjetas(stats):

    return ft.Row(

        [

            tarjeta("Asignados", stats["asignados"], "📦"),

            tarjeta("Entregados", stats["entregados"], "✅"),

            tarjeta("Incidencias", stats["no_entregados"], "⚠"),

            tarjeta("Devueltos", stats["devueltos"], "↩")

        ],

        wrap=True,
        spacing=20

    )


def tarjeta(titulo, valor, icono):

    return ft.Container(

        content=ft.Column(

            [

                ft.Text(icono, size=30),

                ft.Text(titulo, weight="bold"),

                ft.Text(str(valor), size=28)

            ],

            horizontal_alignment="center"

        ),

        padding=20,
        border_radius=12,
        bgcolor="#f0f4f8",
        width=180

    )


# ---------------------------
# ESTADISTICAS GENERALES
# ---------------------------

def obtener_estadisticas():

    response = supabase.table("paquetes") \
        .select("estatus") \
        .execute()

    paquetes = response.data

    stats = {

        "asignados": 0,
        "entregados": 0,
        "no_entregados": 0,
        "devueltos": 0

    }

    for p in paquetes:

        estatus = p["estatus"]

        if estatus == "ASIGNADO":
            stats["asignados"] += 1

        elif estatus == "ENTREGADO":
            stats["entregados"] += 1

        elif estatus == "NO_ENTREGADO":
            stats["no_entregados"] += 1

        elif estatus == "DEVUELTO_BODEGA":
            stats["devueltos"] += 1

    return stats


def calcular_cumplimiento(stats):

    total = stats["entregados"] + stats["no_entregados"]

    if total == 0:
        return 0

    porcentaje = (stats["entregados"] / total) * 100

    return round(porcentaje, 2)


# ---------------------------
# EFICIENCIA REPARTIDORES
# ---------------------------

def eficiencia_repartidores():

    response = supabase.table("paquetes") \
        .select("repartidor_id, estatus") \
        .execute()

    paquetes = response.data

    data = {}

    for p in paquetes:

        rid = p["repartidor_id"]

        if rid not in data:

            data[rid] = {
                "entregados": 0,
                "fallidos": 0
            }

        if p["estatus"] == "ENTREGADO":
            data[rid]["entregados"] += 1

        elif p["estatus"] == "NO_ENTREGADO":
            data[rid]["fallidos"] += 1

    return data


def tabla_eficiencia(data):

    rows = []

    for rid, stats in data.items():

        total = stats["entregados"] + stats["fallidos"]

        eficiencia = 0

        if total > 0:
            eficiencia = round((stats["entregados"] / total) * 100, 2)

        rows.append(

            ft.DataRow(

                cells=[

                    ft.DataCell(ft.Text(str(rid))),

                    ft.DataCell(ft.Text(str(stats["entregados"]))),

                    ft.DataCell(ft.Text(str(stats["fallidos"]))),

                    ft.DataCell(ft.Text(f"{eficiencia}%"))

                ]

            )

        )

    return ft.DataTable(

        columns=[

            ft.DataColumn(ft.Text("Repartidor")),

            ft.DataColumn(ft.Text("Entregados")),

            ft.DataColumn(ft.Text("Fallidos")),

            ft.DataColumn(ft.Text("Eficiencia"))

        ],

        rows=rows

    )


# ---------------------------
# REPARTIDORES ACTIVOS
# ---------------------------

def repartidores_activos():

    from datetime import datetime, timezone

    response = supabase.table("ubicaciones") \
        .select("*") \
        .order("timestamp", desc=True) \
        .execute()

    ubicaciones = response.data

    rows = []

    vistos = set()

    ahora = datetime.now(timezone.utc)

    for u in ubicaciones:

        rid = u["repartidor_id"]

        if rid in vistos:
            continue

        vistos.add(rid)

        ts = u["timestamp"]

        try:
            ultima = datetime.fromisoformat(ts.replace("Z", "+00:00"))
            minutos = (ahora - ultima).total_seconds() / 60
        except:
            minutos = 999

        # determinar estado

        if minutos <= 2:
            estado = "ACTIVO"
            color = "green"

        elif minutos <= 10:
            estado = "INACTIVO"
            color = "orange"

        else:
            estado = "DESCONECTADO"
            color = "red"

        rows.append(

            ft.DataRow(

                cells=[

                    ft.DataCell(ft.Text(str(rid))),

                    ft.DataCell(ft.Text(str(u["latitud"]))),

                    ft.DataCell(ft.Text(str(u["longitud"]))),

                    ft.DataCell(ft.Text(str(u["timestamp"]))),

                    ft.DataCell(

                        ft.Container(

                            content=ft.Text(
                                estado,
                                color="white"
                            ),

                            bgcolor=color,
                            padding=5,
                            border_radius=6

                        )

                    )

                ]

            )

        )

    return ft.Column(

        [

            ft.Text(
                "Estado de Repartidores",
                size=20,
                weight="bold"
            ),

            ft.DataTable(

                columns=[

                    ft.DataColumn(ft.Text("Repartidor")),

                    ft.DataColumn(ft.Text("Latitud")),

                    ft.DataColumn(ft.Text("Longitud")),

                    ft.DataColumn(ft.Text("Última actualización")),

                    ft.DataColumn(ft.Text("Estado"))

                ],

                rows=rows

            )

        ]

    )

# ---------------------------
# EVENTOS RECIENTES
# ---------------------------

def eventos_recientes():

    response = supabase.table("paquetes") \
        .select("direccion, nombre_destinatario, estatus, motivo_no_entrega") \
        .order("fecha_asignacion", desc=True) \
        .limit(10) \
        .execute()

    paquetes = response.data

    rows = []

    for p in paquetes:

        motivo = p.get("motivo_no_entrega") or ""

        rows.append(

            ft.DataRow(

                cells=[

                    ft.DataCell(ft.Text(str(p["direccion"]))),

                    ft.DataCell(ft.Text(str(p["nombre_destinatario"]))),

                    ft.DataCell(ft.Text(str(p["estatus"]))),

                    ft.DataCell(ft.Text(str(motivo)))

                ]

            )

        )

    return ft.Column(

        [

            ft.Text(
                "Actividad reciente de paquetes",
                size=20,
                weight="bold"
            ),

            ft.DataTable(

                columns=[

                    ft.DataColumn(ft.Text("Dirección")),

                    ft.DataColumn(ft.Text("Destinatario")),

                    ft.DataColumn(ft.Text("Estatus")),

                    ft.DataColumn(ft.Text("Motivo"))

                ],

                rows=rows

            )

        ]

    )

def calcular_sla():

    from datetime import datetime

    response = supabase.table("paquetes") \
        .select("estatus, fecha_limite, fecha_entrega") \
        .execute()

    paquetes = response.data

    ahora = datetime.now()

    entregados_tiempo = 0
    entregados_tarde = 0
    vencidos = 0

    for p in paquetes:

        estatus = p.get("estatus")
        fl = p.get("fecha_limite")
        fe = p.get("fecha_entrega")

        if fl:
            fl = datetime.fromisoformat(fl)

        if fe:
            fe = datetime.fromisoformat(fe)

        # ENTREGADOS
        if estatus == "ENTREGADO" and fe and fl:

            if fe <= fl:
                entregados_tiempo += 1
            else:
                entregados_tarde += 1

        # VENCIDOS
        if fl and ahora > fl and estatus != "ENTREGADO":
            vencidos += 1

    total = len(paquetes)

    sla = (entregados_tiempo / total * 100) if total > 0 else 0

    return {
        "sla": round(sla, 2),
        "tiempo": entregados_tiempo,
        "tarde": entregados_tarde,
        "vencidos": vencidos
    }

def fila_sla(sla):

    return ft.Row(

        [

            tarjeta("SLA", f"{sla['sla']}%", "🎯"),

            tarjeta("A tiempo", sla["tiempo"], "✅"),

            tarjeta("Tarde", sla["tarde"], "⏱"),

            tarjeta("Vencidos", sla["vencidos"], "🔴"),

        ],

        wrap=True,
        spacing=20

    )