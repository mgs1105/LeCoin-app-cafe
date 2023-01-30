create table cliente (
id int primary key not null auto_increment,
rut varchar(30) not null,
nombre varchar(20) not null,
apellido varchar(20) not null,
telefono int,
direccion varchar(30)
);