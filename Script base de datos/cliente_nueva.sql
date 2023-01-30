create table cliente(
id int primary key auto_increment not null,
nombre varchar(20) not null,
apellido varchar(20) not null,
rut varchar(20) not null,
telefono int not null,
direccion varchar(30),
correo varchar(30) not null,
password longtext not null
);