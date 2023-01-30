create table pedido (
id int primary key not null auto_increment,
estado int not null,
fecha date not null,
hora time not null,
neto int not null,
iva int not null,
bruto int not null,
observaciones varchar(50),
id_sucursal int not null,
id_cliente int not null
);