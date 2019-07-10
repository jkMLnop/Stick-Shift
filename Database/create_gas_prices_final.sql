CREATE TABLE gas_prices_final
(
	zip numeric,
	id numeric PRIMARY KEY,
	name text,
	price_regular numeric,
	address text,
	distance numeric,
	url text,
	time_updated numeric
);
