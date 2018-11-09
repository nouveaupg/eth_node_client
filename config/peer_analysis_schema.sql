create table nodes
(
  node_id    smallint(5) unsigned auto_increment
    primary key,
  identifier varchar(55) null
);

create table peer_connections
(
  connection_id  int unsigned auto_increment
    primary key,
  enode          varchar(255)         null,
  id             char(64)             null,
  remote_address varchar(36)          null,
  caps           json                 null,
  node_id        smallint(5) unsigned null,
  captured       datetime             null
);

create index peer_connections_node_id_index
  on peer_connections (node_id);