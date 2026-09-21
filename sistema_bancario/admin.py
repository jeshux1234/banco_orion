from gestor_de_clientes import crear_cuenta, iniciar_sesion, registrar_cliente


def administracion_de_usuarios(banco):
    """Funciones para administrar clientes desde otros modulos."""
    return {
        "registrar_cliente": lambda *datos: registrar_cliente(banco, *datos),
        "iniciar_sesion": lambda *datos: iniciar_sesion(banco, *datos),
        "crear_cuenta": lambda *datos: crear_cuenta(banco, *datos),
    }