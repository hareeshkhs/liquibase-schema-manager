--liquibase formatted sql

--changeset chhareeshkumar:1602251613-01 splitStatements:false
CREATE SCHEMA IF NOT EXISTS merchant_template;

--changeset chhareeshkumar:1602251613-02 splitStatements:false
CREATE TABLE merchant_template.table_template (
  ID INT PRIMARY KEY,
  NAME VARCHAR(100)
);

