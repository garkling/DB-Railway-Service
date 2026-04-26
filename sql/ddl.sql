CREATE TABLE train (
    train_number          VARCHAR(10) NOT NULL,
    service_date          DATE        NOT NULL,
    scheduled_departure   DATETIME    NOT NULL,
    scheduled_arrival     DATETIME    NOT NULL,
    duration_minutes      INT GENERATED ALWAYS AS
        (TIMESTAMPDIFF(MINUTE, scheduled_departure, scheduled_arrival)) STORED,
    train_status          ENUM('on_time','delayed','cancelled') NOT NULL DEFAULT 'on_time',
    operator_code         VARCHAR(10) NOT NULL,
    route_id              INT UNSIGNED NOT NULL,
    -- NEW (green): added in HW3 Step 4
    actual_departure      DATETIME NULL,
    actual_arrival        DATETIME NULL,
    delay_reason          VARCHAR(255) NULL,

    PRIMARY KEY (train_number, service_date),
    CONSTRAINT fk_train_operator FOREIGN KEY (operator_code)
        REFERENCES railway_operator (operator_code)
        ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT fk_train_route FOREIGN KEY (route_id) REFERENCES route (route_id)
        ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB COMMENT='Train service entity — refined HW3';


CREATE TABLE route
(
    route_id                  INT UNSIGNED  NOT NULL AUTO_INCREMENT,
    route_name                VARCHAR(100) NOT NULL UNIQUE COMMENT 'CK: unique route name',
    total_distance_km         DECIMAL(8, 2) DEFAULT NULL COMMENT 'Total distance in km (stored, updated manually)',
    distance_price_multiplier DECIMAL(5, 3) GENERATED ALWAYS AS
        (COALESCE(total_distance_km / 100.0, 1.0)) STORED
        COMMENT 'Derived: price multiplier based on distance',
    PRIMARY KEY (route_id)
) ENGINE=InnoDB COMMENT='Route entity type';

CREATE TABLE station
(
    station_code        CHAR(6)      NOT NULL COMMENT 'UIC station code, e.g. 370006',
    station_name        VARCHAR(100) NOT NULL UNIQUE COMMENT 'CK: unique station name',
    city                VARCHAR(80)  NOT NULL,
    country             VARCHAR(60)  NOT NULL,
    number_of_platforms TINYINT UNSIGNED DEFAULT NULL,
    PRIMARY KEY (station_code)
) ENGINE=InnoDB COMMENT='Station entity type';

CREATE TABLE coach
(
    train_number         VARCHAR(10) NOT NULL COMMENT 'FK to train (part of PK)',
    service_date         DATE        NOT NULL COMMENT 'FK to train (part of PK)',
    coach_number         SMALLINT UNSIGNED NOT NULL COMMENT 'Coach number within train (part of PK)',
    coach_type           VARCHAR(30) NOT NULL COMMENT 'e.g. Seating, Sleeping, Dining, Luggage',
    seat_capacity        SMALLINT UNSIGNED NOT NULL DEFAULT 0,
    has_air_conditioning BOOLEAN     NOT NULL DEFAULT TRUE,
    class_code           VARCHAR(5)  NOT NULL COMMENT 'FK to travel_class (offers)',
    owner_operator_code  VARCHAR(10)          DEFAULT NULL COMMENT 'FK to railway_operator (ownedBy, optional)',

    PRIMARY KEY (train_number, service_date, coach_number),
    CONSTRAINT fk_coach_train FOREIGN KEY (train_number, service_date)
        REFERENCES train (train_number, service_date)
        ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_coach_class
        FOREIGN KEY (class_code) REFERENCES travel_class (class_code)
        ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT fk_coach_owner
        FOREIGN KEY (owner_operator_code) REFERENCES railway_operator (operator_code)
        ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB COMMENT='Coach entity type (Weak ET, identifying rel to Train)';

CREATE TABLE travel_class
(
    class_code            VARCHAR(5)    NOT NULL COMMENT 'e.g. 1ST, 2ND, SLP',
    class_name            VARCHAR(50)   NOT NULL UNIQUE COMMENT 'CK: Full class name',
    description           TEXT                   DEFAULT NULL,
    base_price_multiplier DECIMAL(4, 2) NOT NULL DEFAULT 1.00,
    PRIMARY KEY (class_code)
) ENGINE=InnoDB COMMENT='Travel class entity type';

CREATE TABLE facility
(
    facility_id          INT UNSIGNED   NOT NULL AUTO_INCREMENT,
    facility_name        VARCHAR(80) NOT NULL UNIQUE COMMENT 'CK: unique facility name',
    facility_description TEXT DEFAULT NULL,
    PRIMARY KEY (facility_id)
) ENGINE=InnoDB COMMENT='Onboard facility entity type';

CREATE TABLE passenger
(
    passenger_id  VARCHAR(20) NOT NULL COMMENT 'National ID or passport number',
    first_name    VARCHAR(60) NOT NULL COMMENT 'Part of composite: passengerName',
    last_name     VARCHAR(60) NOT NULL COMMENT 'Part of composite: passengerName',
    date_of_birth DATE        DEFAULT NULL,
    email         VARCHAR(120) UNIQUE COMMENT 'CK: unique email',
    PRIMARY KEY (passenger_id)
) ENGINE=InnoDB COMMENT='Passenger entity type';

CREATE TABLE ticket(
    train_number     VARCHAR(10) NOT NULL,
    service_date     DATE        NOT NULL,
    ticket_number    INT UNSIGNED NOT NULL,
    seat_number      VARCHAR(10) DEFAULT NULL,
    price_paid       DECIMAL(10, 2) NOT NULL,
    booking_date     DATE        NOT NULL,
    passenger_id     VARCHAR(20) NOT NULL,
    class_code       VARCHAR(5)  NOT NULL,
    -- NEW (green): added in HW3 Step 4
    booking_status   ENUM('confirmed','cancelled','refunded') NOT NULL DEFAULT 'confirmed',
    payment_method   VARCHAR(20) NOT NULL DEFAULT 'card',

    PRIMARY KEY (train_number, service_date, ticket_number),
    CONSTRAINT fk_ticket_train FOREIGN KEY (train_number, service_date)
        REFERENCES train (train_number, service_date)
        ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_ticket_passenger FOREIGN KEY (passenger_id)
        REFERENCES passenger (passenger_id)
        ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT fk_ticket_class FOREIGN KEY (class_code)
        REFERENCES travel_class (class_code)
        ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB COMMENT='Ticket entity (Weak ET, identifying rel to Train) — refined HW3';

CREATE TABLE railway_operator
(
    operator_code VARCHAR(10)    NOT NULL COMMENT 'e.g. UZ for Ukrzaliznytsia',
    operator_name VARCHAR(100)   NOT NULL UNIQUE COMMENT 'CK: unique operator name',
    country       VARCHAR(60)    NOT NULL,
    contact_phone VARCHAR(20)             DEFAULT NULL,
    base_fare     DECIMAL(10, 2) NOT NULL DEFAULT 0.00 COMMENT 'Operator base fare for pricing',
    PRIMARY KEY (operator_code)
) ENGINE=InnoDB COMMENT='Railway operator entity type';

CREATE TABLE route_station
(
    route_id     INT UNSIGNED     NOT NULL,
    station_code CHAR(6) NOT NULL,
    stop_order   TINYINT UNSIGNED NOT NULL COMMENT 'Order of stop on the route (1, 2, 3...)',
    PRIMARY KEY (route_id, station_code),
    CONSTRAINT fk_rs_route FOREIGN KEY (route_id) REFERENCES route (route_id)
        ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_rs_station FOREIGN KEY (station_code) REFERENCES station (station_code)
        ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE = InnoDB COMMENT ='Junction table: Route connects Station (M:N)';

CREATE TABLE class_facility
(
    class_code  VARCHAR(5) NOT NULL,
    facility_id INT UNSIGNED NOT NULL,
    PRIMARY KEY (class_code, facility_id),
    CONSTRAINT fk_cf_class FOREIGN KEY (class_code) REFERENCES travel_class (class_code)
        ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_cf_facility FOREIGN KEY (facility_id) REFERENCES facility (facility_id)
        ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE = InnoDB COMMENT ='Junction table: TravelClass provides Facility (M:N).';


CREATE TABLE operator_class_route_pricing
(
    operator_code VARCHAR(10)    NOT NULL,
    class_code    VARCHAR(5)     NOT NULL,
    route_id      INT UNSIGNED   NOT NULL,
    base_price    DECIMAL(10, 2) NOT NULL COMMENT 'Price set by operator for class on route',
    PRIMARY KEY (operator_code, class_code, route_id),
    CONSTRAINT fk_pricing_operator FOREIGN KEY (operator_code)
        REFERENCES railway_operator (operator_code) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_pricing_class FOREIGN KEY (class_code)
        REFERENCES travel_class (class_code) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_pricing_route FOREIGN KEY (route_id)
        REFERENCES route (route_id) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB COMMENT='Ternary relationship: Operator charges for Class on Route';


CREATE TABLE first_class
(
    class_code         VARCHAR(5) NOT NULL PRIMARY KEY,
    lounge_access      BOOLEAN    NOT NULL DEFAULT FALSE,
    complimentary_meal BOOLEAN    NOT NULL DEFAULT FALSE,
    CONSTRAINT fk_first_class_tc FOREIGN KEY (class_code)
        REFERENCES travel_class (class_code) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB COMMENT='Specialization: FirstClass (classCode=1ST).';

CREATE TABLE second_class
(
    class_code        VARCHAR(5) NOT NULL PRIMARY KEY,
    has_folding_table BOOLEAN    NOT NULL DEFAULT TRUE,
    CONSTRAINT fk_second_class_tc FOREIGN KEY (class_code)
        REFERENCES travel_class (class_code) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB COMMENT='Specialization: SecondClass (classCode=2ND).';

CREATE TABLE sleeping_class
(
    class_code           VARCHAR(5) NOT NULL PRIMARY KEY,
    berth_type           ENUM('upper','lower','both') NOT NULL DEFAULT 'both',
    linens_included      BOOLEAN    NOT NULL DEFAULT TRUE,
    compartment_capacity TINYINT UNSIGNED NOT NULL DEFAULT 4,
    CONSTRAINT fk_sleeping_class_tc FOREIGN KEY (class_code)
        REFERENCES travel_class (class_code) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB COMMENT='Specialization: SleepingClass (classCode=SLP).';

CREATE TABLE seating_coach (
    train_number     VARCHAR(10) NOT NULL,
    service_date     DATE        NOT NULL,
    coach_number     SMALLINT UNSIGNED NOT NULL,
    seat_arrangement VARCHAR(10) NOT NULL DEFAULT '2+2' COMMENT 'e.g. 2+2, 2+1',
    PRIMARY KEY (train_number, service_date, coach_number),
    CONSTRAINT fk_seating_coach FOREIGN KEY (train_number, service_date, coach_number)
        REFERENCES coach (train_number, service_date, coach_number)
        ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB COMMENT='Specialization: SeatingCoach.';

CREATE TABLE sleeping_coach (
    train_number           VARCHAR(10) NOT NULL,
    service_date           DATE        NOT NULL,
    coach_number           SMALLINT UNSIGNED NOT NULL,
    number_of_compartments TINYINT UNSIGNED  NOT NULL DEFAULT 9,
    berths_per_compartment TINYINT UNSIGNED  NOT NULL DEFAULT 4,
    PRIMARY KEY (train_number, service_date, coach_number),
    CONSTRAINT fk_sleeping_coach FOREIGN KEY (train_number, service_date, coach_number)
        REFERENCES coach (train_number, service_date, coach_number)
        ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB COMMENT='Specialization: SleepingCoach.';

CREATE TABLE dining_coach (
    train_number     VARCHAR(10) NOT NULL,
    service_date     DATE        NOT NULL,
    coach_number     SMALLINT UNSIGNED NOT NULL,
    number_of_tables TINYINT UNSIGNED  NOT NULL DEFAULT 10,
    menu_type        VARCHAR(50) DEFAULT NULL,
    PRIMARY KEY (train_number, service_date, coach_number),
    CONSTRAINT fk_dining_coach FOREIGN KEY (train_number, service_date, coach_number)
        REFERENCES coach (train_number, service_date, coach_number)
        ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB COMMENT='Specialization: DiningCoach.';

CREATE TABLE luggage_van (
    train_number     VARCHAR(10)   NOT NULL,
    service_date     DATE          NOT NULL,
    coach_number     SMALLINT UNSIGNED NOT NULL,
    max_weight_kg    DECIMAL(8, 2) NOT NULL DEFAULT 5000.00,
    has_bicycle_rack BOOLEAN       NOT NULL DEFAULT FALSE,
    PRIMARY KEY (train_number, service_date, coach_number),
    CONSTRAINT fk_luggage_van FOREIGN KEY (train_number, service_date, coach_number)
        REFERENCES coach (train_number, service_date, coach_number)
        ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB COMMENT='Specialization: LuggageVan.';
