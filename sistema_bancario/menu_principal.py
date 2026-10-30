import tkinter as tk
from tkinter import messagebox, simpledialog, ttk

from gestor_de_clientes import crear_cuenta, iniciar_sesion, registrar_cliente
from historial import consultar_historial, reporte_sistema
from operaciones_bancarias import depositar, retirar, transferir
from sistema import crear_banco


class AplicacionBanco:
    def __init__(self, banco):
        self.banco = banco
        self.numero_cuenta = None

        self.root = tk.Tk()
        self.root.title("Banco Orion")
        self.root.geometry("680x460")
        self.root.minsize(580, 400)

        self.estilo = ttk.Style(self.root)
        if "clam" in self.estilo.theme_names():
            self.estilo.theme_use("clam")
        self.estilo.configure("Titulo.TLabel", font=("Segoe UI", 20, "bold"))
        self.estilo.configure("Saldo.TLabel", font=("Segoe UI", 18, "bold"))
        self.estilo.configure("Accion.TButton", padding=(12, 8))

        self.contenedor = ttk.Frame(self.root, padding=28)
        self.contenedor.pack(fill="both", expand=True)
        self.mostrar_inicio()

    def ejecutar(self):
        self.root.mainloop()

    def _limpiar(self):
        for widget in self.contenedor.winfo_children():
            widget.destroy()

    def mostrar_inicio(self):
        self.numero_cuenta = None
        self._limpiar()

        ttk.Label(
            self.contenedor, text="BANCO ORION", style="Titulo.TLabel"
        ).pack(pady=(35, 10))
        ttk.Label(
            self.contenedor, text="Sistema bancario"
        ).pack(pady=(0, 25))

        acciones = ttk.Frame(self.contenedor)
        acciones.pack()
        ttk.Button(
            acciones, text="Iniciar sesion", style="Accion.TButton",
            command=self.mostrar_inicio_sesion,
        ).grid(row=0, column=0, padx=8, pady=8, sticky="ew")
        ttk.Button(
            acciones, text="Registrar cliente", style="Accion.TButton",
            command=self.mostrar_registro,
        ).grid(row=0, column=1, padx=8, pady=8, sticky="ew")
        ttk.Button(
            acciones, text="Reporte del sistema", style="Accion.TButton",
            command=self.mostrar_reporte,
        ).grid(row=1, column=0, padx=8, pady=8, sticky="ew")
        ttk.Button(
            acciones, text="Salir", style="Accion.TButton",
            command=self.root.destroy,
        ).grid(row=1, column=1, padx=8, pady=8, sticky="ew")

    def _crear_formulario(self, titulo, campos, guardar):
        ventana = tk.Toplevel(self.root)
        ventana.title(titulo)
        ventana.resizable(False, False)
        ventana.transient(self.root)
        ventana.grab_set()

        formulario = ttk.Frame(ventana, padding=20)
        formulario.pack(fill="both", expand=True)
        ttk.Label(formulario, text=titulo, style="Titulo.TLabel").grid(
            row=0, column=0, columnspan=2, sticky="w", pady=(0, 16)
        )

        entradas = {}
        for fila, (clave, etiqueta, secreto) in enumerate(campos, start=1):
            ttk.Label(formulario, text=etiqueta).grid(
                row=fila, column=0, sticky="w", padx=(0, 12), pady=6
            )
            entrada = ttk.Entry(
                formulario, show="*" if secreto else "", width=30
            )
            entrada.grid(row=fila, column=1, sticky="ew", pady=6)
            entradas[clave] = entrada

        def enviar():
            datos = {
                clave: (
                    entrada.get()
                    if clave == "clave"
                    else entrada.get().strip()
                )
                for clave, entrada in entradas.items()
            }
            try:
                guardado = guardar(**datos)
            except (ValueError, TypeError) as error:
                messagebox.showerror("Error", str(error), parent=ventana)
                return
            if guardado is False:
                return
            ventana.destroy()

        ttk.Button(
            formulario, text="Continuar", command=enviar
        ).grid(row=len(campos) + 1, column=0, columnspan=2, pady=(16, 0))
        ventana.bind("<Return>", lambda _evento: enviar())
        next(iter(entradas.values())).focus_set()

    def mostrar_registro(self):
        def guardar(nombre, apellido, rut, clave, numero_cuenta):
            numero_cuenta = numero_cuenta.strip()
            if not numero_cuenta:
                raise ValueError("El numero de cuenta es obligatorio")
            if numero_cuenta in self.banco.cuentas:
                raise ValueError("El numero de cuenta ya existe")
            registrar_cliente(self.banco, nombre, apellido, rut, clave)
            crear_cuenta(self.banco, rut, numero_cuenta)
            messagebox.showinfo(
                "Registro", "Cliente y cuenta registrados correctamente.",
                parent=self.root,
            )
            return True

        self._crear_formulario(
            "Registro de cliente",
            [
                ("nombre", "Nombre", False),
                ("apellido", "Apellido", False),
                ("rut", "RUT", False),
                ("clave", "Clave", True),
                ("numero_cuenta", "Numero de cuenta", False),
            ],
            guardar,
        )

    def mostrar_inicio_sesion(self):
        def guardar(numero_cuenta, clave):
            try:
                iniciar_sesion(self.banco, numero_cuenta, clave)
            except (ValueError, TypeError) as error:
                messagebox.showerror(
                    "Acceso denegado", str(error), parent=self.root
                )
                return False
            self.numero_cuenta = numero_cuenta
            self.mostrar_cuenta()
            return True

        self._crear_formulario(
            "Inicio de sesion",
            [
                ("numero_cuenta", "Numero de cuenta", False),
                ("clave", "Clave", True),
            ],
            guardar,
        )

    def mostrar_cuenta(self):
        cuenta = self.banco.cuentas[self.numero_cuenta]
        cliente = cuenta["cliente"]
        self._limpiar()

        ttk.Label(
            self.contenedor, text="BANCO ORION", style="Titulo.TLabel"
        ).pack(anchor="w")
        ttk.Label(
            self.contenedor, text=f"Titular: {cliente.nombre_completo}"
        ).pack(anchor="w", pady=(10, 0))
        ttk.Label(
            self.contenedor, text=f"Cuenta: {self.numero_cuenta}"
        ).pack(anchor="w")
        ttk.Label(
            self.contenedor,
            text=f"Saldo: ${cuenta['saldo']:.2f}",
            style="Saldo.TLabel",
        ).pack(anchor="w", pady=(12, 20))

        acciones = ttk.Frame(self.contenedor)
        acciones.pack(anchor="w")
        botones = [
            ("Depositar dinero", self.realizar_deposito),
            ("Retirar dinero", self.realizar_retiro),
            ("Transferir dinero", self.realizar_transferencia),
            ("Ver historial", self.mostrar_historial),
            ("Cerrar sesion", self.mostrar_inicio),
        ]
        for fila, (texto, accion) in enumerate(botones):
            ttk.Button(
                acciones, text=texto, style="Accion.TButton", command=accion
            ).grid(row=fila, column=0, sticky="ew", pady=4)

    def _pedir_monto(self, titulo):
        return simpledialog.askfloat(
            titulo,
            "Ingrese un monto mayor que cero:",
            parent=self.root,
            minvalue=0.01,
        )

    def _mostrar_error_operacion(self, accion, monto):
        if monto is None:
            return
        try:
            saldo = accion(monto)
        except (ValueError, TypeError) as error:
            messagebox.showerror("Operacion no completada", str(error), parent=self.root)
            return
        self.mostrar_cuenta()
        messagebox.showinfo(
            "Operacion completada",
            f"Operacion realizada. Nuevo saldo: ${saldo:.2f}",
            parent=self.root,
        )

    def realizar_deposito(self):
        monto = self._pedir_monto("Deposito")
        self._mostrar_error_operacion(
            lambda valor: depositar(self.banco, self.numero_cuenta, valor),
            monto,
        )

    def realizar_retiro(self):
        monto = self._pedir_monto("Retiro")
        self._mostrar_error_operacion(
            lambda valor: retirar(self.banco, self.numero_cuenta, valor),
            monto,
        )

    def realizar_transferencia(self):
        destino = simpledialog.askstring(
            "Transferencia", "Numero de cuenta destino:", parent=self.root
        )
        if destino is None:
            return
        monto = self._pedir_monto("Transferencia")
        if monto is None:
            return
        try:
            saldo = transferir(
                self.banco, self.numero_cuenta, destino.strip(), monto
            )
        except (ValueError, TypeError) as error:
            messagebox.showerror(
                "Transferencia no completada", str(error), parent=self.root
            )
            return
        self.mostrar_cuenta()
        messagebox.showinfo(
            "Transferencia completada",
            f"Transferencia realizada. Nuevo saldo: ${saldo:.2f}",
            parent=self.root,
        )

    def mostrar_historial(self):
        movimientos = consultar_historial(self.banco, self.numero_cuenta)
        ventana = tk.Toplevel(self.root)
        ventana.title("Historial de movimientos")
        ventana.geometry("650x320")
        ventana.transient(self.root)

        columnas = ("fecha", "tipo", "monto", "detalle")
        tabla = ttk.Treeview(ventana, columns=columnas, show="headings")
        encabezados = {
            "fecha": "Fecha",
            "tipo": "Tipo",
            "monto": "Monto",
            "detalle": "Detalle",
        }
        anchos = {"fecha": 150, "tipo": 180, "monto": 100, "detalle": 180}
        for columna in columnas:
            tabla.heading(columna, text=encabezados[columna])
            tabla.column(columna, width=anchos[columna], anchor="w")
        for movimiento in movimientos:
            tabla.insert(
                "",
                "end",
                values=(
                    movimiento["fecha"],
                    movimiento["tipo"],
                    f"${movimiento['monto']:.2f}",
                    movimiento["detalle"],
                ),
            )
        tabla.pack(fill="both", expand=True, padx=12, pady=12)
        if not movimientos:
            ttk.Label(
                ventana, text="No hay movimientos registrados."
            ).pack(pady=(0, 12))

    def mostrar_reporte(self):
        reporte = reporte_sistema(self.banco)
        messagebox.showinfo(
            "Reporte del sistema",
            "Clientes registrados: {clientes}\n"
            "Cuentas creadas: {cuentas}\n"
            "Saldo total: ${saldo_total:.2f}\n"
            "Movimientos: {movimientos}".format(**reporte),
            parent=self.root,
        )


def ejecutar_menu(banco=None):
    banco = banco if banco is not None else crear_banco()
    AplicacionBanco(banco).ejecutar()
    return banco


if __name__ == "__main__":
    ejecutar_menu()
