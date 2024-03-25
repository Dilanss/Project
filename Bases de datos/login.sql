CREATE DATABASE login;
USE login;

CREATE TABLE citas (
  id_cita int(11) NOT NULL PRIMARY KEY AUTO_INCREMENT,
  id_cliente int(11) NOT NULL,
  nombre varchar(100) NOT NULL,
  servicio varchar(100) NOT NULL,
  empleado int(11) NOT NULL,
  fecha date NOT NULL,
  hora time NOT NULL,
  motivo varchar(500) NOT NULL
) ;

INSERT INTO citas (id_cita, id_cliente, nombre, servicio, empleado, fecha, hora, motivo) VALUES
(1, 3, 'Lorena Hernandez', 'Corte de cabello', 2, '2024-03-23', '10:00:00', 'Corte de mantenimiento'),
(2, 4, 'Alejandro Martinez', 'Manicure', 2, '2024-03-24', '15:30:00', 'Arreglo de uñas'),
(3, 1, 'Wendy Huertas', 'Maquillaje', 1, '2024-03-25', '12:00:00', 'Maquillaje para evento');

CREATE TABLE entrada_productos (
  Id_Entrada int(11) NOT NULL PRIMARY KEY AUTO_INCREMENT,
  Id_Producto int(11) NOT NULL,
  Nombre varchar(100) NOT NULL,
  Cantidad int(11) NOT NULL,
  precio float NOT NULL,
  Fecha_Entrada date DEFAULT NULL
);

INSERT INTO entrada_productos (Id_Entrada, Id_Producto, Nombre, Cantidad, precio, Fecha_Entrada) VALUES
(1, 1, 'asd', 12, 1232, '2024-03-18'),
(2, 2, 'Uñas', 100, 1000, '2024-03-18'),
(3, 3, 'Dilan', 100, 100, '2024-03-18');

CREATE TABLE novedades (
    Id_Novedades int(11) NOT NULL PRIMARY KEY AUTO_INCREMENT,
    Id_Producto int(11) NOT NULL,
    fecha date NOT NULL,
    Nombre varchar(100) NOT NULL,
    Cantidad int(11) NOT NULL,
    Entrada int(11) NOT NULL,
    Salida int(11) NOT NULL,
    Tipo varchar(50) NOT NULL DEFAULT ''
);

INSERT INTO novedades (Id_Novedades, Id_Producto, fecha, Nombre, Cantidad, Entrada, Salida, Tipo) VALUES
(1, 1, '2024-03-18', 'asd', 12, 12, 0, 'Entrada'),
(2, 1, '2024-03-18', 'asd', 7, 0, 7, 'Salida'),
(3, 2, '2024-03-18', 'Uñas', 100, 100, 0, 'Entrada'),
(4, 2, '2024-03-18', 'Uñas', 50, 0, 50, 'Salida'),
(5, 2, '2024-03-18', 'Uñas', 25, 0, 25, 'Salida'),
(6, 3, '2024-03-18', 'Dilan', 100, 100, 0, 'Entrada'),
(7, 3, '2024-03-18', 'Dilan', 10, 0, 10, 'Salida');

CREATE TABLE productos (
  Id int(11) NOT NULL PRIMARY KEY AUTO_INCREMENT,
  Nombre varchar(100) NOT NULL,
  Cantidad int(11) NOT NULL,
  Marca varchar(200) NOT NULL,
  precio float NOT NULL,
  Descripcion varchar(500) NOT NULL,
  Fecha_vencimiento date DEFAULT NULL
);

INSERT INTO productos (Id, Nombre, Cantidad, Marca, precio, Descripcion, Fecha_vencimiento) VALUES
(3, 'Dilan', 90, 'esika', 1345, 'ad', '2024-03-20');

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

CREATE TABLE roles (
  id_rol int(11) NOT NULL PRIMARY KEY AUTO_INCREMENT,
  descripcion varchar(30) NOT NULL
);


INSERT INTO roles (id_rol, descripcion) VALUES
(1, 'Admin'),
(2, 'empleado'),
(3, 'cliente');

CREATE TABLE salida_productos (
  Id_Salida int(11) NOT NULL PRIMARY KEY AUTO_INCREMENT,
  Id_Producto int(11) NOT NULL,
  Nombre varchar(100) NOT NULL,
  Cantidad int(11) NOT NULL,
  precio float NOT NULL,
  Fecha_Salida date DEFAULT NULL
);

INSERT INTO salida_productos (Id_Salida, Id_Producto, Nombre, Cantidad, precio, Fecha_Salida) VALUES
(1, 1, 'asd', 5, 166, '2024-03-18'),
(2, 2, 'Uñas', 25, 123, '2024-03-18');

CREATE TABLE usuarios (
  id int(11) NOT NULL,
  correo varchar(100) NOT NULL,
  password varchar(100) NOT NULL,
  id_rol int(11) NOT NULL,
  nombre varchar(100) DEFAULT NULL,
  apellido varchar(100) DEFAULT NULL,
  telefono int(20) DEFAULT NULL
  num_citas int(11) DEFAULT 0
);

INSERT INTO usuarios (id, correo, password, id_rol, nombre, apellido, telefono, num_citas) VALUES
(1, 'wendyhuertas2408@gmail.com', '12', 1, 'Wendy', 'Huertas', 123123, 0),
(2, 'dilanjimenez208@gmail.com', '123', 2, 'Dilan', 'Jimenez', 234234, 0),
(3, 'wendy2408@outlook.es', '1234', 3, 'Lorena', 'Hernandez', 423423, 0),
(5, 'alejandro@gmail.com', '456', 3, 'Alejandro', 'Martinez', 2147483647, 0),
(6, 'alejandro@gmail.com', '456', 3, 'Alejandro', 'Martinez', 2147483647, 0),
(7, 'dilanjimenez200@gmail.com', '1234567', 1, 'Dilan', 'Jimenez', 123124, 0);

CREATE TABLE servicios (
  id_servicio int(11) NOT NULL,
  nombre varchar(100) NOT NULL,
  empleado int(11) NOT NULL
);

INSERT INTO servicios (id_servicio, nombre, empleado) VALUES
(1, 'Corte de cabello', 2),
(2, 'Manicure', 2),
(3, 'Maquillaje', 1);