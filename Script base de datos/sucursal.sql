create table sucursal (
id int primary key not null auto_increment,
razon_social varchar(100) not null,
giro varchar(100) not null,
nombre varchar(30) not null,
rut varchar(30) not null,
telefono int,
direccion varchar(30) not null,
correo varchar(30) not null
);