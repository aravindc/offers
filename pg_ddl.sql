drop table if exists tesco;
CREATE TABLE public.tesco (
	id uuid NULL,
	"data" jsonb NULL,
	ins_ts date NULL
) partition by range(ins_ts);


drop table if exists sainsburys;
CREATE TABLE public.sainsburys (
	id uuid NULL,
	"data" jsonb NULL,
	ins_ts date NULL
) partition by range(ins_ts);

drop table if exists morrison;
CREATE TABLE public.morrison (
	id uuid NULL,
	"data" jsonb NULL,
	ins_ts date NULL
) partition by range(ins_ts);


drop table if exists ocado;
CREATE TABLE public.ocado (
	id uuid NULL,
	"data" jsonb NULL,
	ins_ts date NULL
) partition by range(ins_ts);
