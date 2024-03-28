--SELECT * from home_info where address is null;

SELECT address, COUNT(*) AS duplicate_count
FROM home_info
GROUP BY address
HAVING COUNT(*) > 1;

--print them all
SELECT *
FROM home_info
WHERE address IN (
    SELECT address
    FROM home_info
    WHERE address IS NOT NULL
    GROUP BY address
    HAVING COUNT(*) > 1
)
order by address;



--same date
SELECT * from home_info where address = '10 Kennedy Pl #103, San Francisco, CA, 94124';

SELECT address, listing_contract_date, COUNT(*) AS count
FROM home_info
GROUP BY address, listing_contract_date
HAVING COUNT(*) > 1
order by address;

--select those entries
SELECT *
FROM home_info
WHERE (address, listing_contract_date) IN (
    SELECT address, listing_contract_date
    FROM home_info
    GROUP BY address, listing_contract_date
    HAVING COUNT(*) > 1
)
ORDER BY address;



--Pseudo duplicate
SELECT * from home_info where address = '10 Oldham Street, Houston, TX, 77011';

SELECT address, COUNT(DISTINCT listing_contract_date) AS unique_listing_dates_count
FROM home_info
GROUP BY address
HAVING COUNT(DISTINCT listing_contract_date) > 1
order by address;

--select them
SELECT *
FROM home_info
WHERE address IN (
    SELECT address
    FROM home_info
    GROUP BY address
    HAVING COUNT(DISTINCT listing_contract_date) > 1
)
ORDER BY address;



--making absolute duplicates wihtin a time-range of 7 days
SELECT h1.address, h1.listing_contract_date AS listing_contract_date_1, 
       h2.listing_contract_date AS listing_contract_date_2
FROM home_info h1
INNER JOIN home_info h2 ON h1.address = h2.address
WHERE h1.id < h2.id and h1.listing_contract_date != h2.listing_contract_date
AND ABS(EXTRACT(DAY FROM h1.listing_contract_date - h2.listing_contract_date)) <= 7
order by address
;
--selecting unique vales 
SELECT DISTINCT h1.address, h1.listing_contract_date AS listing_contract_date_1, 
       h2.listing_contract_date AS listing_contract_date_2
FROM home_info h1
INNER JOIN home_info h2 ON h1.address = h2.address
WHERE h1.id < h2.id and h1.listing_contract_date != h2.listing_contract_date
AND ABS(EXTRACT(DAY FROM h1.listing_contract_date - h2.listing_contract_date)) <= 7
order by address;

--Absolute duplicate
WITH AbsoluteDuplicates AS (
    SELECT DISTINCT h1.address, h1.listing_contract_date AS listing_contract_date_1, 
           h2.listing_contract_date AS listing_contract_date_2
    FROM home_info h1
    INNER JOIN home_info h2 ON h1.address = h2.address
    WHERE h1.id < h2.id and h1.listing_contract_date != h2.listing_contract_date
    AND ABS(EXTRACT(DAY FROM h1.listing_contract_date - h2.listing_contract_date)) <= 7
)
SELECT address, listing_contract_date_1, listing_contract_date_2
FROM AbsoluteDuplicates
WHERE ABS(EXTRACT(DAY FROM listing_contract_date_1 - listing_contract_date_2)) <= 7;

-- select those entires 
SELECT *
FROM home_info h1
WHERE EXISTS (
    SELECT 1
    FROM home_info h2
    WHERE h1.address = h2.address
      AND ABS(EXTRACT(DAY FROM h1.listing_contract_date - h2.listing_contract_date)) <= 7
)
ORDER BY address
;

--testing 
SELECT * FROM (
SELECT *
FROM home_info h1
WHERE EXISTS (
    SELECT 1
    FROM home_info h2
    WHERE h1.address = h2.address
      AND ABS(EXTRACT(DAY FROM h1.listing_contract_date - h2.listing_contract_date)) <= 7
)
ORDER BY address) where address = '1018 NE 71st Street, Seattle, WA, 98115'
;


CHECKPOINT;
BEGIN;
--delete duplicates of Pseudo Duplicate
WITH duplicates AS (
    SELECT *,
           ROW_NUMBER() OVER (PARTITION BY address ORDER BY listing_contract_date DESC) AS row_num
    FROM home_info
)
DELETE FROM home_info
WHERE (address, listing_contract_date) IN (
    SELECT address, listing_contract_date
    FROM duplicates
    WHERE row_num > 1
);

--check if its deleted
SELECT address, COUNT(DISTINCT listing_contract_date) AS unique_listing_dates_count
FROM home_info
GROUP BY address
HAVING COUNT(DISTINCT listing_contract_date) > 1
order by address;
--they are deleted

ROLLBACK;