CREATE SCHEMA IF NOT EXISTS content;

CREATE TYPE tv_type AS ENUM ('movie', 'tv_show');

CREATE TYPE role_type AS ENUM ('actor', 'writer', 'director');

CREATE TABLE IF NOT EXISTS content.film_work(
    id uuid DEFAULT gen_random_uuid() PRIMARY KEY,
    title VARCHAR NOT NULL,
    description TEXT,
    creation_date DATE,
    rating float,
    type tv_type NOT NULL,
    created_at timestamp with time zone,
    updated_at timestamp with time zone
);

CREATE TABLE IF NOT EXISTS content.genre(
    id uuid DEFAULT gen_random_uuid() PRIMARY KEY,
    name VARCHAR NOT NULL,
    description TEXT,
    created_at timestamp with time zone,
    updated_at timestamp with time zone
);

CREATE TABLE IF NOT EXISTS content.genre_film_work(
    id uuid DEFAULT gen_random_uuid() PRIMARY KEY,
    film_work_id uuid NOT NULL,
    genre_id uuid NOT NULL,
    created_at timestamp with time zone
);

CREATE TABLE IF NOT EXISTS content.person(
    id uuid DEFAULT gen_random_uuid() PRIMARY KEY,
    full_name VARCHAR NOT NULL,
    created_at timestamp with time zone,
    updated_at timestamp with time zone
);

CREATE TABLE IF NOT EXISTS content.person_film_work(
    id uuid DEFAULT gen_random_uuid() PRIMARY KEY,
    film_work_id uuid NOT NULL,
    person_id uuid NOT NULL,
    role role_type NOT NULL,
    created_at timestamp with time zone
);

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

CREATE INDEX IF NOT EXISTS film_work_creation_date_idx ON content.film_work(creation_date);

CREATE UNIQUE INDEX IF NOT EXISTS genre_name_idx ON content.genre(name);

CREATE INDEX IF NOT EXISTS person_full_name_idx ON content.person(full_name);

CREATE UNIQUE INDEX IF NOT EXISTS film_work_genre_idx ON content.genre_film_work(film_work_id, genre_id);

CREATE UNIQUE INDEX IF NOT EXISTS film_work_person_idx ON content.person_film_work(film_work_id, person_id, role);
