from flask import Flask, render_template, request, url_for, flash, session, redirect
from flask_mysqldb import MySQL
from flask_mail import Mail, Message
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Configuración para MySQL
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'login'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

# Configuración para enviar correos
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'dilanyarce22@gmail.com'  
app.config['MAIL_PASSWORD'] = 'ppoj ltoy ryhq zrkg'  
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True

mail = Mail(app)

mysql = MySQL(app)

app.config['UPLOAD_FOLDER'] = 'static/img'

# Rutas y funciones para la primera aplicación
# Ruta para cuando se inicialice el programa se inicie desde el index.html
@app.route('/')
def home():
    return render_template("index.html")

@app.route('/Home_Catalogo')
def Home_Catalogo():
    return render_template('home.html')

@app.route('/products_action')
def products_action():
    return render_template('product_actions.html')

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
    return render_template("Registrar_Empleado.html", nombre=session.get('nombre'))

@app.route('/products', methods=['GET', 'POST'])
def create_product():
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        price = request.form.get('price')

        # Guardar la imagen en el servidor
        image = request.files['image']
        filename = secure_filename(image.filename)
        image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        image.save(image_path)

        # Construir la ruta completa de la imagen
        full_image_path = url_for('static', filename='uploads/' + filename)

        # Insertar los datos en la base de datos
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO product (title, description, price, image_path) VALUES (%s, %s, %s, %s)", 
                    (title, description, price, full_image_path)) 
        mysql.connection.commit()
        cur.close()

        flash('Producto creado exitosamente', 'success')
        return redirect(url_for('Home_Catalogo'))
    return render_template('create_product.html')

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

    cursor.close()

    return render_template("Citas.html", nombres_servicios=nombres_servicios, empleados_servicios=empleados_servicios, citas=citas, nombre=session.get('nombre'))

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
        return render_template("login.html")

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
        empleados_data = cur.fetchall()
        cur.close()
        return render_template("Registrar_Empleado.html", empleados=empleados_data, nombre=session.get('nombre'))

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

# Citas
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

@app.route('/forgot', methods=['GET', 'POST'])
def forgot():
    error = None
    if request.method == 'POST':
        user_email = request.form['txtCorreo']
            
        if is_email_registered(user_email):
            session['reset_email'] = user_email
            # Envía el correo electrónico con el enlace de restablecimiento de contraseña
            send_reset_email(user_email)
            flash('Se ha enviado el link para recuperar la contraseña a tu correo electrónico.', 'success')
            return redirect(url_for('login'))
        else:
            error = 'Correo no registrado. Por favor, inténtalo de nuevo o regístrate.'
    return render_template('forgot.html', error=error)

# Función para verificar si el correo electrónico está registrado en la base de datos
def is_email_registered(user_email):
    # Aquí debes implementar la lógica para verificar si el correo electrónico está registrado en tu base de datos
    return True  # Esto es solo un ejemplo, debes implementar tu propia lógica

# Función para enviar el correo electrónico con el enlace de restablecimiento de contraseña
def send_reset_email(user_email):
    token = generate_reset_token(user_email)
    reset_link = url_for('newpassword', token=token, _external=True)
    msg = Message('Recuperación de contraseña', sender='dilanyarce22@gmail.com', recipients=[user_email])
    msg.body = f'Para restablecer tu contraseña, haz clic en el siguiente enlace: {reset_link}'
    mail.send(msg)

# Genera un token único para el restablecimiento de contraseña
def generate_reset_token(user_email):
    # Aquí debes implementar la lógica para generar un token único
    return 'unique_token'  # Esto es solo un ejemplo, debes implementar tu propia lógica

# Ruta para restablecer la contraseña
@app.route('/newpassword/<token>', methods=['GET', 'POST'])
def newpassword(token):
    error = None
    if request.method == 'POST':
        if request.form['newpass'] != request.form['conpass']:
            error = 'Las contraseñas no coinciden..!!'
        else:
            user_email = session.get('reset_email')
            new_password = request.form['newpass']
            # Aquí debes implementar la lógica para actualizar la contraseña en tu base de datos
            session.pop('reset_email', None)
            flash('Contraseña restablecida exitosamente. Inicia sesión con tu nueva contraseña.', 'success')
            return redirect(url_for('login'))
    return render_template('newpassword.html', error=error)


if __name__ == "__main__":
    app.run(debug=True)
