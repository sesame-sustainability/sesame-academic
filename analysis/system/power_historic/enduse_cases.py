#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Aug  4 15:04:16 2020

@author: ngoteti
These are the end-use case for system analysis
"""

#IN UI, the user could choose state, start year and end year
state='CA'
start='2018'
end='2019'

#The query below is for extracting total hourly generation and emissions for start/stop, part load, near full load, and full load
#The table provides the output for different fuel type and turbine types

#start of query, the total query is divided into different parts for reducing time
#SQL start
--part 1: Extract the processed arp and egrid data for given years and states
-- note year and states are hard coded but should be decided by the UI
with arp_small as (
		select plant_id, unit, state, orispl, nameplate_capacity, prime_mover, fuel_type
		from arp_egrid_capacity
		where (date_part='2018' or date_part='2019') and state='CA'),

/*part 2: select arp date for a given timestamp range and state and combine with arp_small for nameplate capacities*/
	arp_select as (
		select * from arp where
		plant_id in (select plant_id from arp_small) and
	 	arp.timestamp>='2018-01-01 00:00:00' and
	 	arp.timestamp<'2020-01-01 00:00:00'),

/*part 3: deciding the buckets they fall under and merging with loading fractions */
	arp_combine as (
		SELECT *,gload/nameplate_capacity as lf  FROM arp_select
		join arp_small on arp_select.plant_id=arp_small.plant_id and arp_select.unit=arp_small.unit
		where nameplate_capacity is not null or nameplate_capacity<>0
		order by timestamp),
	arp_bucket as (
		SELECT *,
		CASE  when (lf<=0.2 and prime_mover in ('CT','CC','CS','ST')) then 0.2
			   when (lf>0.2 and lf<=0.75 and prime_mover in ('CT','CC','CS','ST')) then 0.75
			   when (lf>0.75 and lf<=0.9 and prime_mover in ('CT','CC','CS','ST')) then 0.9
			   when (lf>0.9 and lf<=1 and prime_mover in ('CT','CC','CS')) then 1
			   when (lf<=0.4 and prime_mover in ('CT','CC','CS','ST')) then 0.4
				when (lf>0.4 and lf<=0.75 and prime_mover in ('GT')) then 0.75
				when (lf>0.75 and lf<=0.9 and prime_mover in ('GT')) then 0.9
				when (lf>0.9 and lf<=1 and prime_mover in ('GT')) then 1
		END as bucket
		FROM arp_combine
	),

	arp_lf as (
	select * from arp_bucket
	join loading_fraction on
		arp_bucket.bucket= loading_fraction.loading_fraction and
		arp_bucket.prime_mover=loading_fraction.prime_mover)

/* merging it all and grouping by hour and year for different fuels and types of turbines */
	select  date_part('hour', "timestamp") as hour, date_part('year', "timestamp") as year,
			sum(gload) as generation,
			sum(so2_mass) as so2, sum(nox_mass) as nox, sum(co2_mass) as co2,
			sum(heat_input) as heat, state, sum(nameplate_capacity) as total_capacity,
			fuel_type, status, type
	from arp_lf
	group by date_part('hour', "timestamp"), date_part('year', "timestamp"),
	state, fuel_type, status, type
	order by year,hour,type;
#SQL end

#Query 2 estimates the emissions intensity over two years for a given state for start/stop, part load, near full load, and full load
#IN UI, the user could choose state, start year and end year
state='CA'
start='2018'
end='2019'

#SQL start
--part 1: Extract the processed arp and egrid data for given years and states
-- note year and states are hard coded but should be decided by the UI
with arp_small as (
		select plant_id, unit, state, orispl, nameplate_capacity, prime_mover, fuel_type
		from arp_egrid_capacity
		where (date_part='2018' or date_part='2019') and state='CA'),

/*part 2: select arp date for a given timestamp range and state and combine with arp_small for nameplate capacities*/
	arp_select as (
		select * from arp where
		plant_id in (select plant_id from arp_small) and
	 	arp.timestamp>='2018-01-01 00:00:00' and
	 	arp.timestamp<'2020-01-01 00:00:00'),

/*part 3: deciding the buckets they fall under and merging with loading fractions */
	arp_combine as (
		SELECT *,gload/nameplate_capacity as lf  FROM arp_select
		join arp_small on arp_select.plant_id=arp_small.plant_id and arp_select.unit=arp_small.unit
		where nameplate_capacity is not null or nameplate_capacity<>0
		order by timestamp),
	arp_bucket as (
		SELECT *,
		CASE  when (lf<=0.2 and prime_mover in ('CT','CC','CS','ST')) then 0.2
			   when (lf>0.2 and lf<=0.75 and prime_mover in ('CT','CC','CS','ST')) then 0.75
			   when (lf>0.75 and lf<=0.9 and prime_mover in ('CT','CC','CS','ST')) then 0.9
			   when (lf>0.9 and lf<=1 and prime_mover in ('CT','CC','CS')) then 1
			   when (lf<=0.4 and prime_mover in ('CT','CC','CS','ST')) then 0.4
				when (lf>0.4 and lf<=0.75 and prime_mover in ('GT')) then 0.75
				when (lf>0.75 and lf<=0.9 and prime_mover in ('GT')) then 0.9
				when (lf>0.9 and lf<=1 and prime_mover in ('GT')) then 1
		END as bucket
		FROM arp_combine
	),

	arp_lf as (
	select * from arp_bucket
	join loading_fraction on
		arp_bucket.bucket= loading_fraction.loading_fraction and
		arp_bucket.prime_mover=loading_fraction.prime_mover)

/* merging it all and grouping by hour and year for different fuels and types of turbines */
	select  date_part('year', "timestamp") as year,
			sum(co2_mass)/sum(gload) as emission_intensity, state
			fuel_type, status, type
	from arp_lf
	group by date_part('year', "timestamp"),
	state, fuel_type, status, type
	order by year,type;

#SQL end
