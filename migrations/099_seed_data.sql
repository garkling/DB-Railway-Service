-- Independent tables (no FK dependencies on other seeded tables)

LOAD DATA INFILE '/var/lib/mysql-files/railway_operator.csv'
    INTO TABLE railway_operator
    FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '"'
    LINES TERMINATED BY '\n'
    IGNORE 1 ROWS;

-- route: explicit column list omits the GENERATED distance_price_multiplier column
LOAD DATA INFILE '/var/lib/mysql-files/route.csv'
    INTO TABLE route
    FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '"'
    LINES TERMINATED BY '\n'
    IGNORE 1 ROWS
    (route_id, route_name, total_distance_km);

LOAD DATA INFILE '/var/lib/mysql-files/station.csv'
    INTO TABLE station
    FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '"'
    LINES TERMINATED BY '\n'
    IGNORE 1 ROWS;

LOAD DATA INFILE '/var/lib/mysql-files/travel_class.csv'
    INTO TABLE travel_class
    FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '"'
    LINES TERMINATED BY '\n'
    IGNORE 1 ROWS;

LOAD DATA INFILE '/var/lib/mysql-files/facility.csv'
    INTO TABLE facility
    FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '"'
    LINES TERMINATED BY '\n'
    IGNORE 1 ROWS;

LOAD DATA INFILE '/var/lib/mysql-files/passenger.csv'
    INTO TABLE passenger
    FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '"'
    LINES TERMINATED BY '\n'
    IGNORE 1 ROWS;

-- train: explicit column list discards the GENERATED duration_minutes column from the CSV
LOAD DATA INFILE '/var/lib/mysql-files/train.csv'
    INTO TABLE train
    FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '"'
    LINES TERMINATED BY '\n'
    IGNORE 1 ROWS
    (train_number, service_date, scheduled_departure, scheduled_arrival, @duration_minutes,
     train_status, operator_code, route_id, actual_departure, actual_arrival, delay_reason);

LOAD DATA INFILE '/var/lib/mysql-files/coach.csv'
    INTO TABLE coach
    FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '"'
    LINES TERMINATED BY '\n'
    IGNORE 1 ROWS;

LOAD DATA INFILE '/var/lib/mysql-files/ticket.csv'
    INTO TABLE ticket
    FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '"'
    LINES TERMINATED BY '\n'
    IGNORE 1 ROWS;

-- Junction tables

LOAD DATA INFILE '/var/lib/mysql-files/route_station.csv'
    INTO TABLE route_station
    FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '"'
    LINES TERMINATED BY '\n'
    IGNORE 1 ROWS;

LOAD DATA INFILE '/var/lib/mysql-files/class_facility.csv'
    INTO TABLE class_facility
    FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '"'
    LINES TERMINATED BY '\n'
    IGNORE 1 ROWS;

LOAD DATA INFILE '/var/lib/mysql-files/operator_class_route_pricing.csv'
    INTO TABLE operator_class_route_pricing
    FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '"'
    LINES TERMINATED BY '\n'
    IGNORE 1 ROWS;

-- Specialization tables

LOAD DATA INFILE '/var/lib/mysql-files/first_class.csv'
    INTO TABLE first_class
    FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '"'
    LINES TERMINATED BY '\n'
    IGNORE 1 ROWS;

LOAD DATA INFILE '/var/lib/mysql-files/second_class.csv'
    INTO TABLE second_class
    FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '"'
    LINES TERMINATED BY '\n'
    IGNORE 1 ROWS;

LOAD DATA INFILE '/var/lib/mysql-files/sleeping_class.csv'
    INTO TABLE sleeping_class
    FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '"'
    LINES TERMINATED BY '\n'
    IGNORE 1 ROWS;

LOAD DATA INFILE '/var/lib/mysql-files/seating_coach.csv'
    INTO TABLE seating_coach
    FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '"'
    LINES TERMINATED BY '\n'
    IGNORE 1 ROWS;

LOAD DATA INFILE '/var/lib/mysql-files/sleeping_coach.csv'
    INTO TABLE sleeping_coach
    FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '"'
    LINES TERMINATED BY '\n'
    IGNORE 1 ROWS;

LOAD DATA INFILE '/var/lib/mysql-files/dining_coach.csv'
    INTO TABLE dining_coach
    FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '"'
    LINES TERMINATED BY '\n'
    IGNORE 1 ROWS;

LOAD DATA INFILE '/var/lib/mysql-files/luggage_van.csv'
    INTO TABLE luggage_van
    FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '"'
    LINES TERMINATED BY '\n'
    IGNORE 1 ROWS;