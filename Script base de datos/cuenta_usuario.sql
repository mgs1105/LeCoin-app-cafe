create table cuenta_usuario (
id int primary key not null auto_increment,
nombre_usuario varchar(20) not null,
correo varchar(30) not null,
password longtext not null
);