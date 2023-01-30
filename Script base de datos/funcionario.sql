create table funcionario (
id int primary key not null auto_increment,
rut varchar(20) not null,
nombre varchar(20) not null,
apellido varchar(20) not null,
correo varchar(30) not null,
password longtext not null,
rol int not null
);