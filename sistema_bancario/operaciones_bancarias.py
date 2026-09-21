from historial import registrar_movimiento


def _monto_valido(monto):
    try:
        monto = float(monto)
    except (TypeError, ValueError) as error:
        raise ValueError("El monto debe ser numerico") from error
    if monto <= 0:
        raise ValueError("El monto debe ser mayor que cero")
    return monto


def _obtener_cuenta(banco, numero_cuenta):
    cuenta = banco.cuentas.get(str(numero_cuenta).strip())
    if cuenta is None:
        raise ValueError("La cuenta no existe")
    return cuenta


def depositar(banco, numero_cuenta, monto):
    monto = _monto_valido(monto)
    cuenta = _obtener_cuenta(banco, numero_cuenta)
    cuenta["saldo"] += monto
    registrar_movimiento(banco, numero_cuenta, "DEPOSITO", monto)
    return cuenta["saldo"]


def retirar(banco, numero_cuenta, monto):
    monto = _monto_valido(monto)
    cuenta = _obtener_cuenta(banco, numero_cuenta)
    if monto > cuenta["saldo"]:
        raise ValueError("Fondos insuficientes")
    cuenta["saldo"] -= monto
    registrar_movimiento(banco, numero_cuenta, "RETIRO", monto)
    return cuenta["saldo"]


def transferir(banco, cuenta_origen, cuenta_destino, monto):
    monto = _monto_valido(monto)
    if str(cuenta_origen) == str(cuenta_destino):
        raise ValueError("Las cuentas deben ser diferentes")
    origen = _obtener_cuenta(banco, cuenta_origen)
    destino = _obtener_cuenta(banco, cuenta_destino)
    if monto > origen["saldo"]:
        raise ValueError("Fondos insuficientes")
    origen["saldo"] -= monto
    destino["saldo"] += monto
    registrar_movimiento(banco, cuenta_origen, "TRANSFERENCIA ENVIADA", monto, f"A {cuenta_destino}")
    registrar_movimiento(banco, cuenta_destino, "TRANSFERENCIA RECIBIDA", monto, f"De {cuenta_origen}")
    return origen["saldo"]
