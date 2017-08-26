drop table if exists tasks;
create table tasks (
  task_id integer primary key autoincrement,
  user_id string not null,
  end_date date not null,
  item string not null,
  status integer default 0 not null,
  create_record_date date default current_timestamp,
  update_record_date date
);
drop table if exists users;
create table users (
  user_id string primary key,
  password string not null
);
