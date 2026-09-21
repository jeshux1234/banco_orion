class BancoOrion:
    """Estado en memoria compartido por todos los modulos del sistema."""

    def __init__(self):
        self.clientes = {}
        self.cuentas = {}
        self.movimientos = []


def crear_banco():
    return BancoOrion()
