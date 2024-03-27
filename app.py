from flask import Flask, render_template, request, url_for, flash, session, redirect
from flask_mysqldb import MySQL
from flask_mail import Mail
from flask_mail import Message
from werkzeug.utils import secure_filename
import os, re

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Configuración para MySQL
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'AngieStudio'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
app.config['UPLOAD_FOLDER'] = 'static/img'

# Configuracion para enviar correos
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'dilanyarce22@gmail.com'  
app.config['MAIL_PASSWORD'] = 'ppoj ltoy ryhq zrkg'  
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True

mail = Mail(app)

mysql = MySQL(app)

# Rutas y funciones para la primera aplicación
# Ruta para cuando se inicialice el programa se inicie desde el index.html
@app.route('/')
def home():
    return render_template("index.html")

# Funcion del login para inicar sesion
@app.route('/acceso-login', methods=["GET", "POST"])
def login():
    if request.method == 'POST' and 'txtCorreo' in request.form and 'txtPassword' in request.form:
        _correo = request.form['txtCorreo']
        _password = request.form['txtPassword']

        cur = mysql.connection.cursor()
        cur.execute('SELECT * FROM usuarios WHERE correo = %s AND password = %s', (_correo, _password,))
        account = cur.fetchone()

        if account:
            session['logueado'] = True
            session['id'] = account['id']  
            session['id_rol'] = account['id_rol']  
            session['nombre'] = account['nombre']  

            if session['id_rol'] == 1:
                return render_template("Administrador.html", nombre=session['nombre'])
            elif session['id_rol'] == 2:
                return render_template("Empleado.html", nombre=session['nombre'])
            elif session['id_rol'] == 3:
                return render_template("Cliente.html", nombre=session['nombre'])
        else:
            return render_template('login.html', mensaje="¡Usuario o contraseña incorrectas!")

    return render_template('login.html')

# Funcion para redirigir al Administrador.html
@app.route('/admin')
def admin():
    return render_template("Administrador.html", nombre=session.get('nombre'))

# Redireccion al template del empleado
@app.route('/Empleado')
def Empleado():
    return render_template("Empleado.html", nombre=session.get('nombre'))

# Redireccion al template de cliente
@app.route('/Cliente')
def Cliente():
    return render_template("Cliente.html", nombre=session.get('nombre'))

# Redireccion al template de registrar empleado
@app.route('/Redirigir_Empleado')
def Redirigir_Empleado():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM usuarios WHERE id_rol = 2")
    empleados = cur.fetchall()
    cur.close()
    return render_template("Registrar_Empleado.html", empleados=empleados, nombre=session.get('nombre'))


#Redirigir al template de Citas.html
@app.route('/Citas', methods=['GET', 'POST'])
def Citas():
    if request.method == 'POST':
        id_cita = request.form['id_cita']
        fecha = request.form['fecha']
        hora = request.form['hora']
        servicio = request.form['servicio']  
        empleado_nombre = request.form['empleado_nombre'] 
        motivo = request.form['motivo']
        
        # Actualizar la cita en la base de datos
        cur = mysql.connection.cursor()
        cur.execute("UPDATE citas SET fecha=%s, hora=%s, servicio=%s, empleado_nombre=%s, motivo=%s WHERE id_cita=%s", 
                    (fecha, hora, servicio, empleado_nombre, motivo, id_cita)) 
        mysql.connection.commit()
        cur.close()
        
        flash("Cita actualizada correctamente.")
        return redirect(url_for('Citas'))

    # Obtener el ID del cliente logeado desde la sesión
    cliente_id = session.get('id')

    cursor = mysql.connection.cursor()

    if session.get('id_rol') == 2:  # Si el usuario es un empleado
        # Consulta para obtener el nombre del empleado logueado
        cursor.execute("SELECT nombre FROM usuarios WHERE id = %s", (cliente_id,))
        nombre_empleado = cursor.fetchone()['nombre']

        # Consulta para obtener las citas del empleado logeado
        cursor.execute("SELECT * FROM citas WHERE empleado_nombre = %s", (nombre_empleado,))
    elif session.get('id_rol') == 1:  # Si el usuario es un administrador
        # Consulta para obtener todas las citas
        cursor.execute("SELECT * FROM citas")
    else:
        # Consulta para obtener las citas del cliente logeado
        cursor.execute("SELECT * FROM citas WHERE id_cliente = %s", (cliente_id,))
    
    citas = cursor.fetchall()

    # Consulta para obtener nombres de servicios
    cursor.execute("SELECT nombre FROM servicios")
    servicios = cursor.fetchall()
    nombres_servicios = [servicio['nombre'] for servicio in servicios]

    # Consulta para obtener nombres de empleados
    cursor.execute("SELECT nombre FROM usuarios WHERE id_rol = 2")
    empleados = cursor.fetchall()
    empleados_servicios = [empleado['nombre'] for empleado in empleados]
    
    # Consulta para obtener nombres de servicios
    cursor.execute("SELECT nombre FROM servicios")
    servicios = cursor.fetchall()
    nombres_servicios = [servicio['nombre'] for servicio in servicios]

    cursor.close()

    return render_template("Citas.html", nombres_servicios=nombres_servicios, empleados_servicios=empleados_servicios, citas=citas, nombre=session.get('nombre'), lista_servicios=nombres_servicios)


@app.route('/agregar_servicio', methods=['POST'])
def agregar_servicio():
    if request.method == 'POST':
        nombre_servicio = request.form['nombre_servicio']
        empleado = request.form['empleados_nombre']

        # Insertar el nuevo servicio en la base de datos
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO servicios (nombre, empleado) VALUES (%s, %s)", (nombre_servicio, empleado))
        mysql.connection.commit()
        cur.close()

        flash("Nuevo servicio agregado correctamente.")
        return redirect(url_for('Citas'))
    else:
        flash("Error al agregar el nuevo servicio.")
        return redirect(url_for('Citas'))

# Función para cerrar sesión
@app.route('/logout')
def logout():
    # Eliminar la sesión del usuario
    session.clear()
    # Redirigir al usuario a la página de inicio
    return redirect(url_for('home'))

# Función para redirigir al registro.html
@app.route('/registro')
def registro():
    return render_template("registro.html")

# Función para crear el registro desde el template del registro
@app.route('/crear-registro', methods=["GET", "POST"])
def crear_registro():
    if request.method == "POST":
        correo = request.form['txtCorreo']
        password = request.form['txtPassword']
        nombre = request.form['txtNombre']
        apellido = request.form['txtApellido']
        telefono = request.form['txtTelefono']
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO usuarios (correo, password, nombre, apellido, telefono, id_rol) VALUES (%s, %s, %s, %s, %s, %s)",
                    (correo, password, nombre, apellido, telefono, '3'))
        mysql.connection.commit()
        cur.close()
        url_for('static', filename='style.css')
        return render_template("login.html")
    else:
        pass

# Función para crear Empleados
@app.route('/Registrar_Empleado', methods=["GET", "POST"])
def Registrar_Empleado():
    if request.method == "POST":
        correo = request.form.get('correo')
        password = request.form.get('password')
        nombre = request.form.get('nombre')
        apellido = request.form.get('apellido')
        telefono = request.form.get('telefono')
        # Asegúrate de que tu conexión y consulta SQL sean correctas
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO usuarios (correo, password, nombre, apellido, telefono, id_rol) VALUES (%s, %s, %s, %s, %s, %s)",
                    (correo, password, nombre, apellido, telefono, 2))
        mysql.connection.commit()
        cur.close()
        return redirect(url_for('Redirigir_Empleado'), nombre=session.get('nombre'))  
    else:
        #Listar empleado en la tabla
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM usuarios WHERE id_rol = 2")
        empleados = cur.fetchall()  
        cur.close()
        return render_template("Registrar_Empleado.html", empleados=empleados, nombre=session.get('nombre'))  

# Función del inventario para seleccionar los productos y los campos
@app.route('/inventario')
def inventario():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM productos")
    productos_data = cur.fetchall()
    cur.close()
    return render_template('inventario.html', productos=productos_data, nombre=session.get('nombre'))

# Función para insertar un nuevo producto
@app.route('/insert', methods=['POST'])
def insert():
    if request.method == "POST":
        flash("Producto ingresado con éxito")
        Nombre = request.form['Nombre']
        Cantidad = request.form['Cantidad']
        Marca = request.form['Marca']
        Precio = request.form['Precio']
        Descripcion = request.form['Descripcion']
        Fecha_vencimiento = request.form['Fecha_vencimiento']
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO productos (Nombre, Cantidad, Marca, Precio, Descripcion, Fecha_vencimiento) VALUES (%s, %s, %s, %s, %s, %s)", 
                    (Nombre, Cantidad, Marca, Precio, Descripcion, Fecha_vencimiento))
        mysql.connection.commit()
        return redirect(url_for('inventario', nombre=session.get('nombre')))

# Función para eliminar el producto
@app.route('/delete/<string:Id>', methods=['GET'])
def delete(Id):
    try:
        cur = mysql.connection.cursor()
        cur.execute("DELETE FROM productos WHERE Id=%s", (Id,))
        mysql.connection.commit()
        flash("Producto eliminado con éxito")
    except Exception as e:
        flash("Error al eliminar el producto: " + str(e))
    finally:
        cur.close()
    return redirect(url_for('inventario'))

@app.route('/ Delete_Empleado/<string:id>', methods=['GET'])
def Delete_Empleado(id):
    try:
        cur = mysql.connection.cursor()
        cur.execute("DELETE FROM usuarios WHERE id=%s", (id,))
        mysql.connection.commit()
        flash("Empleado eliminado con éxito")
    except Exception as e:
        flash("Error al eliminar el empleado: " + str(e))
    finally:
        cur.close()
    return redirect(url_for('Redirigir_Empleado', nombre=session.get('nombre')))

# Función para actualizar un producto
@app.route('/update', methods=['POST', 'GET'])
def update():
    if request.method == 'POST':
        Id = request.form['Id']
        Nombre = request.form['Nombre']
        Cantidad = request.form['Cantidad']
        Marca = request.form['Marca']
        Precio = request.form['precio']
        Descripcion = request.form['Descripcion']
        Fecha_vencimiento = request.form['Fecha_vencimiento']
        try:
            cur = mysql.connection.cursor()
            cur.execute("""
            UPDATE productos SET Nombre=%s, Cantidad=%s, Marca=%s, Precio=%s, Descripcion=%s, Fecha_vencimiento=%s
            WHERE Id=%s
            """, (Nombre, Cantidad, Marca, Precio, Descripcion, Fecha_vencimiento, Id))
            
            mysql.connection.commit()
            flash("Actualizado con éxito")
            return redirect(url_for('inventario', nombre=session.get('nombre')))
        except Exception as e:
            flash(f"Error al actualizar: {str(e)}")
        finally:
            cur.close()
    return render_template('inventario.html', nombre=session.get('nombre'))

# Update_Empleado Función para editar al empleado
@app.route('/Update_Empleado', methods=['POST', 'GET'])
def Update_Empleado():
    if request.method == 'POST':
        id = request.form['id']
        Correo = request.form['correo']
        Nombre = request.form['Nombre']
        apellido = request.form['apellido']
        telefono = request.form['telefono']
        try:
            cur = mysql.connection.cursor()
            cur.execute("""
            UPDATE usuarios SET correo=%s, nombre=%s, apellido=%s, telefono=%s
            WHERE id=%s
            """, (Correo, Nombre, apellido, telefono, id))
            
            mysql.connection.commit()
            flash("Empleado actualizado con éxito")
            return redirect(url_for('inventario', nombre=session.get('nombre')))
        except Exception as e:
            flash(f"Error al actualizar al empleado: {str(e)}")
        finally:
            cur.close()
    return render_template('Redirigir_Empleado', nombre=session.get('nombre'))

# Función del inventario para registrar las entradas
@app.route('/Entradas')
def Entradas():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM entrada_productos")
    entradas_data = cur.fetchall()
    cur.close()
    return render_template('Entradas.html', entradas_data=entradas_data, nombre=session.get('nombre'))

# Función para redirigir al template de Entradas.html
@app.route('/redireccionar_a_entradas')
def redireccionar_a_entradas():
    # Redireccionar a la página de Entradas.html
    return redirect(url_for('Entradas', nombre=session.get('nombre')))

# Función para registrar las salidas de los productos
@app.route('/Salidas')
def Salidas():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM salida_productos")
    salidas_data = cur.fetchall()
    cur.close()
    return render_template('Salidas.html', salidas=salidas_data, nombre=session.get('nombre'))

# Función para registrar las novedades de los productos
# Función para mostrar las novedades de entrada
@app.route('/Novedades')
def Novedades():
    cur = mysql.connection.cursor()
    cur.execute("SELECT n.*, p.Cantidad AS Cantidad_Actual FROM Novedades n JOIN productos p ON n.Id_Producto = p.Id WHERE n.Tipo = 'Entrada'")
    entradas_data = cur.fetchall()

    cur.execute("SELECT * FROM Novedades WHERE Tipo = 'Salida'")
    salidas_data = cur.fetchall()

    cur.close()
    
    return render_template('Novedades.html', entradas=entradas_data, salidas=salidas_data, nombre=session.get('nombre'))

# --------------------------------------------------------Registrar Citas
@app.route('/Registrar_Cita', methods=["GET", "POST"])
def Registrar_Cita():
    if request.method == "POST":
        cliente_id = session.get('id')

        # Verificar el límite de citas
        cur = mysql.connection.cursor()
        cur.execute("SELECT num_citas FROM usuarios WHERE id = %s", (cliente_id,))
        num_citas = cur.fetchone()['num_citas']
        cur.close()

        if num_citas >= 5:
            flash("Has alcanzado el límite de 5 citas por favor, elimina una cita existente para agregar una nueva.")
            return redirect(url_for('Citas'))

        # Procesar el formulario de cita
        nombre = request.form.get('nombre')
        servicio = request.form.get('servicio')
        empleado_nombre = request.form.get('empleados_nombre')
        fecha = request.form.get('Fecha')
        hora = request.form.get('Hora')
        motivo = request.form.get('motivo')

        # Verificar si la cita ya existe
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM citas WHERE nombre = %s AND servicio = %s AND empleado_nombre = %s AND fecha = %s AND hora = %s AND id_cliente = %s",
                    (nombre, servicio, empleado_nombre, fecha, hora, cliente_id))
        existing_cita = cur.fetchone()
        cur.close()

        # Insertar la cita en la base de datos
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO citas (nombre, servicio, empleado_nombre, fecha, hora, motivo, id_cliente) VALUES (%s, %s, %s, %s, %s, %s, %s)",
                    (nombre, servicio, empleado_nombre, fecha, hora, motivo, cliente_id))
        mysql.connection.commit()

        # Obtener el correo electrónico del usuario
        cur = mysql.connection.cursor()
        cur.execute("SELECT correo FROM usuarios WHERE id = %s", (cliente_id,))
        user_email = cur.fetchone()['correo']
        cur.close()

        # Enviar correo electrónico
        msg = Message('Nueva cita registrada', sender='dilanyarce22@gmail.com', recipients=[user_email])
        msg.body = f"""\
        Nueva cita registrada

        Se ha registrado una nueva cita para {nombre} el día {fecha} a las {hora} con el empleado {empleado_nombre}. Motivo: {motivo}
        """
        mail.send(msg)

        flash("Cita agregada correctamente.")
        return redirect(url_for('Citas'))

    return render_template("Citas.html", nombre=session.get('nombre'))

# ---------------------------------------------------Funcion pora eliminar cita
@app.route('/eliminar_cita/<int:cita_id>', methods=["GET"])
def eliminar_cita(cita_id):
    try:
        # Eliminar la cita de la base de datos
        cur = mysql.connection.cursor()
        cur.execute("DELETE FROM citas WHERE id_cita = %s", (cita_id,))
        mysql.connection.commit()
        cur.close()

        flash("Cita eliminada correctamente.")
    except Exception as e:
        flash("Error al eliminar la cita: " + str(e))

    return redirect(url_for('Citas'))

# -----------------------------------------Funcion para pedir el correo para el restablecimiento de contraseña
@app.route('/forgot', methods=['GET', 'POST'])
def forgot():
    error = None
    if request.method == 'POST':
        user_email = request.form['txtCorreo']
            
        session['reset_email'] = user_email
        send_reset_email(user_email)
        return redirect(url_for('login'))
    return render_template('forgot.html', error=error)

# -----------------------Función para enviar el correo electrónico con el enlace de restablecimiento de contraseña
def send_reset_email(user_email):
    reset_link = url_for('newpassword', _external=True)
    msg = Message('Recuperación de contraseña', sender='dilanyarce22@gmail.com', recipients=[user_email])
    msg.body = f'Para restablecer tu contraseña, haz clic en el siguiente enlace: {reset_link}'
    mail.send(msg)

# -----------------------------------------------------Ruta para restablecer la contraseña
@app.route('/newpassword', methods=['GET', 'POST'])
def newpassword():
    error = None
    if request.method == 'POST':
        if request.form['newpass'] != request.form['conpass']:
            error = 'Las contraseñas no coinciden..!!'
        else:
            user_email = session.get('reset_email')
            new_password = request.form['newpass']
            if update_password_in_database(user_email, new_password):
                session.pop('reset_email', None)
                return redirect(url_for('login'))
            else:
                error = 'Error al actualizar la contraseña. Por favor, inténtalo de nuevo.'
    return render_template('newpassword.html', error=error)

#---------------------------------------- Función para actualizar la contraseña en la base de datos
def update_password_in_database(user_email, new_password):
    try:
        cur = mysql.connection.cursor()
        cur.execute("UPDATE usuarios SET password = %s WHERE correo = %s", (new_password, user_email))
        mysql.connection.commit()
        cur.close()
        return True
    except Exception as e:
        print("Error al actualizar la contraseña:", e)
        return False
    
#------------------------------------------------------------------ Actualizar cuenta
@app.route('/actualizar-cuenta', methods=['GET', 'POST'])
def actualizar_cuenta():
    if request.method == 'POST':
        # Obtener los datos del formulario
        nuevo_nombre = request.form['txtNombre']
        nuevo_apellido = request.form['txtApellido']
        nuevo_correo = request.form['txtCorreo']
        nuevo_telefono = request.form['txtTelefono']
        nueva_contrasena = request.form['txtPassword']
        confirmar_contrasena = request.form['txtConfirmPassword']

        # Validar que las contraseñas coincidan
        if nueva_contrasena != confirmar_contrasena:
            flash('Las contraseñas no coinciden. Inténtalo de nuevo.', 'error')
            return redirect(url_for('actualizar_cuenta'))

        # Actualizar los datos en la base de datos
        cur = mysql.connection.cursor()
        cur.execute("UPDATE usuarios SET nombre = %s, apellido = %s, correo = %s, telefono = %s, password = %s WHERE id = %s",
                    (nuevo_nombre, nuevo_apellido, nuevo_correo, nuevo_telefono, nueva_contrasena, session['id']))
        mysql.connection.commit()
        cur.close()

        flash('Información de la cuenta actualizada correctamente.', 'success')
        return redirect(url_for('actualizar_cuenta'))

    # Obtener los datos actuales del usuario
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM usuarios WHERE id = %s", (session['id'],))
    usuario = cur.fetchone()
    cur.close()

    return render_template('Cambiar_perfil.html', usuario=usuario)

# ---------------------------------------------------- Catalogo
@app.route('/Home_Catalogo')
def Home_Catalogo():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM product WHERE active = 1")
    products = cur.fetchall()
    cur.close()
    return render_template('home.html', products=products)

@app.route('/add_to_cart/<int:id>', methods=['POST'])
def add_to_cart(id):
    product_id = id

    # Verificar si 'cart' ya está en la sesión
    if 'cart' not in session:
        session['cart'] = {}

    # Verificar si el producto ya está en el carrito
    if str(product_id) in session['cart']:
        # Si el producto ya está en el carrito, aumentar la cantidad en 1
        session['cart'][str(product_id)] += 1
    else:
        # Si el producto no está en el carrito, agregarlo con cantidad 1
        session['cart'][str(product_id)] = 1

    # Mostrar un mensaje de éxito
    flash('Producto añadido al carrito exitosamente', 'success')

    # Redirigir de vuelta a la página de inicio
    return redirect(url_for('Home_Catalogo'))

@app.route('/cart')
def cart():
    if 'cart' not in session or len(session['cart']) == 0:
        flash('No hay productos en el carrito', 'info')
        return redirect(url_for('Home_Catalogo'))
    
    cart_items = []
    total_price = 0
    
    cur = mysql.connection.cursor()
    for product_id, quantity in session['cart'].items():
        cur.execute("SELECT * FROM product WHERE id = %s", (int(product_id),))
        product = cur.fetchone()
        if product:
            cart_items.append({'product': product, 'quantity': quantity})
            total_price += product['price'] * quantity
    cur.close()

    return render_template('cart.html', cart_items=cart_items, total_price=total_price)

@app.route('/remove_from_cart/<int:id>', methods=['POST'])
def remove_from_cart(id):
    product_id = id
    if 'cart' in session and str(product_id) in session['cart']:
        session['cart'].pop(str(product_id))
        flash('Producto removido del carrito exitosamente', 'success')
    else:
        flash('El producto no está en el carrito', 'danger')
    return redirect(url_for('cart'))

# ---------------------- crear productos

@app.route('/products', methods=['GET', 'POST'])
def create_product():
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        price = request.form.get('price')
        
        # Save the image on the server
        image = request.files['image']
        filename = secure_filename(image.filename)
        image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        image.save(image_path)

        # Create the product in the database
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO product (title, description, price, image_path) VALUES (%s, %s, %s, %s)", (title, description, price, image_path))
        mysql.connection.commit()
        cur.close()

        flash('Producto creado exitosamente', 'success')
        return redirect(url_for('Home_Catalogo'))
    return render_template('create_product.html')

# --------------------- borrar productos

@app.route('/products/delete/<int:id>', methods=['GET', 'POST'])
def delete_product(id):
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM product WHERE id = %s", (id,))
    mysql.connection.commit()
    cur.close()
    flash('Producto eliminado exitosamente', 'success')
    return redirect(url_for('Home_Catalogo'))

# ---------------------------- actualizar producto

@app.route('/products/update/<int:id>', methods=['GET', 'POST'])
def update_product(id):
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        price = request.form.get('price')
        image = request.files['image']
        if image:
            filename = secure_filename(image.filename)
            image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            image.save(image_path)
        else:
            cur = mysql.connection.cursor()
            cur.execute("SELECT image_path FROM product WHERE id = %s", (id,))
            image_path = cur.fetchone()['image_path']
            cur.close()

        # Update the product in the database
        cur = mysql.connection.cursor()
        cur.execute("UPDATE product SET title = %s, description = %s, price = %s, image_path = %s WHERE id = %s", (title, description, price, image_path, id))
        mysql.connection.commit()
        cur.close()

        flash('Producto actualizado exitosamente', 'success')
        return redirect(url_for('Home_Catalogo'))
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM product WHERE id = %s", (id,))
    product = cur.fetchone()
    cur.close()
    return render_template('update_product.html', product=product)

# ---------------------- boton de activar o descativar

@app.route('/products/activate/<int:id>', methods=['GET', 'POST'])
def activate_product(id):
    cur = mysql.connection.cursor()
    cur.execute("UPDATE product SET active = 1 WHERE id = %s", (id,))
    mysql.connection.commit()
    cur.close()
    flash('Producto activado exitosamente', 'success')
    return redirect(url_for('Home_Catalogo'))

@app.route('/products/deactivate/<int:id>', methods=['GET', 'POST'])
def deactivate_product(id):
    cur = mysql.connection.cursor()
    cur.execute("UPDATE product SET active = 0 WHERE id = %s", (id,))
    mysql.connection.commit()
    cur.close()
    flash('Producto desactivado exitosamente', 'success')
    return redirect(url_for('Home_Catalogo'))

# ------------ producto

@app.route('/product_actions')
def product_actions():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM product")
    products = cur.fetchall()
    cur.close()
    return render_template('product_actions.html', products=products)
    
if __name__ == "__main__":
    app.run(debug=True)
