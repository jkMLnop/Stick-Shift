CREATE TABLE car_listings_final
(
	zip text,
	id text PRIMARY KEY,
	url text,
	date text,
	title text,
	price numeric,
	make text,
	model text,
	model_year numeric,
	thumbnail_url text
);
