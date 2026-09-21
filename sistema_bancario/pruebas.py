from gestor_de_clientes import crear_cuenta, iniciar_sesion, registrar_cliente
from operaciones_bancarias import depositar, retirar, transferir
from sistema import crear_banco


def prueba_operaciones():
	banco = crear_banco()
	registrar_cliente(banco, "Ana", "Perez", "1-1", "1234")
	registrar_cliente(banco, "Luis", "Rojas", "2-2", "5678")
	crear_cuenta(banco, "1-1", "100")
	crear_cuenta(banco, "2-2", "200")
	iniciar_sesion(banco, "100", "1234")
	depositar(banco, "100", 1000)
	retirar(banco, "100", 150)
	transferir(banco, "100", "200", 300)
	assert banco.cuentas["100"]["saldo"] == 550
	assert banco.cuentas["200"]["saldo"] == 300
	assert len(banco.movimientos) == 4

	for operacion in (
		lambda: depositar(banco, "100", -1),
		lambda: retirar(banco, "100", 10000),
	):
		try:
			operacion()
		except ValueError:
			pass
		else:
			raise AssertionError("Se acepto una operacion invalida")

	return "Pruebas correctas"


if __name__ == "__main__":
	print(prueba_operaciones())
