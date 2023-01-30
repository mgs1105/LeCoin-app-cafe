create table producto (
id int primary key not null auto_increment,
sku varchar(20) not null,
nombre varchar(20) not null,
precio int not null,
cantidad_tienda int not null,
cantidad_bodega int not null,
descripcion varchar(30),
imagen longtext,
categoria int not null
);