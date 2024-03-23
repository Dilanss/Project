from flask import Flask, render_template, request, url_for, flash, session, redirect
from flask_mysqldb import MySQL

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Configuración para MySQL
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'login'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'


mysql = MySQL(app)

# Rutas y funciones para la primera aplicación

# Ruta para cuando se inicialice el programa se inicie desde el index.html
@app.route('/')
def home():
    return render_template("index.html")

# Funcion para redirigir al Administrador.html
@app.route('/admin')
def admin():
    return render_template("Administrador.html")

# Redireccion al template del empleado
@app.route('/Empleado')
def Empleado():
    return render_template("Empleado.html")

# Redireccion al template de cliente
@app.route('/Cliente')
def Cliente():
    return render_template("Cliente.html")

# Redireccion al template de registrar empleado
@app.route('/Redirigir_Empleado')
def Redirigir_Empleado():
    return render_template("Registrar_Empleado.html")

#Redirigir al template de Citas.html
@app.route('/Citas')
def Citas():
    return render_template("Citas.html")

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

# Funcion de olvidar contraseña
@app.route('/forgot', methods=['GET', 'POST'])
def forgot():
    error = None
    if request.method == 'POST':
        user_email = request.form['txtCorreo']

        if is_email_registered(user_email):
            session['reset_email'] = user_email
            return redirect(url_for('newpassword'))
        else:
            error = 'Correo no registrado. Por favor, inténtalo de nuevo o regístrate.'
    return render_template('forgot.html', error=error)

# Funcion para redirigir al olvidar contraseña
@app.route('/logout')
def logout():
    session.clear()  
    return redirect(url_for('home'))  

def is_email_registered(correo):
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM usuarios WHERE correo = %s", (correo,))
    account = cur.fetchone()
    cur.close()
    if account:
        return True
    else:
        return False

# Funcion para el template de la nueva contraseña 
@app.route('/newpassword', methods=['GET', 'POST'])
def newpassword():
    error = None
    if request.method == 'POST':
        if request.form['newpass'] != request.form['conpass']:
            error = 'Las contraseñas no coinciden..!!'
        else:
            user_email = session.get('reset_email')
            new_password = request.form['newpass']
            cur = mysql.connection.cursor()
            cur.execute("UPDATE usuarios SET password = %s WHERE correo = %s", (new_password, user_email))
            mysql.connection.commit()
            cur.close()
            session.pop('reset_email', None)
            return redirect(url_for('home'))
    return render_template('newpassword.html', error=error)

# Funcion para redirigir al registro.html
@app.route('/registro')
def registro():
    return render_template("registro.html")

# Funcion para crear el registro desde el template del registro
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

# Funcion para crear Empleados
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
        return redirect(url_for('Redirigir_Empleado'))  
    return render_template("Registrar_Empleado.html")

# Funcion para mostrar datos de todos los empleado en en Registrar_Empleado.html:
@app.route('/ver_empleados')
def ver_empleados():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM usuarios WHERE id_rol = 2")
    empleados_data = cur.fetchall()
    cur.close()
    return render_template("Registrar_Empleado.html", empleados=empleados_data)

# Rutas y funciones para (Inventario)
# Funcion del inventario para seleccionar los productos y los campos
@app.route('/inventario')
def inventario():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM productos")
    productos_data = cur.fetchall()
    cur.close()
    return render_template('inventario.html', productos=productos_data)

# Funcion para insertar un nuevo producto
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
        return redirect(url_for('inventario'))

# Funcion de eliminar el producto
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
    return redirect(url_for('Redirigir_Empleado'))

# Funcion para actualizar un producto
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
            return redirect(url_for('inventario'))
        except Exception as e:
            flash(f"Error al actualizar: {str(e)}")
        finally:
            cur.close()
    return render_template('inventario.html')

# Update_Empleado Funcion para editar al empleado
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
            return redirect(url_for('inventario'))
        except Exception as e:
            flash(f"Error al actualizar al empleado: {str(e)}")
        finally:
            cur.close()
    return render_template('Redirigir_Empleado')

# Funcion del inventario para registrar las entradas
@app.route('/Entradas')
def Entradas():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM entrada_productos")
    entradas_data = cur.fetchall()
    cur.close()
    return render_template('Entradas.html', entradas_data=entradas_data)  

# Funcion para redirigir al template de Entradas.html
@app.route('/redireccionar_a_entradas')
def redireccionar_a_entradas():
    # Redireccionar a la página de Entradas.html
    return redirect(url_for('Entradas'))

# Funcion para registrar las salidas de los productos
@app.route('/Salidas')
def Salidas():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM salida_productos")
    salidas_data = cur.fetchall()
    cur.close()
    return render_template('Salidas.html', salidas=salidas_data)

# Funcion para registrar las novedades de los productos
# Funcion para mostrar las novedades de entrada
@app.route('/Novedades')
def Novedades():
    cur = mysql.connection.cursor()
    cur.execute("SELECT n.*, p.Cantidad AS Cantidad_Actual FROM Novedades n JOIN productos p ON n.Id_Producto = p.Id WHERE n.Tipo = 'Entrada'")
    entradas_data = cur.fetchall()

    cur.execute("SELECT * FROM Novedades WHERE Tipo = 'Salida'")
    salidas_data = cur.fetchall()

    cur.close()
    
    return render_template('Novedades.html', entradas=entradas_data, salidas=salidas_data)

# Citas
@app.route('/Registrar_Cita', methods=["GET", "POST"])
def Registrar_Cita():
    cur = mysql.connection.cursor()
    cur.execute("SELECT nombre FROM servicios")
    servicios_data = [row[0] for row in cur.fetchall()]
    cur.close()
    
    if request.method == "POST":
        nombre = request.form.get('nombre')
        servicio = request.form.get('servicio')
        empleado = request.form.get('Empleado')
        fecha = request.form.get('Fecha')
        hora = request.form.get('Hora')
        motivo = request.form.get('motivo')
        
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO citas (nombre, servicio, empleado, fecha, hora, motivo) VALUES (%s, %s, %s, %s, %s, %s)",
                    (nombre, servicio, empleado, fecha, hora, motivo))
        mysql.connection.commit()
        cur.close()
        

        return redirect(url_for('Citas'))
    

    return render_template("Citas.html", servicios_data=servicios_data)

if __name__ == "__main__":
    app.run(debug=True)
