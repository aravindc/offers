drop table if exists tesco;
CREATE TABLE public.tesco (
	id uuid NULL,
	"data" jsonb NULL,
	ins_ts date NULL
) WITH ( OIDS=FALSE);


drop table if exists sainsburys;
CREATE TABLE public.sainsburys (
	id uuid NULL,
	"data" jsonb NULL,
	ins_ts date NULL
) WITH ( OIDS=FALSE);

drop table if exists morrison;
CREATE TABLE public.morrison (
	id uuid NULL,
	"data" jsonb NULL,
	ins_ts date NULL
) WITH ( OIDS=FALSE);


drop table if exists ocado;
CREATE TABLE public.ocado (
	id uuid NULL,
	"data" jsonb NULL,
	ins_ts date NULL
) WITH ( OIDS=FALSE);


CREATE OR REPLACE FUNCTION create_partition_and_insert() RETURNS trigger AS
  $BODY$
    DECLARE
      partition_date TEXT;
      partition TEXT;
    BEGIN
      partition_date := to_char(NEW.ins_ts,'YYYYMMDD');
      partition := TG_RELNAME || '_' || partition_date;
      IF NOT EXISTS(SELECT relname FROM pg_class WHERE relname=partition) THEN
        RAISE NOTICE 'A partition has been created %',partition;
        EXECUTE 'CREATE TABLE ' || partition || ' (check (ins_ts = ''' || NEW.ins_ts || ''')) INHERITS (' || TG_RELNAME || ');';
      END IF;
      EXECUTE 'INSERT INTO ' || partition || ' SELECT(' || TG_RELNAME || ' ' || quote_literal(NEW) || ').* RETURNING id;';
      RETURN NULL;
    END;
  $BODY$
LANGUAGE plpgsql VOLATILE
COST 100;

CREATE TRIGGER tesco_partition_insert_trigger
BEFORE INSERT ON tesco
FOR EACH ROW EXECUTE PROCEDURE create_partition_and_insert();

CREATE TRIGGER sains_partition_insert_trigger
BEFORE INSERT ON sainsburys
FOR EACH ROW EXECUTE PROCEDURE create_partition_and_insert();

CREATE TRIGGER morri_partition_insert_trigger
BEFORE INSERT ON morrison
FOR EACH ROW EXECUTE PROCEDURE create_partition_and_insert();

CREATE TRIGGER ocado_partition_insert_trigger
BEFORE INSERT ON ocado
FOR EACH ROW EXECUTE PROCEDURE create_partition_and_insert();

drop table if exists asda;
CREATE TABLE public.asda (
	id uuid NULL,
	"data" jsonb NULL,
	ins_ts date NULL
) WITH ( OIDS=FALSE);

CREATE TRIGGER asda_partition_insert_trigger
BEFORE INSERT ON asda
FOR EACH ROW EXECUTE PROCEDURE create_partition_and_insert();
