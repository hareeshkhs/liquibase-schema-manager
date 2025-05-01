--liquibase formatted sql

--changeset chhareeshkumar:1602251613-01 splitStatements:false
CREATE SCHEMA IF NOT EXISTS core;

--changeset chhareeshkumar:1602251613-02 splitStatements:false
CREATE TABLE core.table_core (
  ID INT PRIMARY KEY,
  NAME VARCHAR(100),
  DOB DATE
);


