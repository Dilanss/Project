CREATE DATABASE AngieStudio;
use AngieStudio;


CREATE TABLE cart_item (
  id int(11) NOT NULL PRIMARY KEY AUTO_INCREMENT,
  product_id int(11) NOT NULL,
  quantity int(11) NOT NULL
) ;

CREATE TABLE citas (
  id_cita int(11) NOT NULL PRIMARY KEY AUTO_INCREMENT,
  id_cliente int(11) NOT NULL,
  nombre varchar(100) NOT NULL,
  servicio varchar(100) NOT NULL,
  empleado_nombre varchar(100) NOT NULL,
  fecha date NOT NULL,
  hora time NOT NULL,
  motivo varchar(500) NOT NULL
) ;

--
-- Volcado de datos para la tabla citas
--

INSERT INTO citas (id_cita, id_cliente, nombre, servicio, empleado_nombre, fecha, hora, motivo) VALUES
(2, 4, 'Alejandro Martinez', 'Manicure', '2', '2024-03-24', '15:30:00', 'Arreglo de uñas'),
(7, 5, 'Alejandro', 'Corte de cabello', 'Yusep', '2024-02-29', '09:58:00', 'asd'),
(15, 3, 'zasd', 'Manicure', 'Yusep', '2024-03-20', '19:51:00', 'asd'),
(16, 3, 'asd', 'Corte de cabello', 'Dilan', '2024-03-27', '19:57:00', 'asd'),
(22, 15, 'Dilan', 'Corte de cabello', 'Yusep', '2024-03-13', '20:22:00', 'Degradado'),
(23, 15, 'asdasd', 'Manicure', 'Dilan', '2024-02-27', '20:23:00', 'asd'),
(26, 15, 'Dilan Jiomenez', 'Corte de cabello', 'Dilan', '2024-03-18', '04:07:00', 'asd');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla entrada_productos
--

CREATE TABLE entrada_productos (
  Id_Entrada int(11) NOT NULL PRIMARY KEY AUTO_INCREMENT,
  Id_Producto int(11) NOT NULL,
  Nombre varchar(100) NOT NULL,
  Cantidad int(11) NOT NULL,
  precio float NOT NULL,
  Fecha_Entrada date DEFAULT NULL
) ;

--
-- Volcado de datos para la tabla entrada_productos
--

INSERT INTO entrada_productos (Id_Entrada, Id_Producto, Nombre, Cantidad, precio, Fecha_Entrada) VALUES
(1, 1, 'asd', 12, 1232, '2024-03-18'),
(2, 2, 'Uñas', 100, 1000, '2024-03-18'),
(3, 3, 'Dilan', 100, 100, '2024-03-18'),
(4, 4, 'Uñas', 100, 10000, '2024-03-25');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla novedades
--

CREATE TABLE novedades (
  Id_Novedades int(11) NOT NULL PRIMARY KEY AUTO_INCREMENT,
  Id_Producto int(11) NOT NULL,
  fecha date NOT NULL,
  Nombre varchar(100) NOT NULL,
  Precio decimal(10,2) NOT NULL,
  Cantidad int(11) NOT NULL,
  Entrada int(11) NOT NULL,
  Salida int(11) NOT NULL,
  Tipo varchar(50) NOT NULL DEFAULT ''
) ;

--
-- Volcado de datos para la tabla novedades
--

INSERT INTO novedades (Id_Novedades, Id_Producto, fecha, Nombre, Precio, Cantidad, Entrada, Salida, Tipo) VALUES
(1, 1, '2024-03-18', 'asd', 0.00, 12, 12, 0, 'Entrada'),
(2, 1, '2024-03-18', 'asd', 0.00, 7, 0, 7, 'Salida'),
(3, 2, '2024-03-18', 'Uñas', 0.00, 100, 100, 0, 'Entrada'),
(4, 2, '2024-03-18', 'Uñas', 0.00, 50, 0, 50, 'Salida'),
(5, 2, '2024-03-18', 'Uñas', 0.00, 25, 0, 25, 'Salida'),
(6, 3, '2024-03-18', 'Dilan', 0.00, 100, 100, 0, 'Entrada'),
(7, 3, '2024-03-18', 'Dilan', 0.00, 10, 0, 10, 'Salida'),
(8, 4, '2024-03-25', 'Uñas', 0.00, 100, 100, 0, 'Entrada'),
(9, 4, '2024-03-25', 'Uñas', 0.00, 10, 0, 10, 'Salida'),
(10, 4, '2024-03-25', 'Uñas', 0.00, 40, 0, 40, 'Salida');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla product
--

CREATE TABLE product (
  id int(11) NOT NULL PRIMARY KEY AUTO_INCREMENT,
  title varchar(80) NOT NULL,
  description text NOT NULL,
  price float NOT NULL,
  image_path varchar(255) NOT NULL,
  active tinyint(1) NOT NULL DEFAULT 1
) ;

--
-- Volcado de datos para la tabla product
--

INSERT INTO product (id, title, description, price, image_path, active) VALUES
(3, 'maquillaje', 'polvos para bellezas como tu bebe', 24000, 'static/img\\pexels-jhong-pascua-3018845.jpg', 1),
(4, 'polvos', 'cremas', 25000, 'static/img\\pexels-harper-sunday-2866796.jpg', 1),
(5, 'cremas', 'en polvo', 5500, 'static/img\\imagen_noticia_Ballerina_28_10_2020.png', 1),
(6, 'asdasdsadasdas', 'asdasd', 154645, 'pexels-harper-sunday-2866796.jpg', 1);

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla productos
--

CREATE TABLE productos (
  Id int(11) NOT NULL PRIMARY KEY AUTO_INCREMENT,
  Nombre varchar(100) NOT NULL,
  Cantidad int(11) NOT NULL,
  Marca varchar(200) NOT NULL,
  precio float NOT NULL,
  Descripcion varchar(500) NOT NULL,
  Fecha_vencimiento date DEFAULT NULL
) ;

--
-- Volcado de datos para la tabla productos
--

INSERT INTO productos (Id, Nombre, Cantidad, Marca, precio, Descripcion, Fecha_vencimiento) VALUES
(4, 'Uñas', 50, 'esika', 10000, 'saasd', '2024-03-21');

--
-- Disparadores productos
--
DELIMITER $$
CREATE TRIGGER after_delete_producto AFTER DELETE ON productos FOR EACH ROW BEGIN
    INSERT INTO salida_productos (Id_Producto, Nombre, Cantidad, precio, Fecha_Salida)
    VALUES (OLD.Id, OLD.Nombre, OLD.Cantidad, OLD.precio, NOW());
END
$$
DELIMITER ;
DELIMITER $$
CREATE TRIGGER after_insert_producto AFTER INSERT ON productos FOR EACH ROW BEGIN
    INSERT INTO entrada_productos (Id_Producto, Nombre, Cantidad, precio, Fecha_Entrada)
    VALUES (NEW.Id, NEW.Nombre, NEW.Cantidad, NEW.precio, NOW());

    INSERT INTO Novedades (Id_Producto, fecha, Nombre, Cantidad, Entrada, Salida, Tipo)
    VALUES (NEW.Id, NOW(), NEW.Nombre, NEW.Cantidad, NEW.Cantidad, 0, 'Entrada');
END
$$
DELIMITER ;
DELIMITER $$
CREATE TRIGGER after_update_producto AFTER UPDATE ON productos FOR EACH ROW BEGIN
    DECLARE cantidad_anterior INT;
    DECLARE diferencia_cantidad INT;
    
    SET cantidad_anterior = OLD.Cantidad;
    SET diferencia_cantidad = NEW.Cantidad - cantidad_anterior;

    IF diferencia_cantidad < 0 THEN
        INSERT INTO Novedades (Id_Producto, fecha, Nombre, Cantidad, Entrada, Salida, Tipo)
        VALUES (NEW.Id, NOW(), NEW.Nombre, ABS(diferencia_cantidad), 0, ABS(diferencia_cantidad), 'Salida');
    END IF;
END
$$
DELIMITER ;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla roles
--

CREATE TABLE roles (
  id_rol int(11) NOT NULL PRIMARY KEY AUTO_INCREMENT,
  descripcion varchar(30) NOT NULL
) ;

--
-- Volcado de datos para la tabla roles
--

INSERT INTO roles (id_rol, descripcion) VALUES
(1, 'Admin'),
(2, 'empleado'),
(3, 'cliente');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla salida_productos
--

CREATE TABLE salida_productos (
  Id_Salida int(11) NOT NULL PRIMARY KEY AUTO_INCREMENT,
  Id_Producto int(11) NOT NULL,
  Nombre varchar(100) NOT NULL,
  Cantidad int(11) NOT NULL,
  precio float NOT NULL,
  Fecha_Salida date DEFAULT NULL
) ;

--
-- Volcado de datos para la tabla salida_productos
--

INSERT INTO salida_productos (Id_Salida, Id_Producto, Nombre, Cantidad, precio, Fecha_Salida) VALUES
(1, 1, 'asd', 5, 166, '2024-03-18'),
(2, 2, 'Uñas', 25, 123, '2024-03-18'),
(3, 3, 'Dilan', 90, 123, '2024-03-25');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla servicios
--

CREATE TABLE servicios (
  id_servicio int(11) NOT NULL PRIMARY KEY AUTO_INCREMENT,
  nombre varchar(100) NOT NULL,
  empleado varchar(100) NOT NULL
) ;

--
-- Volcado de datos para la tabla servicios
--

INSERT INTO servicios (id_servicio, nombre, empleado) VALUES
(1, 'Corte de cabello', '2'),
(2, 'Manicure', '2'),
(3, 'Maquillaje', '1'),
(8, 'Queratina', 'Dilan');



CREATE TABLE usuarios (
  id int(11) NOT NULL PRIMARY KEY AUTO_INCREMENT,
  correo varchar(100) NOT NULL,
  password varchar(100) NOT NULL,
  id_rol int(11) NOT NULL,
  nombre varchar(100) DEFAULT NULL,
  apellido varchar(100) DEFAULT NULL,
  telefono int(20) DEFAULT NULL,
  num_citas int(11) DEFAULT 0
) ;



INSERT INTO usuarios (id, correo, password, id_rol, nombre, apellido, telefono, num_citas) VALUES
(1, 'wendyhuertas2408@gmail.com', '12', 1, 'Wendy', 'Huertas', 123123, 0),
(2, 'dilanjimenez208@gmail.com', 'Dilan1', 2, 'Dilan', 'Jimenez', 234234, 0),
(3, 'wendy2408@outlook.es', '1234', 3, 'Lorena', 'Hernandez', 423423, 0),
(5, 'alejandro@gmail.com', '456', 3, 'Alejandro', 'Martinez', 2147483647, 0),
(6, 'alejandro@gmail.com', '456', 3, 'Alejandro', 'Martinez', 2147483647, 0),
(7, 'dilanjimenez200@gmail.com', '1234567', 1, 'Dilan', 'Jimenez', 123124, 0),
(8, 'Yusep@gmail.com', '123', 2, 'Yusep', 'Yarce', 123123, 0),
(15, 'dilanjimenez208@gmail.com', 'Dilan1', 3, 'Dilan Yusep', 'Jimenez Yarce', 1231, 0),
(16, 'dronlext@gmail.com', 'Oscar1', 3, 'Oscar', 'Sanabria', 312312, 0);


ALTER TABLE cart_item
  ADD CONSTRAINT fk_cart_item_product FOREIGN KEY (product_id) REFERENCES product (id) ON DELETE CASCADE;



