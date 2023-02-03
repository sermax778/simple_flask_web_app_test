CREATE TABLE IF NOT EXISTS items(
id integer PRIMARY KEY AUTOINCREMENT,
title tinytext NOT NULL,
price double NOT NULL,
description text NOT NULL,
image_url text,
isActive integer NOT NULL,
time integer NOT NULL
);


CREATE TABLE IF NOT EXISTS users(
id integer PRIMARY KEY AUTOINCREMENT,
login text NOT NULL,
email text NOT NULL,
password text NOT NULL,
time integer NOT NULL
);