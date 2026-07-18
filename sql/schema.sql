--
-- PostgreSQL database dump
--

\restrict LDvCPIkvyuZGC8R4j4VgzET5T8QvU8E8gEmdoM9i0YZauzkykDItnSxbtTOx9B5

-- Dumped from database version 18.0
-- Dumped by pg_dump version 18.0

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: sales; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.sales (
    invoiceno character varying(20),
    stockcode character varying(20),
    description text,
    quantity integer,
    invoicedate timestamp without time zone,
    unitprice numeric(10,2),
    customerid integer,
    country character varying(100),
    totalprice numeric(12,2)
);


ALTER TABLE public.sales OWNER TO postgres;

--
-- PostgreSQL database dump complete
--

\unrestrict LDvCPIkvyuZGC8R4j4VgzET5T8QvU8E8gEmdoM9i0YZauzkykDItnSxbtTOx9B5

