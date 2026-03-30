import flet as ft
from datetime import datetime, timedelta
from app.supabase_client import supabase

# ---------------- CACHE ----------------
paquetes_cache = []


def cargar_paquetes_cache(repartidor_id):
    global paquetes_cache

    hace_3_dias = (datetime.now() - timedelta(days=3)).isoformat()

    res = (
        supabase.table("paquetes")
        .select("*")
        .eq("repartidor_id", repartidor_id)
        .gte("fecha_asignacion", hace_3_dias)
        .neq("estatus", "ENTREGADO")
        .execute()
    )

    paquetes_cache = res.data or []


# ---------------- BUSCAR ----------------
def buscar_paquete(codigo):
    for p in paquetes_cache:
        if p.get("codigo") == codigo:
            return p
    return None


# ---------------- SLA ----------------
def evaluar_estado(paquete):

    fecha_limite = paquete.get("fecha_limite")

    if not fecha_limite:
        return "OK"

    try:
        limite = datetime.fromisoformat(fecha_limite)
    except:
        return "OK"

    if datetime.now() > limite:
        return "VENCIDO"

    return "OK"


# ---------------- VISTA ----------------
def vista_scan(page: ft.Page, usuario: dict, volver):

    beep = ft.Audio(src="assets/beep.mp3", autoplay=False)
    page.overlay.append(beep)

    resultado = ft.Text(size=22, weight="bold")
    detalle = ft.Text(size=16)

    codigo_input = ft.TextField(
        label="Escanear código (manual o scanner)",
        autofocus=True,
        on_submit=lambda e: procesar_codigo(e.control.value),
    )

    # ---------------- PROCESO ----------------
    def procesar_codigo(codigo):

        codigo = (codigo or "").strip()

        if not codigo:
            return

        paquete = buscar_paquete(codigo)

        # ❌ NO EXISTE
        if not paquete:
            resultado.value = "❌ NO ENCONTRADO"
            detalle.value = codigo
            beep.play()
            page.update()
            limpiar_input()
            return

        estado = evaluar_estado(paquete)

        # 🔴 VENCIDO → DEVOLUCIÓN
        if estado == "VENCIDO":

            supabase.table("paquetes").update(
                {"estatus": "DEVUELTO_BODEGA"}
            ).eq("id", paquete["id"]).execute()

            resultado.value = "🔴 VENCIDO → DEVUELTO"
            detalle.value = paquete.get("direccion", "")

        else:

            # 🟢 ENTREGA AUTOMÁTICA
            supabase.table("entregas").insert(
                {
                    "paquete_id": paquete["id"],
                    "quien_recibe": "AUTO_SCAN",
                    "fecha_entrega": datetime.now().isoformat(),
                }
            ).execute()

            supabase.table("paquetes").update(
                {
                    "estatus": "ENTREGADO",
                    "fecha_entrega": datetime.now().isoformat(),
                }
            ).eq("id", paquete["id"]).execute()

            resultado.value = "✅ ENTREGADO"
            detalle.value = paquete.get("nombre_destinatario", "")
            beep.play()

        paquetes_cache.remove(paquete)

        page.update()
        limpiar_input()

    # ---------------- LIMPIAR ----------------
    def limpiar_input():
        codigo_input.value = ""
        page.update()
        codigo_input.focus()

    # ---------------- CAMARA ----------------
    
    def abrir_camara(e):

        page.launch_url(
            "https://scanqr.org/",
            web_window_name="_self"
        )
    # ---------------- VIEW ----------------
    view = ft.Column(
        [
            ft.Row(
                [
                    ft.IconButton(
                        icon=ft.Icons.ARROW_BACK,
                        on_click=lambda e: volver(),
                    ),
                    ft.Image(src="assets/logo.png", width=40),
                    ft.Text("Modo Escaneo", size=20, weight="bold"),
                ]
            ),
            codigo_input,
            ft.ElevatedButton(
                "📷 Escanear con cámara",
                on_click=abrir_camara,
            ),
            ft.Divider(),
            resultado,
            detalle,
        ],
        expand=True,
    )

    return view