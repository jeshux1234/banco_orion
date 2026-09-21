from datetime import datetime


def registrar_movimiento(banco, numero_cuenta, tipo, monto, detalle=""):
    movimiento = {
        "fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "cuenta": str(numero_cuenta),
        "tipo": tipo,
        "monto": float(monto),
        "detalle": detalle,
    }
    banco.movimientos.append(movimiento)
    return movimiento


def consultar_historial(banco, numero_cuenta):
    numero_cuenta = str(numero_cuenta)
    return [
        movimiento for movimiento in banco.movimientos
        if movimiento["cuenta"] == numero_cuenta
    ]


def reporte_sistema(banco):
    return {
        "clientes": len(banco.clientes),
        "cuentas": len(banco.cuentas),
        "saldo_total": sum(cuenta["saldo"] for cuenta in banco.cuentas.values()),
        "movimientos": len(banco.movimientos),
    }


def imprimir_historial(movimientos):
    if not movimientos:
        print("No hay movimientos registrados.")
        return
    for movimiento in movimientos:
        print(
            f"{movimiento['fecha']} | {movimiento['tipo']} | "
            f"${movimiento['monto']:.2f} | {movimiento['detalle']}"
        )
