from gestor_de_clientes import crear_cuenta, iniciar_sesion, registrar_cliente
from historial import consultar_historial, imprimir_historial, reporte_sistema
from operaciones_bancarias import depositar, retirar, transferir
from sistema import crear_banco


def _leer_monto(mensaje):
    while True:
        try:
            monto = float(input(mensaje))
            if monto <= 0:
                raise ValueError
            return monto
        except ValueError:
            print("Ingrese un monto numerico mayor que cero.")


def _mostrar_reporte(banco):
    reporte = reporte_sistema(banco)
    print("\n--- Reporte del sistema ---")
    print(f"Clientes registrados: {reporte['clientes']}")
    print(f"Cuentas creadas: {reporte['cuentas']}")
    print(f"Saldo total: ${reporte['saldo_total']:.2f}")
    print(f"Movimientos: {reporte['movimientos']}")


def _registrar(banco):
    print("\n--- Registro de cliente ---")
    nombre = input("Nombre: ")
    apellido = input("Apellido: ")
    rut = input("RUT: ")
    clave = input("Clave: ")
    numero_cuenta = input("Numero de cuenta: ")
    try:
        registrar_cliente(banco, nombre, apellido, rut, clave)
        crear_cuenta(banco, rut, numero_cuenta)
        print("Cliente y cuenta registrados correctamente.")
    except (ValueError, TypeError) as error:
        print(f"No se pudo registrar: {error}")


def _mostrar_historial(banco, numero_cuenta):
    print("\n--- Historial de movimientos ---")
    imprimir_historial(consultar_historial(banco, numero_cuenta))


def _menu_cuenta(banco, numero_cuenta):
    while True:
        cuenta = banco.cuentas[numero_cuenta]
        cliente = cuenta["cliente"]
        print("\n=== BANCO ORION ===")
        print(f"Titular: {cliente.nombre_completo}")
        print(f"Cuenta: {numero_cuenta}")
        print(f"Saldo: ${cuenta['saldo']:.2f}")
        print("1. Depositar dinero")
        print("2. Retirar dinero")
        print("3. Transferir dinero")
        print("4. Ver historial")
        print("5. Cerrar sesion")

        opcion = input("Seleccione una opcion: ").strip()
        try:
            if opcion == "1":
                saldo = depositar(banco, numero_cuenta, _leer_monto("Monto a depositar: "))
                print(f"Deposito realizado. Nuevo saldo: ${saldo:.2f}")
            elif opcion == "2":
                saldo = retirar(banco, numero_cuenta, _leer_monto("Monto a retirar: "))
                print(f"Retiro realizado. Nuevo saldo: ${saldo:.2f}")
            elif opcion == "3":
                destino = input("Cuenta destino: ").strip()
                monto = _leer_monto("Monto a transferir: ")
                saldo = transferir(banco, numero_cuenta, destino, monto)
                print(f"Transferencia realizada. Nuevo saldo: ${saldo:.2f}")
            elif opcion == "4":
                _mostrar_historial(banco, numero_cuenta)
            elif opcion == "5":
                print("Sesion cerrada.")
                return
            else:
                print("Opcion no valida.")
        except (ValueError, TypeError) as error:
            print(f"No se pudo completar la operacion: {error}")


def _iniciar_sesion(banco):
    print("\n--- Inicio de sesion ---")
    numero_cuenta = input("Numero de cuenta: ").strip()
    clave = input("Clave: ")
    try:
        iniciar_sesion(banco, numero_cuenta, clave)
        _menu_cuenta(banco, numero_cuenta)
    except (ValueError, TypeError) as error:
        print(f"Acceso denegado: {error}")


def ejecutar_menu(banco=None):
    banco = banco or crear_banco()
    while True:
        print("\n=== BANCO ORION ===")
        print("1. Registrar cliente")
        print("2. Iniciar sesion")
        print("3. Ver reporte del sistema")
        print("4. Salir")

        try:
            opcion = input("Seleccione una opcion: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nPrograma finalizado.")
            break

        if opcion == "1":
            _registrar(banco)
        elif opcion == "2":
            _iniciar_sesion(banco)
        elif opcion == "3":
            _mostrar_reporte(banco)
        elif opcion == "4":
            print("Programa finalizado.")
            break
        else:
            print("Opcion no valida.")
    return banco


if __name__ == "__main__":
    ejecutar_menu()