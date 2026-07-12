-- PostgreSQL extensions and schema for Property Service
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "postgis";
CREATE SCHEMA IF NOT EXISTS property;
SET search_path TO property, public;
