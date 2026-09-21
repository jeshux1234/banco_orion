class cliente:
    """Datos y comportamiento basico de un cliente del banco."""

    def __init__(self, nombre, apellido, rut, password=None):
        self.nombre = nombre.strip()
        self.apellido = apellido.strip()
        self.rut = rut.strip()
        self.password = password

    @property
    def nombre_completo(self):
        return f"{self.nombre} {self.apellido}".strip()

    def creacion_de_contrasena(self, password=None):
        if self.password is not None:
            return False
        password = password if password is not None else input("Cree una contraseña: ")
        if not password or not str(password).strip():
            raise ValueError("La contraseña no puede estar vacia")
        self.password = str(password)
        return True

    def validacion_de_contrasena(self, password=None):
        password = password if password is not None else input("Ingrese su contraseña: ")
        return password == self.password

    def registro_usuario(self):
        nombre = input("Ingrese su nombre: ")
        apellido = input("Ingrese su apellido: ")
        rut = input("Ingrese su RUT: ")
        return nombre, apellido, rut


def registrar_cliente(banco, nombre, apellido, rut, password):
    if not all(str(valor).strip() for valor in (nombre, apellido, rut, password)):
        raise ValueError("Todos los datos del cliente son obligatorios")
    if rut in banco.clientes:
        raise ValueError("Ya existe un cliente con ese RUT")
    nuevo_cliente = cliente(nombre, apellido, rut, password)
    banco.clientes[rut] = nuevo_cliente
    return nuevo_cliente


def iniciar_sesion(banco, numero_cuenta, password):
    cuenta = banco.cuentas.get(str(numero_cuenta).strip())
    if cuenta is None or not cuenta["cliente"].validacion_de_contrasena(password):
        raise ValueError("Numero de cuenta o clave incorrectos")
    return cuenta


def crear_cuenta(banco, rut, numero_cuenta):
    numero_cuenta = str(numero_cuenta).strip()
    if rut not in banco.clientes:
        raise ValueError("El cliente no esta registrado")
    if not numero_cuenta:
        raise ValueError("El numero de cuenta es obligatorio")
    if numero_cuenta in banco.cuentas:
        raise ValueError("El numero de cuenta ya existe")
    cuenta = {"cliente": banco.clientes[rut], "saldo": 0.0}
    banco.cuentas[numero_cuenta] = cuenta
    return numero_cuenta