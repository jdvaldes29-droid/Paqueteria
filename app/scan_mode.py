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

    resultado = ft.Text(size=22, weight="bold")
    detalle = ft.Text(size=16)

    codigo_input = ft.TextField(
        label="Código escaneado",
        autofocus=True,
    )

    # ---------------- PROCESAR ----------------
    def procesar_codigo(codigo):

        codigo = (codigo or "").strip()

        if not codigo:
            return

        paquete = buscar_paquete(codigo)

        if not paquete:
            resultado.value = "❌ NO ENCONTRADO"
            detalle.value = codigo
            page.update()
            return

        estado = evaluar_estado(paquete)

        if estado == "VENCIDO":

            supabase.table("paquetes").update(
                {"estatus": "DEVUELTO_BODEGA"}
            ).eq("id", paquete["id"]).execute()

            resultado.value = "🔴 VENCIDO → DEVUELTO"
            detalle.value = paquete.get("direccion", "")

        else:

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

        paquetes_cache.remove(paquete)

        page.update()

    # ---------------- SCANNER ----------------
    def abrir_scanner(e):

        scanner = ft.BarcodeScanner(
            formats=[
                ft.BarcodeFormat.QR_CODE,
                ft.BarcodeFormat.CODE_128,
                ft.BarcodeFormat.EAN_13,
                ft.BarcodeFormat.CODE_39,
            ],
            on_scan=lambda e: on_codigo_detectado(e),
        )

        page.overlay.append(scanner)
        scanner.start()

    def on_codigo_detectado(e):

        codigo = e.data

        codigo_input.value = codigo
        page.update()

        procesar_codigo(codigo)

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
                "📷 Escanear paquete",
                on_click=abrir_scanner,
            ),

            ft.Divider(),

            resultado,
            detalle,
        ],
        expand=True,
    )

    return view