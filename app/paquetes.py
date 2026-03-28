import flet as ft
from app.supabase_client import supabase
from datetime import datetime

ft.ElevatedButton(
    "TEST CLICK",
    on_click=lambda e: print("🔥 CLICK TEST OK")
)   
def paquetes_view(page: ft.Page, usuario: dict, volver):

    repartidor_id = usuario.get("repartidor_id")
    nombre = usuario.get("nombre", "Repartidor")

    # ---------------- UI ----------------
    info = ft.Text("Cargando paquetes...")
    buscador = ft.TextField(label="Buscar o escanear código")
    lista = ft.Column(expand=True, scroll=ft.ScrollMode.AUTO)

    paquetes = []

    # ---------------- UTIL ----------------
    def show_error(msg):
        page.snack_bar = ft.SnackBar(ft.Text(msg))
        page.snack_bar.open = True
        page.update()

    # ---------------- CONTADOR ----------------
    def actualizar_contador():
        total = len(paquetes)
        entregados = len([p for p in paquetes if p.get("estatus") == "ENTREGADO"])
        pendientes = total - entregados

        info.value = f"Total: {total} | Pendientes: {pendientes} | Entregados: {entregados}"

    # ---------------- RENDER ----------------
    def render(data):
        lista.controls.clear()

        if not data:
            lista.controls.append(ft.Text("Sin paquetes"))

        for p in data:
            lista.controls.append(tarjeta_paquete(p))

        page.update()

    # ---------------- CARGA ----------------
    from datetime import datetime, timedelta

    def cargar_paquetes():
        nonlocal paquetes

        try:
            limite = datetime.now() - timedelta(days=3)

            res = supabase.table("paquetes") \
                .select("*") \
                .eq("repartidor_id", repartidor_id) \
                .order("fecha_asignacion", desc=True) \
                .execute()

            paquetes = []

            for p in (res.data or []):

                # ignorar paquetes ya cerrados
                if p.get("estatus") in ["ENTREGADO", "DEVUELTO_BODEGA"]:
                    continue

                fecha = p.get("fecha_asignacion")

                if fecha:
                    try:
                        fecha = datetime.fromisoformat(fecha)
                    except:
                        fecha = None

                # solo últimos 3 días
                if fecha and fecha >= limite:
                    paquetes.append(p)

        except Exception as ex:
            paquetes = []
            show_error(str(ex))

        actualizar_contador()
        render(paquetes)
   

    
    # ---------------- BUSCAR ----------------
    def buscar(e):
        texto = (buscador.value or "").lower()

        filtrados = [
            p for p in paquetes
            if texto in (p.get("direccion") or "").lower()
            or texto in (p.get("nombre_destinatario") or "").lower()
            or texto in (p.get("codigo") or "").lower()
        ]

        render(filtrados)

    buscador.on_change = buscar

    # ---------------- ESCANEO ----------------
    def escanear(e):
        codigo = (buscador.value or "").strip()

        encontrados = [p for p in paquetes if p.get("codigo") == codigo]

        if encontrados:
            render(encontrados)

        buscador.value = ""
        page.update()

    buscador.on_submit = escanear

    # ---------------- MODALES ----------------
    def cerrar_dialogo(dialog):
        dialog.open = False
        page.update()

    # ---------------- ENTREGADO ----------------
    def marcar_entregado(paquete_id):

        quien = ft.TextField(label="Nombre quien recibe")

        def guardar(e):
            try:
                supabase.table("entregas").insert({
                    "paquete_id": paquete_id,
                    "quien_recibe": quien.value,
                    "fecha_entrega": datetime.now().isoformat()
                }).execute()

                supabase.table("paquetes") \
                    .update({
                        "estatus": "ENTREGADO",
                        "fecha_entrega": datetime.now().isoformat()
                    }) \
                    .eq("id", paquete_id) \
                    .execute()

                dialog.open = False
                page.update()

                cargar_paquetes()

            except Exception as ex:
                show_error(str(ex))

        dialog = ft.AlertDialog(
            title=ft.Text("Registrar entrega"),
            content=quien,
            actions=[
                ft.TextButton("Cancelar", on_click=lambda e: cerrar_dialogo(dialog)),
                ft.ElevatedButton("Guardar", on_click=guardar)
            ]
        )

        page.open(dialog)

    # ---------------- NO ENTREGADO ----------------
    def marcar_no_entregado(paquete_id):

        motivo = ft.TextField(label="Motivo de no entrega")

        def guardar(e):
            try:
                supabase.table("paquetes") \
                    .update({
                        "estatus": "NO_ENTREGADO",
                        "comentario_no_entrega": motivo.value
                    }) \
                    .eq("id", paquete_id) \
                    .execute()

                dialog.open = False
                page.update()

                cargar_paquetes()

            except Exception as ex:
                show_error(str(ex))

        dialog = ft.AlertDialog(
            title=ft.Text("Registrar incidencia"),
            content=motivo,
            actions=[
                ft.TextButton("Cancelar", on_click=lambda e: cerrar_dialogo(dialog)),
                ft.ElevatedButton("Guardar", on_click=guardar)
            ]
        )

        page.open(dialog)

    # ---------------- TARJETA ----------------
    def tarjeta_paquete(p):

        paquete_id = p.get("id")

        return ft.Card(
            content=ft.Container(
                padding=10,
                content=ft.Column(
                    [
                        ft.Text(f"📦 {p.get('codigo')}", weight="bold"),
                        ft.Text(p.get("direccion")),
                        ft.Text(p.get("nombre_destinatario")),

                        ft.Row(
                            [
                                ft.ElevatedButton(
                                    "ENTREGADO",
                                    bgcolor=ft.colors.GREEN,
                                    color="white",
                                    on_click=lambda e, pid=paquete_id: marcar_entregado(pid)
                                ),
                                ft.ElevatedButton(
                                    "NO ENTREGADO",
                                    bgcolor=ft.colors.RED,
                                    color="white",
                                    on_click=lambda e, pid=paquete_id: marcar_no_entregado(pid)
                                ),
                            ]
                        )
                    ]
                )
            )
        )


    # ---------------- VIEW ----------------
    view = ft.Column(
        [
            # 🔥 HEADER CON BOTÓN ATRÁS
            ft.Row(
                [
                    ft.IconButton(
                        icon=ft.Icons.ARROW_BACK,
                        on_click=lambda e: volver()
                    ),
                    ft.Image(src="assets/logo.png", width=40),
                    ft.Text("Paquetes", size=20, weight="bold")
                ]
            ),

            ft.Text(f"Repartidor: {nombre}"),
            info,
            buscador,
            lista
        ],
        expand=True
    )

    # 🔥 carga inicial NORMAL (sin hacks)
    cargar_paquetes()

    return view