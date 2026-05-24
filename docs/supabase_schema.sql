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

alter table categorias_nubank enable row level security;
alter table contas_casa enable row level security;
alter table entradas enable row level security;
alter table contas_banco_manuais enable row level security;
alter table dizimo_mensal enable row level security;
alter table nubank_lancamentos enable row level security;

drop policy if exists "allow app all categorias_nubank" on categorias_nubank;
drop policy if exists "allow app all contas_casa" on contas_casa;
drop policy if exists "allow app all entradas" on entradas;
drop policy if exists "allow app all contas_banco_manuais" on contas_banco_manuais;
drop policy if exists "allow app all dizimo_mensal" on dizimo_mensal;
drop policy if exists "allow app all nubank_lancamentos" on nubank_lancamentos;

create policy "allow app all categorias_nubank"
on categorias_nubank
for all
to anon
using (true)
with check (true);

create policy "allow app all contas_casa"
on contas_casa
for all
to anon
using (true)
with check (true);

create policy "allow app all entradas"
on entradas
for all
to anon
using (true)
with check (true);

create policy "allow app all contas_banco_manuais"
on contas_banco_manuais
for all
to anon
using (true)
with check (true);

create policy "allow app all dizimo_mensal"
on dizimo_mensal
for all
to anon
using (true)
with check (true);

create policy "allow app all nubank_lancamentos"
on nubank_lancamentos
for all
to anon
using (true)
with check (true);
