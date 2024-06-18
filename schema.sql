CREATE EXTENSION IF NOT EXISTS citext;
CREATE EXTENSION IF NOT EXISTS timescaledb;

CREATE TABLE IF NOT EXISTS users (
    id BIGSERIAL PRIMARY KEY,
    email CITEXT NOT NULL,
    name TEXT,
    institution TEXT,
    hashed_password TEXT NOT NULL,
    created_at TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT now(),
    updated_at TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT now()
);

CREATE UNIQUE INDEX IF NOT EXISTS users_email_idx ON users (email);

CREATE TABLE IF NOT EXISTS utilities (
    id BIGSERIAL PRIMARY KEY,
    utlsrvid TEXT NOT NULL,
    name TEXT
);

CREATE UNIQUE INDEX IF NOT EXISTS utilties_utlsrvid_idx ON utilities (utlsrvid);

CREATE TABLE IF NOT EXISTS balancing_authorities (
    id BIGSERIAL PRIMARY KEY,
    code TEXT NOT NULL,
    name TEXT NOT NULL
);

CREATE UNIQUE INDEX IF NOT EXISTS balancing_authorities_code_idx ON balancing_authorities (code);

CREATE TABLE IF NOT EXISTS plants (
    id BIGSERIAL PRIMARY KEY,
    utility_id BIGINT NOT NULL REFERENCES utilities(id),
    balancing_authority_id BIGINT REFERENCES balancing_authorities(id),
    orispl TEXT NOT NULL,
    state TEXT NOT NULL,
    name TEXT NOT NULL,
    nerc_region TEXT NOT NULL,
    subregion_acronym TEXT,
    subregion_name TEXT,
    isorto TEXT,
    county_name TEXT,
    latitude DOUBLE PRECISION,
    longitude DOUBLE PRECISION,
    num_units INTEGER,
    num_generators INTEGER,
    primary_fuel TEXT,
    nameplate_capacity DOUBLE PRECISION,
    power_to_heat_ratio DOUBLE PRECISION
);

CREATE UNIQUE INDEX IF NOT EXISTS plants_orispl_idx ON plants (orispl);

CREATE TABLE IF NOT EXISTS egrid (
    id BIGSERIAL PRIMARY KEY,

    year INTEGER NOT NULL,
    plant_id BIGINT NOT NULL REFERENCES plants(id),
    --- TODO: unit TEXT NOT NULL,
    --- TODO: generator TEXT NOT NULL,

    annual_nox_rate DOUBLE PRECISION,
    ozone_season_nox_rate DOUBLE PRECISION,
    annual_so2_rate DOUBLE PRECISION,
    annual_co2_rate DOUBLE PRECISION,
    annual_ch4_rate DOUBLE PRECISION,
    annual_n2o_rate DOUBLE PRECISION,
    annual_co2_equivalent_rate DOUBLE PRECISION,
    annual_hg_rate DOUBLE PRECISION,
    nominal_heat_rate DOUBLE PRECISION
);

CREATE UNIQUE INDEX IF NOT EXISTS egrid_year_plant_id_idx ON egrid (year, plant_id);
CREATE INDEX IF NOT EXISTS egrid_plant_id ON egrid (plant_id);

CREATE TABLE IF NOT EXISTS arp (
    timestamp TIMESTAMP NOT NULL,
    plant_id BIGINT NOT NULL REFERENCES plants(id),
    unit TEXT NOT NULL,

    gload DOUBLE PRECISION,
    so2_mass DOUBLE PRECISION,
    nox_mass DOUBLE PRECISION,
    co2_mass DOUBLE PRECISION,
    heat_input DOUBLE PRECISION
);

CREATE UNIQUE INDEX IF NOT EXISTS arp_timestamp_plant_id_unit_idx ON arp (timestamp, plant_id, unit);
CREATE INDEX IF NOT EXISTS arp_plant_id_idx ON arp (plant_id);
CREATE INDEX IF NOT EXISTS arp_unit_idx ON arp (unit); --- TODO

SELECT create_hypertable('arp', 'timestamp');

CREATE TABLE grid_unit_genmap (
    "Seqno" INTEGER,
    state CHARACTER VARYING NOT NULL,
    plant_name CHARACTER VARYING,
    orispl integer NOT NULL,
    unit CHARACTER VARYING,
    prime_mover CHARACTER VARYING,
    fuel CHARACTER VARYING,
    online_year CHARACTER VARYING,
    egrid_year INTEGER,
    gen CHARACTER VARYING,
    number_of_boiler INTEGER,
    genstatus CHARACTER VARYING,
    gen_prime_mover CHARACTER VARYING,
    gen_fuel CHARACTER VARYING,
    capacity_mw NUMERIC,
    match_score NUMERIC,
    plant_id NUMERIC
);

CREATE TABLE loading_fraction (
    prime_mover CHARACTER VARYING,
    loading_fraction NUMERIC,
    status CHARACTER VARYING,
    type TEXT
);

CREATE MATERIALIZED VIEW arp_egrid_capacity AS
SELECT
  date_part('year', arp.timestamp) AS year,
  arp.plant_id,
  arp.unit,
  sum(arp.gload) AS generation,
  max(arp.gload) AS max_generation,
  sum(arp.so2_mass) AS so2,
  sum(arp.nox_mass) AS nox,
  sum(arp.co2_mass) AS co2,
  sum(arp.heat_input) AS heat,
  grid_unit_genmap.state,
  grid_unit_genmap.orispl,
  grid_unit_genmap.capacity_mw,
  grid_unit_genmap.gen_prime_mover AS prime_mover,
  grid_unit_genmap.gen_fuel AS fuel_type,
  greatest(max(arp.gload), grid_unit_genmap.capacity_mw) AS nameplate_capacity
FROM arp
JOIN grid_unit_genmap
  ON arp.plant_id = grid_unit_genmap.plant_id
  AND arp.unit = grid_unit_genmap.unit
  AND arp.plant_id IS NOT NULL
GROUP BY
  year,
  arp.plant_id,
  arp.unit,
  grid_unit_genmap.gen_prime_mover,
  grid_unit_genmap.capacity_mw,
  grid_unit_genmap.state,
  grid_unit_genmap.orispl,
  grid_unit_genmap.gen_fuel
;

CREATE UNIQUE INDEX ON arp_egrid_capacity (year, plant_id, unit, prime_mover, capacity_mw, state, orispl, fuel_type);

CREATE OR REPLACE FUNCTION arp_bucket(lf double precision, prime_mover text)
RETURNS double precision IMMUTABLE AS $$
BEGIN
  RETURN CASE
    WHEN (lf <= 0.2 AND prime_mover IN ('CT','CC','CS','ST')) THEN 0.2
	WHEN (lf > 0.2 AND lf <= 0.75 AND prime_mover IN ('CT','CC','CS','ST')) THEN 0.75
	WHEN (lf > 0.75 AND lf <= 0.9 AND prime_mover IN ('CT','CC','CS','ST')) THEN 0.9
	WHEN (lf > 0.9 AND lf <= 1 AND prime_mover IN ('CT','CC','CS')) THEN 1
	WHEN (lf <= 0.4 AND prime_mover IN ('CT','CC','CS','ST')) THEN 0.4
	WHEN (lf > 0.4 AND lf <= 0.75 AND prime_mover IN ('GT')) THEN 0.75
	WHEN (lf > 0.75 AND lf <= 0.9 AND prime_mover IN ('GT')) THEN 0.9
	WHEN (lf > 0.9 AND lf <= 1 AND prime_mover in ('GT')) THEN 1
  END;
END;
$$
LANGUAGE plpgsql;

CREATE OR REPLACE VIEW arp_lf AS
SELECT
  date_part('year', timestamp) AS year,
  date_part('hour', timestamp) AS hour,
  arp.gload,
  arp.so2_mass,
  arp.nox_mass,
  arp.co2_mass,
  arp.heat_input,
  arp_egrid_capacity.nameplate_capacity,
  arp_egrid_capacity.prime_mover,
  arp_egrid_capacity.state,
  arp_egrid_capacity.fuel_type,
  loading_fraction.status,
  loading_fraction.type
FROM arp
INNER JOIN arp_egrid_capacity ON
  arp_egrid_capacity.plant_id = arp.plant_id
  AND arp_egrid_capacity.unit = arp.unit
INNER JOIN loading_fraction ON
  arp_bucket(arp.gload / arp_egrid_capacity.nameplate_capacity, arp_egrid_capacity.prime_mover) = loading_fraction.loading_fraction
  AND arp_egrid_capacity.prime_mover = loading_fraction.prime_mover
WHERE
  arp_egrid_capacity.nameplate_capacity IS NOT NULL
  AND arp_egrid_capacity.nameplate_capacity <> 0
;

CREATE MATERIALIZED VIEW arp_generation AS
SELECT
  year,
  hour,
  sum(gload) AS generation,
  sum(so2_mass) AS so2,
  sum(nox_mass) AS nox,
  sum(co2_mass) AS co2,
  sum(heat_input) AS heat,
  sum(nameplate_capacity) AS total_capacity,
  state,
  status,
  type
FROM
  arp_lf
GROUP BY
  hour,
  year,
  state,
  status,
  type
;

CREATE UNIQUE INDEX ON arp_generation (hour, year, state, status, type);

-- To be run whenever arp data changes:
-- REFRESH MATERIALIZED VIEW CONCURRENTLY arp_egrid_capacity;
-- REFRESH MATERIALIZED VIEW CONCURRENTLY arp_generation;
