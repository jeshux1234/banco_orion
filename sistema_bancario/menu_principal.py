import tkinter as tk
from tkinter import messagebox, simpledialog, ttk

from gestor_de_clientes import crear_cuenta, iniciar_sesion, registrar_cliente
from historial import consultar_historial, reporte_sistema
from operaciones_bancarias import depositar, retirar, transferir
from sistema import crear_banco


class BancoOrionApp:
    def __init__(self, root, banco=None):
        self.root = root
        self.banco = banco or crear_banco()
        self.cuenta_actual = None
        self._configurar_ventana()
        self.mostrar_inicio()

    def _configurar_ventana(self):
        self.root.title("Banco Orion")
        self.root.geometry("900x600")
        self.root.minsize(760, 500)
        self.root.configure(bg="#eef3f8")
        estilo = ttk.Style(self.root)
        estilo.theme_use("clam")
        estilo.configure("Titulo.TLabel", font=("Segoe UI", 24, "bold"), foreground="#12304a")
        estilo.configure("Subtitulo.TLabel", font=("Segoe UI", 11), foreground="#587083")
        estilo.configure("Panel.TLabelframe", background="white")
        estilo.configure("Panel.TLabelframe.Label", font=("Segoe UI", 12, "bold"), foreground="#12304a")
        estilo.configure("Accion.TButton", font=("Segoe UI", 10, "bold"), padding=8)
        estilo.configure("Saldo.TLabel", font=("Segoe UI", 28, "bold"), foreground="#0b7564")

    def _limpiar(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    def _encabezado(self, subtitulo):
        encabezado = ttk.Frame(self.root, padding=(36, 28, 36, 12))
        encabezado.pack(fill="x")
        ttk.Label(encabezado, text="BANCO ORION", style="Titulo.TLabel").pack(anchor="w")
        ttk.Label(encabezado, text=subtitulo, style="Subtitulo.TLabel").pack(anchor="w", pady=(4, 0))

    def mostrar_inicio(self):
        self._limpiar()
        self._encabezado("Gestiona tus cuentas de forma simple y segura")
        contenedor = ttk.Frame(self.root, padding=(36, 12, 36, 36))
        contenedor.pack(fill="both", expand=True)
        contenedor.columnconfigure(0, weight=1)
        contenedor.columnconfigure(1, weight=1)
        contenedor.rowconfigure(0, weight=1)

        login = ttk.LabelFrame(contenedor, text="Iniciar sesion", padding=24)
        login.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        login.columnconfigure(1, weight=1)
        self.login_cuenta = tk.StringVar()
        self.login_clave = tk.StringVar()
        self._campo(login, "Numero de cuenta", self.login_cuenta, 0)
        self._campo(login, "Clave", self.login_clave, 1, ocultar=True)
        ttk.Button(login, text="Ingresar", style="Accion.TButton", command=self.iniciar_sesion).grid(
            row=2, column=0, columnspan=2, sticky="ew", pady=(20, 0)
        )

        registro = ttk.LabelFrame(contenedor, text="Nuevo cliente", padding=24)
        registro.grid(row=0, column=1, sticky="nsew", padx=(10, 0))
        registro.columnconfigure(1, weight=1)
        self.registro_nombre = tk.StringVar()
        self.registro_apellido = tk.StringVar()
        self.registro_rut = tk.StringVar()
        self.registro_clave = tk.StringVar()
        self.registro_cuenta = tk.StringVar()
        self._campo(registro, "Nombre", self.registro_nombre, 0)
        self._campo(registro, "Apellido", self.registro_apellido, 1)
        self._campo(registro, "RUT", self.registro_rut, 2)
        self._campo(registro, "Clave", self.registro_clave, 3, ocultar=True)
        self._campo(registro, "Numero de cuenta", self.registro_cuenta, 4)
        ttk.Button(registro, text="Registrar cliente", style="Accion.TButton", command=self.registrar).grid(
            row=5, column=0, columnspan=2, sticky="ew", pady=(20, 0)
        )
        ttk.Button(self.root, text="Reporte del sistema", command=self.mostrar_reporte).pack(
            anchor="e", padx=36, pady=(0, 20)
        )

    @staticmethod
    def _campo(parent, etiqueta, variable, fila, ocultar=False):
        ttk.Label(parent, text=etiqueta).grid(row=fila, column=0, sticky="w", pady=7, padx=(0, 12))
        entrada = ttk.Entry(parent, textvariable=variable, show="*" if ocultar else "")
        entrada.grid(row=fila, column=1, sticky="ew", pady=7)

    def registrar(self):
        try:
            registrar_cliente(
                self.banco,
                self.registro_nombre.get(),
                self.registro_apellido.get(),
                self.registro_rut.get(),
                self.registro_clave.get(),
            )
            crear_cuenta(self.banco, self.registro_rut.get(), self.registro_cuenta.get())
            messagebox.showinfo("Registro exitoso", "El cliente y la cuenta fueron registrados.")
            self.mostrar_inicio()
        except (ValueError, TypeError) as error:
            messagebox.showerror("No se pudo registrar", str(error))

    def iniciar_sesion(self):
        try:
            iniciar_sesion(self.banco, self.login_cuenta.get(), self.login_clave.get())
            self.cuenta_actual = self.login_cuenta.get().strip()
            self.mostrar_panel()
        except (ValueError, TypeError) as error:
            messagebox.showerror("Acceso denegado", str(error))

    def mostrar_panel(self):
        self._limpiar()
        cuenta = self.banco.cuentas[self.cuenta_actual]
        cliente = cuenta["cliente"]
        self._encabezado(f"Hola, {cliente.nombre_completo} | Cuenta {self.cuenta_actual}")
        contenido = ttk.Frame(self.root, padding=(36, 12, 36, 36))
        contenido.pack(fill="both", expand=True)
        contenido.columnconfigure(0, weight=1)
        contenido.columnconfigure(1, weight=1)

        saldo = ttk.LabelFrame(contenido, text="Saldo disponible", padding=24)
        saldo.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 18))
        self.saldo_label = ttk.Label(saldo, style="Saldo.TLabel")
        self.saldo_label.pack(anchor="w")
        self._actualizar_saldo()

        operaciones = ttk.LabelFrame(contenido, text="Operaciones", padding=18)
        operaciones.grid(row=1, column=0, sticky="nsew", padx=(0, 10))
        for texto, comando in (
            ("Depositar dinero", self.abrir_deposito),
            ("Retirar dinero", self.abrir_retiro),
            ("Transferir dinero", self.abrir_transferencia),
            ("Ver historial", self.mostrar_historial),
        ):
            ttk.Button(operaciones, text=texto, style="Accion.TButton", command=comando).pack(fill="x", pady=5)

        cuenta_info = ttk.LabelFrame(contenido, text="Cuenta", padding=18)
        cuenta_info.grid(row=1, column=1, sticky="nsew", padx=(10, 0))
        ttk.Label(cuenta_info, text=f"Titular: {cliente.nombre_completo}").pack(anchor="w", pady=6)
        ttk.Label(cuenta_info, text=f"RUT: {cliente.rut}").pack(anchor="w", pady=6)
        ttk.Button(cuenta_info, text="Cerrar sesion", command=self.cerrar_sesion).pack(fill="x", pady=(24, 5))

    def _actualizar_saldo(self):
        saldo = self.banco.cuentas[self.cuenta_actual]["saldo"]
        self.saldo_label.config(text=f"${saldo:,.2f}")

    def _pedir_monto(self, titulo):
        return simpledialog.askfloat(titulo, "Ingrese el monto:", parent=self.root, minvalue=0.01)

    def abrir_deposito(self):
        monto = self._pedir_monto("Depositar dinero")
        if monto is not None:
            try:
                depositar(self.banco, self.cuenta_actual, monto)
                self._actualizar_saldo()
                messagebox.showinfo("Deposito realizado", "El dinero fue depositado correctamente.")
            except ValueError as error:
                messagebox.showerror("Error", str(error))

    def abrir_retiro(self):
        monto = self._pedir_monto("Retirar dinero")
        if monto is not None:
            try:
                retirar(self.banco, self.cuenta_actual, monto)
                self._actualizar_saldo()
                messagebox.showinfo("Retiro realizado", "El dinero fue retirado correctamente.")
            except ValueError as error:
                messagebox.showerror("Error", str(error))

    def abrir_transferencia(self):
        destino = simpledialog.askstring("Transferir dinero", "Numero de cuenta destino:", parent=self.root)
        if not destino:
            return
        monto = self._pedir_monto("Transferir dinero")
        if monto is not None:
            try:
                transferir(self.banco, self.cuenta_actual, destino, monto)
                self._actualizar_saldo()
                messagebox.showinfo("Transferencia realizada", "La transferencia fue completada.")
            except ValueError as error:
                messagebox.showerror("Error", str(error))

    def mostrar_historial(self):
        ventana = tk.Toplevel(self.root)
        ventana.title("Historial de movimientos")
        ventana.geometry("760x360")
        ventana.transient(self.root)
        columnas = ("fecha", "tipo", "monto", "detalle")
        tabla = ttk.Treeview(ventana, columns=columnas, show="headings")
        for columna, titulo, ancho in (
            ("fecha", "Fecha", 150),
            ("tipo", "Operacion", 190),
            ("monto", "Monto", 100),
            ("detalle", "Detalle", 220),
        ):
            tabla.heading(columna, text=titulo)
            tabla.column(columna, width=ancho)
        for movimiento in consultar_historial(self.banco, self.cuenta_actual):
            tabla.insert("", "end", values=(
                movimiento["fecha"],
                movimiento["tipo"],
                f"${movimiento['monto']:.2f}",
                movimiento["detalle"],
            ))
        tabla.pack(fill="both", expand=True, padx=16, pady=16)

    def mostrar_reporte(self):
        reporte = reporte_sistema(self.banco)
        mensaje = (
            f"Clientes registrados: {reporte['clientes']}\n"
            f"Cuentas creadas: {reporte['cuentas']}\n"
            f"Saldo total: ${reporte['saldo_total']:.2f}\n"
            f"Movimientos: {reporte['movimientos']}"
        )
        messagebox.showinfo("Reporte del sistema", mensaje)

    def cerrar_sesion(self):
        self.cuenta_actual = None
        self.mostrar_inicio()


def ejecutar_menu(banco=None):
    root = tk.Tk()
    BancoOrionApp(root, banco)
    root.mainloop()
    return banco


if __name__ == "__main__":
    ejecutar_menu()
