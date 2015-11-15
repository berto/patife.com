drop table if exists entries;
create table entries (
  id integer primary key auto_increment,
  title_en text not null,
  title_pt text not null,
  text_en text not null,
  text_pt text not null,
  date_created date not null,
  date_updated date not null,
  category_id integer
);
drop table if exists categories;
create table categories (
  id integer primary key auto_increment,
  title_en text not null,
  title_pt text not null,
  weight integer not null
);