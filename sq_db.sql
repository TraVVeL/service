CREATE TABLE IF NOT EXISTS mainmenu (
id integer PRIMARY KEY AUTOINCREMENT,
title text NOT NULL,
url text NOT NULL
);

CREATE TABLE IF NOT EXISTS posts (
id integer PRIMARY KEY AUTOINCREMENT,
title text NOT NULL,
text text NOT NULL,
url text NOT NULL,
time integer NOT NULL
);

CREATE TABLE IF NOT EXISTS users (
id integer PRIMARY KEY AUTOINCREMENT,
name text NOT NULL,
email text NOT NULL,
password text NOT NULL,
cash float NOT NULL,
cart text NOT NULL,
time integer NOT NULL
);

CREATE TABLE IF NOT EXISTS products (
id integer PRIMARY KEY AUTOINCREMENT,

name text NOT NULL,
description text NOT NULL,
quick_describe text NOT NULL,
weight text NOT NULL,
amount text NOT NULL,
price text NOT NULL,
url text NOT NULL,
imgname text NOT NULL,
time integer NOT NULL
);

CREATE TABLE IF NOT EXISTS contact (
id integer PRIMARY KEY AUTOINCREMENT,
phone text NOT NULL,
mail text NOT NULL,
message text NOT NULL,
name text NOT NULL,
surname text NOT NULL,
color text NOT NULL,
price text NOT NULL,
viewed text NOT NULL,
time integer NOT NULL
);

CREATE TABLE IF NOT EXISTS user_information (
id integer PRIMARY KEY AUTOINCREMENT,
name text NOT NULL,
phone text NOT NULL,
mail text NOT NULL,
secondary_name text NOT NULL,
secondary_phone text NOT NULL,
city text NOT NULL,
street text NOT NULL,
building_address text NOT NULL,
entrance text NOT NULL,
floor text NOT NULL,
apartment text NOT NULL,
deliver text NOT NULL,
deliver_time text NOT NULL,
note text NOT NULL,
delivered text NOT NULL,
user_id text NOT NULL,
time integer NOT NULL
);

CREATE TABLE IF NOT EXISTS product_purchase (
id integer PRIMARY KEY AUTOINCREMENT,
user_id text NOT NULL,
product_name text NOT NULL,
product_id text NOT NULL,
product_count text NOT NULL,
final_cost text NOT NULL,
product_price text NOT NULL,
product_url text NOT NULL,
product_img text NOT NULL,
time integer NOT NULL
);