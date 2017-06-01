CREATE DATABASE cloudbox WITH OWNER = postgres ENCODING = 'UTF8' LC_COLLATE = 'en_US.utf8' LC_CTYPE = 'en_US.utf8' TABLESPACE = pg_default CONNECTION LIMIT = -1;

CREATE SCHEMA iot AUTHORIZATION postgres;

CREATE SEQUENCE iot.box_info_id_seq INCREMENT 1 START 1 MINVALUE 1 MAXVALUE 9223372036854775807 CACHE 1;
ALTER SEQUENCE iot.box_info_id_seq OWNER TO postgres;

CREATE SEQUENCE iot.box_type_info_id_seq INCREMENT 1 START 1 MINVALUE 1 MAXVALUE 9223372036854775807 CACHE 1;
ALTER SEQUENCE iot.box_type_info_id_seq OWNER TO postgres;

CREATE SEQUENCE iot.carrier_info_id_seq INCREMENT 1 START 1 MINVALUE 1 MAXVALUE 9223372036854775807 CACHE 1;
ALTER SEQUENCE iot.carrier_info_id_seq OWNER TO postgres;

CREATE SEQUENCE iot.sensor_data_id_seq INCREMENT 1 START 1 MINVALUE 1 MAXVALUE 9223372036854775807 CACHE 1;
ALTER SEQUENCE iot.sensor_data_id_seq OWNER TO postgres;

CREATE SEQUENCE iot."box_order_relation_id _seq" INCREMENT 1 START 1 MINVALUE 1 MAXVALUE 9223372036854775807 CACHE 1;
ALTER SEQUENCE iot."box_order_relation_id _seq" OWNER TO postgres;

CREATE SEQUENCE iot.order_info_id_seq INCREMENT 1 START 1 MINVALUE 1 MAXVALUE 9223372036854775807 CACHE 1;
ALTER SEQUENCE iot.order_info_id_seq OWNER TO postgres;

CREATE SEQUENCE iot.site_info_id_seq INCREMENT 1 START 1 MINVALUE 1 MAXVALUE 9223372036854775807 CACHE 1;
ALTER SEQUENCE iot.site_info_id_seq OWNER TO postgres;

CREATE SEQUENCE iot."alert_level_info_seq" INCREMENT 1 START 1 MINVALUE 1 MAXVALUE 9223372036854775807 CACHE 1;
ALTER SEQUENCE iot."alert_level_info_seq" OWNER TO postgres;

CREATE SEQUENCE iot."alert_type_info_seq" INCREMENT 1 START 1 MINVALUE 1 MAXVALUE 9223372036854775807 CACHE 1;
ALTER SEQUENCE iot."alert_type_info_seq" OWNER TO postgres;

CREATE SEQUENCE iot."alert_code_info_seq" INCREMENT 1 START 1 MINVALUE 1 MAXVALUE 9223372036854775807 CACHE 1;
ALTER SEQUENCE iot."alert_code_info_seq" OWNER TO postgres;

CREATE SEQUENCE iot."battery_info_seq" INCREMENT 1 START 1 MINVALUE 1 MAXVALUE 9223372036854775807 CACHE 1;
ALTER SEQUENCE iot."battery_info_seq" OWNER TO postgres;

CREATE SEQUENCE iot."maintenance_info_seq" INCREMENT 1 START 1 MINVALUE 1 MAXVALUE 9223372036854775807 CACHE 1;
ALTER SEQUENCE iot."maintenance_info_seq" OWNER TO postgres;

CREATE SEQUENCE iot."interval_time_info_seq" INCREMENT 1 START 1 MINVALUE 1 MAXVALUE 9223372036854775807 CACHE 1;
ALTER SEQUENCE iot."interval_time_info_seq" OWNER TO postgres;

CREATE SEQUENCE iot."hardware_info_seq" INCREMENT 1 START 1 MINVALUE 1 MAXVALUE 9223372036854775807 CACHE 1;
ALTER SEQUENCE iot."hardware_info_seq" OWNER TO postgres;

CREATE SEQUENCE iot.manufacturer_info_id_seq INCREMENT 1 START 3 MINVALUE 1 MAXVALUE 9223372036854775807 CACHE 1;
ALTER SEQUENCE iot.manufacturer_info_id_seq OWNER TO postgres;

CREATE SEQUENCE iot.produce_area_info_id_seq INCREMENT 1 START 3 MINVALUE 1 MAXVALUE 9223372036854775807 CACHE 1;
ALTER SEQUENCE iot.produce_area_info_id_seq OWNER TO postgres;


CREATE TABLE iot.box_info
(
    id integer NOT NULL DEFAULT nextval('iot.box_info_id_seq'::regclass),
    deviceid text COLLATE pg_catalog."default",
    type integer,
    date_of_production text COLLATE pg_catalog."default",
    manufacturer integer,
    produce_area integer,
    hardware integer,
    battery integer,
    carrier integer

)
WITH (
    OIDS = FALSE
)
TABLESPACE pg_default;

ALTER TABLE iot.box_info OWNER to postgres;


CREATE TABLE iot.box_type_info
(
    id integer NOT NULL DEFAULT nextval('iot.box_type_info_id_seq'::regclass),
    box_type_name text COLLATE pg_catalog."default",
    box_type_detail text COLLATE pg_catalog."default",
    interval_time INTEGER,
    temperature_threshold_min INTEGER,
    temperature_threshold_max INTEGER,
    humidity_threshold_min INTEGER,
    humidity_threshold_max INTEGER,
    collision_threshold_min INTEGER,
    collision_threshold_max INTEGER,
    battery_threshold_min INTEGER,
    battery_threshold_max INTEGER,
    operation_threshold_max INTEGER,
    operation_threshold_min INTEGER
)
WITH (
    OIDS = FALSE
)
TABLESPACE pg_default;

ALTER TABLE iot.box_type_info OWNER to postgres;


CREATE TABLE iot.carrier_info
(
    id integer NOT NULL DEFAULT nextval('iot.carrier_info_id_seq'::regclass),
    carrier_name text COLLATE pg_catalog."default"
)
WITH (
    OIDS = FALSE
)
TABLESPACE pg_default;

ALTER TABLE iot.carrier_info OWNER to postgres;


CREATE TABLE iot.sensor_data
(
    id integer NOT NULL DEFAULT nextval('iot.sensor_data_id_seq'::regclass),
    "timestamp" integer,
    deviceid text COLLATE pg_catalog."default",
    temperature text COLLATE pg_catalog."default",
    humidity text COLLATE pg_catalog."default",
    longitude text COLLATE pg_catalog."default",
    latitude text COLLATE pg_catalog."default",
    speed text COLLATE pg_catalog."default",
    collide text COLLATE pg_catalog."default",
    light text COLLATE pg_catalog."default",
    legacy text COLLATE pg_catalog."default",
    CONSTRAINT sensor_data_pkey PRIMARY KEY (id)
)
WITH (
    OIDS = FALSE
)
TABLESPACE pg_default;

ALTER TABLE iot.sensor_data OWNER to postgres;

CREATE INDEX idx_timestamp
    ON iot.sensor_data USING btree
    (timestamp)
    TABLESPACE pg_default;



CREATE TABLE iot.box_order_relation
(
    "id " integer NOT NULL DEFAULT nextval('iot."box_order_relation_id _seq"'::regclass),
    trackid text COLLATE pg_catalog."default",
    deviceid text COLLATE pg_catalog."default"
)
WITH (
    OIDS = FALSE
)
TABLESPACE pg_default;

ALTER TABLE iot.box_order_relation OWNER to postgres;



CREATE TABLE iot.order_info
(
    id integer NOT NULL DEFAULT nextval('iot.order_info_id_seq'::regclass),
    srcid integer,
    dstid integer,
    trackid text COLLATE pg_catalog."default",
    starttime text COLLATE pg_catalog."default",
    endtime text COLLATE pg_catalog."default",
    carrierid integer
)
WITH (
    OIDS = FALSE
)
TABLESPACE pg_default;

ALTER TABLE iot.order_info OWNER to postgres;


CREATE TABLE iot.site_info
(
    id integer NOT NULL DEFAULT nextval('iot.site_info_id_seq'::regclass),
    location text COLLATE pg_catalog."default",
    latitude text COLLATE pg_catalog."default",
    longitude text COLLATE pg_catalog."default"
)
WITH (
    OIDS = FALSE
)
TABLESPACE pg_default;

ALTER TABLE iot.site_info OWNER to postgres;


CREATE TABLE iot.alert_level_info
(
  id integer NOT NULL DEFAULT nextval('iot."alert_level_info_seq"'::regclass),
  level text COLLATE pg_catalog."default"
)
WITH (
    OIDS = FALSE
)
TABLESPACE pg_default;

ALTER TABLE iot.alert_level_info OWNER to postgres;


CREATE TABLE iot.alert_type_info
(
  id integer NOT NULL DEFAULT nextval('iot."alert_type_info_seq"'::regclass),
  type text COLLATE pg_catalog."default"
)
WITH (
    OIDS = FALSE
)
TABLESPACE pg_default;

ALTER TABLE iot.alert_type_info OWNER to postgres;


CREATE TABLE iot.alert_code_info
(
  id integer NOT NULL DEFAULT nextval('iot."alert_code_info_seq"'::regclass),
  errcode integer
)
WITH (
    OIDS = FALSE
)
TABLESPACE pg_default;

ALTER TABLE iot.alert_code_info OWNER to postgres;


CREATE TABLE iot.battery_info
(
  id integer NOT NULL DEFAULT nextval('iot."battery_info_seq"'::regclass),
  battery_detail text
)
WITH (
    OIDS = FALSE
)
TABLESPACE pg_default;

ALTER TABLE iot.battery_info OWNER to postgres;


CREATE TABLE iot.maintenance_info
(
  id integer NOT NULL DEFAULT nextval('iot."maintenance_info_seq"'::regclass),
  location text
)
WITH (
    OIDS = FALSE
)
TABLESPACE pg_default;

ALTER TABLE iot.maintenance_info OWNER to postgres;


CREATE TABLE iot.interval_time_info
(
  id integer NOT NULL DEFAULT nextval('iot."interval_time_info_seq"'::regclass),
  interval_time_min integer
)
WITH (
    OIDS = FALSE
)
TABLESPACE pg_default;

ALTER TABLE iot.interval_time_info OWNER to postgres;


CREATE TABLE iot.hardware_info
(
  id integer NOT NULL DEFAULT nextval('iot."hardware_info_seq"'::regclass),
  hardware_detail text
)
WITH (
    OIDS = FALSE
)
TABLESPACE pg_default;

ALTER TABLE iot.hardware_info OWNER to postgres;


CREATE TABLE iot.manufacturer_info
(
    id bigint NOT NULL DEFAULT nextval('iot.manufacturer_info_id_seq'::regclass),
    name text COLLATE pg_catalog."default"
)
WITH (
    OIDS = FALSE
)
TABLESPACE pg_default;

ALTER TABLE iot.manufacturer_info
    OWNER to postgres;


CREATE TABLE iot.produce_area_info
(
    id integer NOT NULL DEFAULT nextval('iot.produce_area_info_id_seq'::regclass),
    address text COLLATE pg_catalog."default"
)
WITH (
    OIDS = FALSE
)
TABLESPACE pg_default;

ALTER TABLE iot.produce_area_info
    OWNER to postgres;