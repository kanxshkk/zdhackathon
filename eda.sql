SELECT * FROM home_info order by address;

SELECT * FROM market order by zipcode;
--SELECT * FROM market where id = 672 order by name;

--SELECT * FROM market_geom where market_id = 672;
SELECT * FROM market_geom;

SELECT m.*, mg.*
FROM market m
INNER JOIN market_geom mg ON m.id = mg.market_id order by m.id;

SELECT m.*, hi.*
FROM market m JOIN home_info hi ON m.id = hi.state_market_id;

--exploring home info 
--Range of attributes
SELECT
    MIN(finished_sqft) AS min_finished_sqft,
    MAX(finished_sqft) AS max_finished_sqft,
    AVG(finished_sqft) AS avg_finished_sqft,
    STDDEV(finished_sqft) AS std_dev_finished_sqft,
    MIN(listing_price) AS min_listing_price,
    MAX(listing_price) AS max_listing_price,
    AVG(listing_price) AS avg_listing_price,
    STDDEV(listing_price) AS std_dev_listing_price,
    MIN(bedrooms) AS min_bedrooms,
    MAX(bedrooms) AS max_bedrooms,
    AVG(bedrooms) AS avg_bedrooms,
    MIN(bathrooms) AS min_bathrooms,
    MAX(bathrooms) AS max_bathrooms,
    AVG(bathrooms) AS avg_bathrooms
FROM home_info;

SELECT * from home_info where finished_sqft=0;

SELECT * from home_info where status='OFF_MARKET' and listing_price!=0;

SELECT status, COUNT(*) AS frequency
FROM home_info
GROUP BY status;

SELECT (home_type), COUNT(*) 
from home_info 
GROUP BY home_type;

SELECT market_level, COUNT(*) AS frequency
FROM market
GROUP BY market_level;


-- Geographical spread 
--Basic Statistics


--checking if calculated and given data are equal
SELECT 
    ST_AsText(ST_Centroid(ST_Collect(geom))) AS computed_centroid,
    ST_AsText(centroid_geom) AS actual_centroid
FROM market_geom
GROUP BY centroid_geom;

--Bounding Box of Geographical Entities
SELECT ST_Extent(geom) AS bounding_box
FROM market_geom;

--Spatial Aggregation and Density
SELECT ST_AsText(centroid_geom) AS centroid, COUNT(*) AS entity_count
FROM market_geom
GROUP BY centroid_geom;


-- Temporal spread


--Earliest and Latest Dates
SELECT MIN(listing_contract_date) AS earliest_date, MAX(listing_contract_date) AS latest_date
FROM home_info;

--distribution of listings over months
SELECT EXTRACT(YEAR FROM listing_contract_date) AS year,
       EXTRACT(MONTH FROM listing_contract_date) AS month,
       COUNT(*) AS listings_count
FROM home_info
GROUP BY year, month
ORDER BY year, month;


--average listing price per year
SELECT EXTRACT(YEAR FROM listing_contract_date) AS year,
       AVG(listing_price) AS avg_listing_price
FROM home_info
GROUP BY year
ORDER BY year;

--weekly trends
SELECT DATE_TRUNC('week', listing_contract_date) AS week_start,
       COUNT(*) AS listings_count
FROM home_info
GROUP BY week_start
ORDER BY week_start;

--compare btw years
SELECT EXTRACT(YEAR FROM listing_contract_date) AS year,
       AVG(CASE WHEN EXTRACT(YEAR FROM listing_contract_date) = 2012 THEN listing_price END) AS avg_price_year1,
       AVG(CASE WHEN EXTRACT(YEAR FROM listing_contract_date) = 2014 THEN listing_price END) AS avg_price_year2
FROM home_info
WHERE EXTRACT(YEAR FROM listing_contract_date) IN (2012, 2014)
GROUP BY year;






--● Identify outlier homes and homes with incorrect data


--has null values?
SELECT COUNT(listing_price) 
FROM home_info 
WHERE listing_price IS NULL;

SELECT COUNT(finished_sqft) 
FROM home_info 
WHERE finished_sqft IS NULL;
--both has no null values


select * from home_info where bathrooms is null;
--setting the NULL values to 0, 
UPDATE home_info
SET bedrooms = COALESCE(bedrooms, 0),
    bathrooms = COALESCE(bathrooms, 0),
	lot_size_sqft = COALESCE(lot_size_sqft, 0),
	finished_sqft = COALESCE(finished_sqft, 0)
WHERE bedrooms IS NULL OR bathrooms IS NULL OR lot_size_sqft IS NULL OR finished_sqft IS NULL;

--remove the homes with 0 bedrooms or 0 bathrooms or 0 sqft from home_info as it amkes no sense
DELETE FROM home_info
WHERE bedrooms = 0 OR bathrooms = 0 OR finished_sqft = 0;

select last_sold_date,last_sold_price from home_info where last_sold_date is null;

--i have to update last sold price to null for null last_sold_date
UPDATE home_info
SET last_sold_price = NULL
WHERE last_sold_date IS NULL;

SELECT * FROM home_info;

--Outliers Based on listing_price and finsihed_sqft with IQR
WITH quartiles AS (
    SELECT 
        PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY listing_price) AS q1_price,
        PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY listing_price) AS q3_price,
        PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY finished_sqft) AS q1_sqft,
        PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY finished_sqft) AS q3_sqft
    FROM home_info
),
iqr AS (
    SELECT 
        q1_price,
        q3_price,
        q3_price - q1_price AS iqr_price,
        q1_sqft,
        q3_sqft,
        q3_sqft - q1_sqft AS iqr_sqft
    FROM quartiles
)
SELECT 
    id,
    listing_price,
    finished_sqft,
    CASE 
        WHEN listing_price < i.q1_price - 1.5 * i.iqr_price OR listing_price > i.q3_price + 1.5 * i.iqr_price THEN 'Outlier'
        ELSE 'Not Outlier'
    END AS price_outlier_status,
    CASE 
        WHEN finished_sqft < i.q1_sqft - 1.5 * i.iqr_sqft OR finished_sqft > i.q3_sqft + 1.5 * i.iqr_sqft THEN 'Outlier'
        ELSE 'Not Outlier'
    END AS sqft_outlier_status
FROM home_info h, iqr i, quartiles q;

--remove entries which doesnt fit in the IQR
--delete the outliers
WITH quartiles AS (
    SELECT 
        PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY listing_price) AS q1_price, 
        PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY listing_price) AS q3_price, 
        PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY finished_sqft) AS q1_sqft, 
        PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY finished_sqft) AS q3_sqft 
    FROM 
        home_info
), 
iqr AS (
    SELECT 
        q1_price, 
        q3_price, 
        q3_price - q1_price AS iqr_price, 
        q1_sqft, 
        q3_sqft, 
        q3_sqft - q1_sqft AS iqr_sqft 
    FROM 
        quartiles
)
DELETE FROM 
    home_info h
USING 
    iqr i
JOIN 
    quartiles q ON 1=1 -- Cartesian product
WHERE 
    (h.listing_price < i.q1_price - 1.5 * i.iqr_price OR h.listing_price > i.q3_price + 1.5 * i.iqr_price)
    OR (h.finished_sqft < i.q1_sqft - 1.5 * i.iqr_sqft OR h.finished_sqft > i.q3_sqft + 1.5 * i.iqr_sqft);






--trying to relate lat and long of home_info to centroid of market_geom
/*
SELECT
    h.id AS home_id,
    h.lat AS home_latitude,
    h.long AS home_longitude,
    m.id AS market_id,
    m.centroid_geom AS market_centroid
FROM
    home_info h
JOIN
    market_geom m
ON
    ST_DWithin(ST_Transform(ST_SetSRID(ST_MakePoint(h.long, h.lat), 4326), 4269)::geography, 
               ST_SetSRID(m.centroid_geom, 4269)::geography, 
               300000);
*/

select * from home_info;

--entires which have same listing key
SELECT listing_key, COUNT(*) AS num_entries
FROM home_info
GROUP BY listing_key
HAVING COUNT(*) > 1;
--22 null values 

select distinct bathrooms from home_info;
select  distinct bedrooms from home_info;
--convert decimal values in the "bathrooms" column to whole numbers
UPDATE home_info
SET bathrooms = ROUND(bathrooms)
WHERE bathrooms IS NOT NULL;

select * from home_info where off_market_date is not NULL and pending_date >off_market_date ;


select * from home_info where off_market_date = '1800-01-01 00:00:00';
--change them to null values
UPDATE home_info
SET off_market_date = NULL
WHERE off_market_date = '1800-01-01 00:00:00';
--similarly change all dates
UPDATE home_info
SET listing_contract_date = NULL
WHERE listing_contract_date = '1800-01-01 00:00:00';
UPDATE home_info
SET on_market_date = NULL
WHERE on_market_date = '1800-01-01 00:00:00' ;
UPDATE home_info
SET pending_date = NULL
WHERE pending_date = '1800-01-01 00:00:00' ; 
UPDATE home_info
SET last_sold_date = NULL
WHERE last_sold_date = '1800-01-01 00:00:00' ; 


SELECT home_type,
       COUNT(*) AS total_count,
       AVG(bedrooms) AS total_bedrooms,
       AVG(bathrooms) AS total_bathrooms,
	   AVG(finished_sqft) AS avg_finished_sqft
FROM home_info
GROUP BY home_type
ORDER BY home_type;

--last sold price set to null if 0.0
UPDATE home_info
SET last_sold_price = NULL
WHERE last_sold_price = 0;



select * from home_info;



--remove duplicate houses
SELECT *
FROM home_info h1
WHERE EXISTS (
    SELECT 1
    FROM home_info h2
    WHERE h1.id <> h2.id -- Exclude the same row
    AND h1.bedrooms = h2.bedrooms
    AND h1.bathrooms = h2.bathrooms
    AND h1.finished_sqft = h2.finished_sqft
    AND h1.listing_contract_date = h2.listing_contract_date
);
/*
SELECT *
FROM home_info h1
WHERE EXISTS (
    SELECT 1
    FROM home_info h2
    WHERE h1.id <> h2.id -- Exclude the same row
    AND h1.source_system = h2.source_system
	AND h1.address = h2.address
    AND h1.usps_address = h2.usps_address
    AND h1.status = h2.status
    AND h1.listing_contract_date = h2.listing_contract_date
    AND h1.on_market_date = h2.on_market_date
    AND h1.pending_date = h2.pending_date
    AND h1.last_sold_date = h2.last_sold_date
    AND h1.off_market_date = h2.off_market_date

    AND h1.home_type = h2.home_type
    AND h1.finished_sqft = h2.finished_sqft
    AND h1.lot_size_sqft = h2.lot_size_sqft
    AND h1.bedrooms = h2.bedrooms
    AND h1.bathrooms = h2.bathrooms
    AND h1.year_built = h2.year_built
    AND h1.new_construction = h2.new_construction
    AND h1.has_pool = h2.has_pool
	
    AND h1.state_market_id = h2.state_market_id
    AND h1.city_market_id = h2.city_market_id
    AND h1.zipcode_market_id = h2.zipcode_market_id
    AND h1.neighborhood_level_1_market_id = h2.neighborhood_level_1_market_id
    AND h1.neighborhood_level_2_market_id = h2.neighborhood_level_2_market_id
    AND h1.neighborhood_level_3_market_id = h2.neighborhood_level_3_market_id
	
    AND h1.crawler = h2.crawler
	group by (source_system )
);
*/
/*
-- remove duplicates using repeated addresses
SELECT address,usps_address, COUNT(*) AS address_count
FROM home_info
WHERE address IS NOT NULL and usps_address IS NOT NULL
GROUP BY (address,usps_address)
HAVING COUNT(*) > 1;

--delete repeated addresses
WITH duplicates AS (
    SELECT *,
           ROW_NUMBER() OVER (PARTITION BY address, usps_address ORDER BY listing_contract_date DESC) AS row_num
    FROM home_info
    WHERE address IS NOT NULL AND usps_address IS NOT NULL
)
DELETE FROM home_info
WHERE (address, usps_address) IN (
    SELECT address, usps_address
    FROM duplicates
    WHERE row_num > 1
);

--ROLLBACK;
*/



