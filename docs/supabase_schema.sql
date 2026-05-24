create table if not exists categorias_nubank (
  categoria text not null,
  subcategoria text not null
);

create table if not exists contas_casa (
  id integer primary key,
  "NUMANOMES" text not null,
  descricao text not null,
  valor numeric not null default 0,
  status text not null default 'Pendente'
);

create table if not exists entradas (
  id integer primary key,
  "NUMANOMES" text not null,
  descricao text not null,
  valor numeric not null default 0,
  status text not null default 'Previsto'
);

create table if not exists contas_banco_manuais (
  id integer primary key,
  data_compra text not null,
  descricao text not null,
  valor numeric not null default 0,
  origem text not null default 'manual',
  "NUMANOMES" text not null,
  banco text not null,
  categoria text default '',
  subcategoria text default ''
);

create table if not exists dizimo_mensal (
  id integer primary key,
  "NUMANOMES" text not null,
  salario_bruno numeric not null default 0,
  dizimo_bruno numeric not null default 0,
  salario_mayara numeric not null default 0,
  dizimo_mayara numeric not null default 0,
  total_dizimo numeric not null default 0,
  status text not null default 'Pendente'
);

create table if not exists nubank_lancamentos (
  data_compra text not null,
  descricao text not null,
  valor numeric not null default 0,
  origem text not null,
  "NUMANOMES" text not null,
  banco text not null,
  categoria text default '',
  subcategoria text default ''
);

