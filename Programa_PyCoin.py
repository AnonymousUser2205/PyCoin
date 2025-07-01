import random
import tkinter as tk
from tkinter import font
from tkinter import messagebox
from tkinter import ttk
import os

#Fecha
# 30/6/2025
##### VARIABLES #######
ventanas_abiertas = {"recibir": 0, "swap": 0,"enviar": 0, "comprar": 0, "vender": 0}
wallet_number = "6942969"
cryptos = []

# Estilo de los botones
bold_font = ("Arial", 12, "bold")
button_style = {
    'bg': '#007AFF',
    'fg': 'white',
    'width': 8,
    'height': 2,
    'bd': 0,
    'font': bold_font,
    'activebackground': '#005BBB',
    'activeforeground': 'white'
}


##### FUNCIONES DE GESTIÓN DE ARCHIVOS #########

def cargar_datos():
    global cryptos
    if os.path.exists("assets.txt"):
        with open("assets.txt", "r") as archivo:
            contenido = archivo.readlines()
            cryptos = []
            for linea in contenido:
                if linea.strip():  # Ignorar líneas vacías
                    try:
                        nombre, cantidad = linea.strip().split(',')
                        precio = obtener_precio_cripto(nombre)
                        cryptos.append((nombre, precio, float(cantidad)))
                    except ValueError:
                        # Línea mal formada, ignorar o manejar error
                        pass
    else:
        print("No se encuentra el archivo assets. Generando archivo por defecto.")
        generar_datos_por_defecto()


def guardar_datos():
    with open("assets.txt", "w") as archivo:
        for nombre, _, cantidad in cryptos:
            archivo.write(f"{nombre},{cantidad}\n")


def generar_datos_por_defecto():
    global cryptos
    cryptos = generar_cripto_data()
    guardar_datos()

precios_fijos = {
    "Ethereum": random.randint(400000, 600000) / 100,
    "Solana": random.randint(150000, 300000) / 100,
    "Avalanche": random.randint(80000, 150000) / 100,
    "Matic": random.randint(6000, 10000) / 100,
    "USD": 1.0
}

def obtener_precio_cripto(nombre):
    return precios_fijos.get(nombre, 0.0)


##### FUNCIONES #########

def conversion():
    pass


def generar_cripto_data():
    return [
        ("Ethereum", random.randint(400000, 600000) / 100, random.randint(150, 350) / 100),
        ("Solana", random.randint(150000, 300000) / 100, random.randint(5000, 7000) / 100),
        ("Avalanche", random.randint(80000, 150000) / 100, random.randint(5000, 7000) / 100),
        ("Matic", random.randint(6000, 10000) / 100, random.randint(1000, 1300) / 100),
        ("USD", 1.0, random.randint(100, 2000))
    ]

def calcular_saldo_total():
    total = 0
    for _, precio, cantidad in cryptos:
        total += precio * cantidad
    return total


def actualizar_saldo():
    total = calcular_saldo_total()
    saldo_var.set(f"${total:,.2f}")


def cerrar_ventana(ventana, tipo):
    ventana.destroy()
    ventanas_abiertas[tipo] -= 1


################################# FUNCION SWAP ###################################

def swap_cryptos(or_sfr, crypto_origen, cantidad, crypto_destino, cryptos, label_mensaje):
    # Busco las posiciones de las criptomonedas de origen y destino en nuestra lista de criptos.
    indice_origen, indice_destino = -1, -1  # Valor predeterminado mientras no se encuentre ka crypto -1

    #  Reviso cada criptomoneda en nuestra lista 'cryptos'
    # Información de cada cripto (nombre, precio, cantidad)
    for i, (nombre, _, _) in enumerate(cryptos):
        # Es el nombre de la crp = a la que queremos cambiar?
        if nombre == crypto_origen:
            indice_origen = i  # Guardamos su posición

        # Verifica si el nombre de la cripto actual es igual a la que queremos obtener
        if nombre == crypto_destino:
            indice_destino = i  # Guardamos su posición

    # Verificar si las dos criptomonedas que eligió el usuario son la misma / ind. iguales = misma crp
    if indice_origen == indice_destino:
        label_mensaje.config(text="Selecciona dos criptomonedas que sean diferentes.", fg="red")
        return False

        # Son diferentes
    if indice_origen != -1 and indice_destino != -1:
        # Saca la información de la cripto de origen usando su índice
        _, precio_origen, cantidad_origen = cryptos[indice_origen]
        # Saca la info de la cripto de destino, precio
        _, precio_destino, _ = cryptos[indice_destino]

        # Cantidad que quiere cambiar es válida?
        # No cero o menos, y no más de lo que tiene
        if cantidad <= 0 or cantidad > cantidad_origen:
            label_mensaje.config(text="La cantidad que ingresaste no es válida o no tienes suficiente.", fg="red") 
            return False

            # Calcula cuánto vale en la moneda base
        valor_origen = cantidad * precio_origen
        # Calcula cuánta cripto de destino puede obtener
        cantidad_destino = valor_origen / precio_destino

        # Actualizamos lista de criptomonedas
        # Cripto de origen, restamos la cantidad que se cambió
        cryptos[indice_origen] = (crypto_origen, precio_origen, cantidad_origen - cantidad)
        # Para la cripto de destino, sumamos la cantidad que se obtuvo
        cryptos[indice_destino] = (crypto_destino, precio_destino, cryptos[indice_destino][2] + cantidad_destino)

        # Guardar datos después de un swap
        guardar_datos()

        return True  # ¡Cambio exitoso!
    else:
        # Si no se enceuntra alguna de las dos criptomonedas...
        label_mensaje.config(text="Parece que una o ambas criptomonedas no existen en tu billetera.", fg="red")
        return False  # No se pudo hacer el cambio


def realizar_swap(crypto_origen_var, cantidad_var, crypto_destino_var, nueva_ventana_swap, label_mensaje):
    # Obtiene los valores que el usuario ingreso
    cripto_origen = crypto_origen_var.get()  # Cripto a cambiar
    cantidad_str = cantidad_var.get()  # Cantidad a cambiar
    cripto_destino = crypto_destino_var.get()  # Cripto a recibir

    # Intento convertir la cantidad a un número, decimal
    try:
        cantidad = float(cantidad_str)
        # Si conversión fue exitosa, llama a la función que realmente hace el cambio
        if swap_cryptos(None, cripto_origen, cantidad, cripto_destino, cryptos, label_mensaje):
            # Actualiza el saldo total que se muestra
            actualizar_saldo()

            label_mensaje.config(text=f"¡Listo! Se cambiaron {cantidad:.4f} {cripto_origen} por {cripto_destino}.", fg="green")
        
            # Actualiza la vista de las criptos en la ventana principal
            actualizar_vista_criptos()

    except ValueError:
        # Si ingresó algo que no es un número en la cantidad, muestra un error.
        label_mensaje.config(text="Por favor, ingresa una cantidad que sea un número válido.", fg="red")


def abrir_ventana_swap():
    # Verifica si hay una ventana de swap abierta
    if ventanas_abiertas["swap"] > 0:
        return  # Si está abierta, no abre otra

    # Marca que ahora hay una abierta
    ventanas_abiertas["swap"] += 1

    # Crea una nueva ventana encima de la principal
    nueva_ventana_swap = tk.Toplevel(root)
    nueva_ventana_swap.title("Cambiar Criptomonedas")  # Título
    nueva_ventana_swap.geometry("350x380")  # Tamaño
    nueva_ventana_swap.configure(bg='#121212')  # El color

    # Cierre de ventana
    nueva_ventana_swap.protocol("WM_DELETE_WINDOW", lambda: cerrar_ventana(nueva_ventana_swap, "swap"))

    # Crear variables para guardar lo que el usuario elija en los menus desplegables
    crypto_origen_var = tk.StringVar(nueva_ventana_swap)
    crypto_destino_var = tk.StringVar(nueva_ventana_swap)

    # Pone una etiqueta
    tk.Label(nueva_ventana_swap, text="Cripto Origen:", font=("Arial", 12), bg='#121212', fg='white').pack(pady=5)

    # Crea el menu desplegable para la cripto de origen
    # Saca los nombres de todas las criptos que hay
    nombres_criptos = [crypto[0] for crypto in cryptos]
    combo_origen = ttk.Combobox(nueva_ventana_swap, textvariable=crypto_origen_var, values=nombres_criptos)
    combo_origen.pack(pady=5)

    # Otra etiqueta para la cantidad a cambiar
    tk.Label(nueva_ventana_swap, text="Cantidad a Cambiar:", font=("Arial", 12), bg='#121212', fg='white').pack(pady=5)

    # Campo para que el usuario escriba la cantidad
    cantidad_var = tk.Entry(nueva_ventana_swap, font=("Arial", 12), justify='center')
    cantidad_var.pack(pady=5)

    # Etiqueta para la cripto de destino
    tk.Label(nueva_ventana_swap, text="Cripto Destino:", font=("Arial", 12), bg='#121212', fg='white').pack(pady=5)

    # Menu desplegable para la cripto a recibir
    combo_destino = ttk.Combobox(nueva_ventana_swap, textvariable=crypto_destino_var, values=nombres_criptos)
    combo_destino.pack(pady=5)

    # Disponible para las funciones de swap
    label_mensaje = tk.Label(nueva_ventana_swap, text="", font=("Arial", 11), bg="#121212")
    label_mensaje.pack(pady=10)

    # Boton para que se realice el cambio
    btn_cambiar = tk.Button(nueva_ventana_swap, text="Cambiar",
                            command=lambda: realizar_swap(crypto_origen_var, cantidad_var, crypto_destino_var,
                                                          nueva_ventana_swap, label_mensaje),
                            **button_style)
    btn_cambiar.pack(pady=10)


def actualizar_vista_criptos():
    # Redibujar la sección donde se muestran las crp

    # Accede a la variable global donde está el frame de las criptos
    global frame_cryptos

    # Para actualizar, eliminamos todo lo que esté dentro del frame
    for widget in frame_cryptos.winfo_children():
        widget.destroy()

    # Volvemos a crear la visualización con la información actualizada de crp
    for i, (name, price, amount) in enumerate(cryptos):
        # CFrame para cada criptomoneda
        frame = tk.Frame(frame_cryptos, bg='#1E1E1E')
        frame.pack(fill='x', pady=5)

        # Muestra el nombre de la cripto a la izquierda
        tk.Label(frame, text=name, font=("Arial", 12), bg='#1E1E1E', fg='white').pack(side='left')

        # Calcula el valor total de la cripto, precio . cantidad
        valor_total = price * amount
        # Y lo muestra
        tk.Label(frame, text=f"${valor_total:,.2f}", font=("Arial", 12, "bold"), bg='#1E1E1E', fg='white').pack(
            side='right')

        # Muestra la cantidad que se tiene
        tk.Label(frame, text=f"{amount:.4f} {name.upper()[0:3]}", font=("Arial", 10), fg='gray', bg='#1E1E1E').pack(
            side='right', padx=10)

        # No es la última cripto de la lista? Agrega una línea separadora
        if i < len(cryptos) - 1:
            tk.Frame(frame_cryptos, bg='white', height=1).pack(fill='x', pady=5)


def swap_fondos():
    # Llama a la función para abrir la ventana de swap
    abrir_ventana_swap()
################################## FUNCION ENVIAR ################################3
def enviar_fondos():
    if ventanas_abiertas["enviar"] > 0:
        return
    ventanas_abiertas["enviar"] += 1
    
    def leer_saldos():
        saldos = {}
        try:
            with open("assets.txt", "r") as f:
                for linea in f:
                    nombre, cantidad = linea.strip().split(',')
                    saldos[nombre] = float(cantidad)
        except FileNotFoundError:
            print("No se encontró el archivo")
        return saldos

    def guardar_saldos(saldos):
        with open("assets.txt", "w") as f:
            for cripto, cant in saldos.items():
                f.write(f"{cripto},{cant:.4f}\n")

    def actualizar_saldo_disponible(event=None): #Funcion para actualizar el saldo de la combo box
        cripto = combo_cripto.get()  # Obtiene la cripto seleccionada del combobox
        cantidad = saldos.get(cripto, 0.0)  # Busca el saldo de esa cripto en el diccionario
        label_saldo_var.set(f"Saldo disponible: {cantidad:.4f} {cripto}") # Actualiza el texto que se muestra en pantalla
        label_error.config(text="", fg="red") #Limpia cualquier mensaje de error anterior

    def procesar_envio():
        cripto = combo_cripto.get() #Obtiene el nombre de la cripto que el usuario selecciono en el combobox
        cantidad_str = entrada_cantidad.get().strip()#Obtiene el texto ingresado en el campo de entrada para la cantidad y quita espacios en blanco al principio o al final
        wallet_destino = entrada_wallet_destino.get().strip()#Toma texto que el usuario ingreso como numero de wallet de destino, y quita espacios al principio/final
        print(f"Usuario eligió: {cripto}, cantidad: {cantidad_str}, wallet destino: {wallet_destino}")

        # Validar cantidad
        try:
            cantidad = float(cantidad_str)
            if cantidad <= 0:
                raise ValueError
        except ValueError:
            label_error.config(text="❌ Cantidad inválida.", fg="red")
            print("Cantidad inválida.")
            return

        # Verificar existencia y saldo
        if cripto not in saldos:
            label_error.config(text=f"❌ No tienes {cripto} en tu wallet.", fg="red")
            print(f"No tienes {cripto} en tu wallet.")
            return
        if saldos[cripto] < cantidad:
            label_error.config(text=f"❌ Saldo insuficiente de {cripto}.", fg="red")
            print(f"Saldo insuficiente de {cripto}.")
            return

        # Validar wallet destino
        if not (wallet_destino.isdigit() and len(wallet_destino) == 7):
            label_error.config(text="❌ El número de wallet debe tener exactamente 7 dígitos.", fg="red")
            print("Número de wallet inválido: debe tener 7 dígitos.")
            return
        
        if wallet_destino == wallet_number:
            label_error.config(text="❌ No podes enviarte criptomonedas a vos mismo.", fg="red")
            print("Intento de autoenvío detectado.")
            return

        # Si todo esta correcto
        saldos[cripto] -= cantidad
        guardar_saldos(saldos)
        cargar_datos()
        actualizar_saldo()
        actualizar_vista_criptos()

        print(f"✅ Has enviado {cantidad} {cripto} a la wallet {wallet_destino}")
        label_error.config(text=f"✅ Has enviado {cantidad} {cripto} a {wallet_destino}", fg="lightgreen")
        
        entrada_cantidad.delete(0, tk.END)# Borra texto de cantidad
        entrada_wallet_destino.delete(0, tk.END)# Borra el numero de wallet
        combo_cripto.set('')  # Deselecciona la cripto elegida
        label_saldo_var.set('')  # Borra el saldo mostrado

    # Leer saldos iniciales
    saldos = leer_saldos()

    # Ventana secundaria
    ventana_enviar = tk.Toplevel(root)
    ventana_enviar.title("Enviar Fondos")
    ventana_enviar.geometry("400x400")
    ventana_enviar.configure(bg='#121212')
    
    ventana_enviar.protocol("WM_DELETE_WINDOW", lambda: cerrar_ventana(ventana_enviar, "enviar"))

    # Widgets
    tk.Label(ventana_enviar, text="Selecciona Criptomoneda", font=bold_font, bg="#121212", fg="white").pack(pady=5)

    combo_cripto = ttk.Combobox(ventana_enviar, values=list(saldos.keys()))
    combo_cripto.pack(pady=5)
    combo_cripto.bind("<<ComboboxSelected>>", actualizar_saldo_disponible)

    label_saldo_var = tk.StringVar()
    label_saldo = tk.Label(ventana_enviar, textvariable=label_saldo_var, font=("Arial", 10), bg="#121212", fg="lightgray")
    label_saldo.pack(pady=5)

    tk.Label(ventana_enviar, text="Cantidad a enviar", font=bold_font, bg="#121212", fg="white").pack(pady=5)
    entrada_cantidad = tk.Entry(ventana_enviar)
    entrada_cantidad.pack(pady=5)

    tk.Label(ventana_enviar, text="Wallet destino", font=bold_font, bg="#121212", fg="white").pack(pady=5)
    entrada_wallet_destino = tk.Entry(ventana_enviar)
    entrada_wallet_destino.pack(pady=5)

    btn_enviar = tk.Button(ventana_enviar, text="Enviar", command=procesar_envio, **button_style)
    btn_enviar.pack(pady=10)

    label_error = tk.Label(ventana_enviar, text="", font=("Arial", 10), bg="#121212", fg="red")
    label_error.pack(pady=5)

    if combo_cripto["values"]:
        combo_cripto.current(0)
        actualizar_saldo_disponible()

################################# FUNCION RECIBIR ################################
def compartir_wallet():
    # falta hacer
    print("Compartido...")


def recibir_fondos():
    if ventanas_abiertas["recibir"] > 0:
        return
    ventanas_abiertas["recibir"] += 1
    wallet_number = 6942969

    # Crear una nueva ventana
    nueva_ventana = tk.Toplevel(root)
    nueva_ventana.title("Recibir Fondos")
    nueva_ventana.geometry("400x300")  # Tamaño de la ventana
    nueva_ventana.configure(bg='#121212')

    # al cerrar la ventana, restamos el contador
    nueva_ventana.protocol("WM_DELETE_WINDOW", lambda: cerrar_ventana(nueva_ventana, "recibir"))

    # etiqueta para mostrar el numero de wallet
    label_wallet = tk.Label(nueva_ventana, text="Tu número de wallet es:", font=("Arial", 12), bg='#121212', fg='white')
    label_wallet.pack(pady=10)

    # campo de texto para mostrar el numero de wallet
    entry_wallet = tk.Entry(nueva_ventana, font=("Arial", 12), justify='center')
    entry_wallet.insert(0, wallet_number)  # Insertar el número de wallet
    entry_wallet.pack(pady=10)
    entry_wallet.config(state='readonly')  # Hacer el campo de texto solo lectura

    # Boton para copiar el numero de wallet
    btn_copiar = tk.Button(nueva_ventana, text="Copiar",
                           command=lambda: root.clipboard_clear() or root.clipboard_append(entry_wallet.get()),
                           **button_style)
    btn_copiar.pack(pady=5)

    # Boton para compartir el numero de wallet
    btn_compartir = tk.Button(nueva_ventana, text="Compartir", command=compartir_wallet, **button_style)
    btn_compartir.pack(pady=5)


# Funciones adicionales
def comprar_fondos():
    if ventanas_abiertas.get("comprar", 0) > 0:
        return
    ventanas_abiertas["comprar"] = 1

    ventana_comprar = tk.Toplevel(root)
    ventana_comprar.title("Comprar Fondos")
    ventana_comprar.geometry("400x450")
    ventana_comprar.configure(bg='#121212')



    def leer_saldos():
        saldos = {}
        try:
            with open("assets.txt", "r") as f:
                for linea in f:
                    nombre, cantidad = linea.strip().split(',')
                    saldos[nombre] = float(cantidad)
        except FileNotFoundError:
            pass  # archivo vacío al principio
        return saldos
    
    

    def guardar_saldos(saldos):
        with open("assets.txt", "w") as archivo:
            for nombre, cantidad in saldos.items():
                archivo.write(f"{nombre},{cantidad}\n")
                    

    def procesar_compra():
        cripto = combo_cripto.get()
        cantidad_str = entrada_cantidad.get().strip()

        try:
            cantidad = float(cantidad_str)
            if cantidad <= 0:
                raise ValueError
        except ValueError:
            label_error.config(text="❌ Cantidad inválida.", fg="red")
            return

        saldos = leer_saldos()

        #Solo actualizamos la cripto seleccionada
        if cripto in saldos:
            saldos[cripto] += cantidad
        else:
            saldos[cripto] = cantidad

        guardar_saldos(saldos)

        #Estas funciones NO deben tocar precios
        cargar_datos()            # ← debe solo actualizar cantidades
        actualizar_saldo()        # ← idem
        actualizar_vista_criptos()# ← idem

        label_error.config(text=f"✅ Has comprado {cantidad} {cripto}.", fg="green")
        entrada_cantidad.delete(0, tk.END)
        combo_cripto.current(0)  # ← volver al valor inicial tras la compra
    

    saldos = leer_saldos()
    ventana_comprar.protocol("WM_DELETE_WINDOW", lambda: (cerrar_ventana(ventana_comprar, "comprar"), ventanas_abiertas.update({"comprar": 0})))

    tk.Label(ventana_comprar, text="Selecciona Criptomoneda", font=bold_font, bg="#121212", fg="white").pack(pady=5)

    combo_cripto = ttk.Combobox(ventana_comprar, values=list(saldos.keys()), state='readonly')
    combo_cripto.current(0)  # ← valor por defecto al abrir la ventana
    combo_cripto.pack(pady=5)

    tk.Label(ventana_comprar, text="Cantidad a comprar", font=bold_font, bg="#121212", fg="white").pack(pady=10)
    entrada_cantidad = tk.Entry(ventana_comprar)
    entrada_cantidad.pack(pady=5)

    btn_comprar = tk.Button(ventana_comprar, text="Comprar", command=procesar_compra, **button_style)
    btn_comprar.pack(pady=10)

    label_error = tk.Label(ventana_comprar, text="", font=("Arial", 10), bg="#121212", fg="red")
    label_error.pack(pady=5)

    # Mostramos los precios actuales por cripto (extraídos de cryptos)
    tk.Label(ventana_comprar, text="Valores Criptos", font=bold_font, bg="#121212", fg="white").pack(pady=10)

    for cripto in saldos:
        # Buscamos el precio actual en la lista `cryptos`
        precio_unitario = next((precio for nombre, precio, _ in cryptos if nombre == cripto), None)

        if precio_unitario is not None:
            valor_unitario_str = f"${precio_unitario:,.2f}"
        else:
            valor_unitario_str = "N/A"

        texto = f"{cripto}: {valor_unitario_str}"
        tk.Label(ventana_comprar, text=texto, font=("Arial", 10), bg="#121212", fg="lightgray").pack()


# falta hacer
def vender_fondos():
    if ventanas_abiertas.get("vender", 0) > 0:
        return
    ventanas_abiertas["vender"] = 1

    ventana_vender = tk.Toplevel(root)
    ventana_vender.title("Vender Criptomonedas")
    ventana_vender.geometry("400x550")
    ventana_vender.configure(bg="#121212")

    ventana_vender.protocol("WM_DELETE_WINDOW", lambda: cerrar_ventana(ventana_vender, "vender"))

    tk.Label(ventana_vender, text="Seleccioná la criptomoneda a vender:",
             font=("Arial", 12), bg="#121212", fg="white").pack(pady=10)

    cripto_nombres = [nombre for nombre, _, _ in cryptos if nombre != "USD"]
    combo = ttk.Combobox(ventana_vender, values=cripto_nombres, state="readonly", font=("Arial", 12))
    combo.pack(pady=5)
    combo.set(cripto_nombres[0])

    tk.Label(ventana_vender, text="Cantidad a vender:", font=("Arial", 12), bg="#121212", fg="white").pack(pady=10)
    entry_cantidad = tk.Entry(ventana_vender, font=("Arial", 12), justify="center")
    entry_cantidad.pack(pady=5)

    # Entrada de CVU
    tk.Label(ventana_vender, text="CVU destino (10 dígitos)", font=("Arial", 12), bg="#121212", fg="white").pack(pady=10)
    entrada_cvu = tk.Entry(ventana_vender, font=("Arial", 12), justify="center")
    entrada_cvu.pack(pady=5)

    label_mensaje = tk.Label(ventana_vender, text="", font=("Arial", 11), bg="#121212")
    label_mensaje.pack(pady=10)

    def realizar_venta():
        nombre_cripto = combo.get()
        cantidad_str = entry_cantidad.get().strip()
        cvu = entrada_cvu.get().strip()

        # Validación de cantidad
        try:
            cantidad = float(cantidad_str)
            if cantidad <= 0:
                raise ValueError
        except ValueError:
            label_mensaje.config(text="❌ Cantidad inválida.", fg="red")
            return

        # Validación de CVU
        if not (cvu.isdigit() and len(cvu) == 10):
            label_mensaje.config(text="❌ El CVU debe tener exactamente 10 dígitos numéricos.", fg="red")
            return

        for i, (nombre, precio, cantidad_disponible) in enumerate(cryptos):
            if nombre == nombre_cripto:
                if cantidad > cantidad_disponible:
                    label_mensaje.config(text="❌ No tenés suficiente saldo.", fg="red")
                    return
                else:
                    precio_usd = obtener_precio_cripto(nombre_cripto)
                    valor_total = cantidad * precio_usd

                    # Descontar de la cripto vendida
                    cryptos[i] = (nombre, precio, cantidad_disponible - cantidad)

                    # Sumar USD al balance
                    for j, (n, p, a) in enumerate(cryptos):
                        if n == "USD":
                            cryptos[j] = (n, p, a + valor_total)
                            break

                    actualizar_vista_criptos()
                    entry_cantidad.delete(0, tk.END)
                    entrada_cvu.delete(0, tk.END)
                    combo.current(0)

                    label_mensaje.config(
                        text=f"✅ Vendiste {cantidad:.4f} {nombre_cripto} por ${valor_total:,.2f} USD\nEnviado a CVU {cvu}",
                        fg="lightgreen"
                    )
                    return

        label_mensaje.config(text="❌ Criptomoneda no encontrada.", fg="red")

    tk.Button(ventana_vender, text="Vender", command=realizar_venta, **button_style).pack(pady=15)

    # Mostrar valores actuales en USD
    tk.Label(ventana_vender, text="Valores Criptos (USD)", font=bold_font, bg="#121212", fg="white").pack(pady=10)
    for cripto in cripto_nombres:
        precio_usd = obtener_precio_cripto(cripto)
        texto = f"{cripto}: ${precio_usd:,.2f}"
        tk.Label(ventana_vender, text=texto, font=("Arial", 10), bg="#121212", fg="lightgray").pack()



# ----------- INICIO DEL PROGRAMA -----------

# Al inicio del programa, cargar los datos
cargar_datos()

# Configuración de la ventana
root = tk.Tk()
root.title("Crypto Wallet")
root.geometry("600x500")
root.configure(bg='#121212')

# Fuente personalizada
bold_font = font.Font(family="Arial", size=14, weight="bold")

# Contenedor principal
frame_main = tk.Frame(root, bg='#1E1E1E', bd=2, relief='ridge')
frame_main.pack(padx=10, pady=10, fill='both', expand=True)

# Saldo Total
saldo_var = tk.StringVar()
actualizar_saldo()
tk.Label(frame_main, textvariable=saldo_var, font=("Arial", 25, "bold"), bg='#1E1E1E', fg='white').pack(pady=5)

# Botones de acciones
frame_buttons = tk.Frame(frame_main, bg='#1E1E1E')
frame_buttons.pack(pady=10)

tk.Button(frame_buttons, text="Comprar", command=comprar_fondos, **button_style).grid(row=0, column=0, padx=5)
tk.Button(frame_buttons, text="Vender", command=vender_fondos, **button_style).grid(row=0, column=1, padx=5)
tk.Button(frame_buttons, text="Cambiar", command=swap_fondos, **button_style).grid(row=0, column=2, padx=5)
tk.Button(frame_buttons, text="Enviar", command=enviar_fondos, **button_style).grid(row=0, column=3, padx=5)
tk.Button(frame_buttons, text="Recibir", command=recibir_fondos, **button_style).grid(row=0, column=4, padx=5)

# Separador
tk.Frame(frame_main, bg='#E0E0E0', height=1).pack(fill='x', padx=10, pady=10)

# Seccion de criptomonedas
frame_cryptos = tk.Frame(frame_main, bg='#1E1E1E')
frame_cryptos.pack(fill='x', padx=10)

actualizar_vista_criptos()
root.mainloop()

