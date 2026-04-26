ALTER TABLE ticket
    ADD COLUMN booking_status ENUM('confirmed','cancelled','refunded') NOT NULL DEFAULT 'confirmed';

ALTER TABLE ticket
    ADD COLUMN payment_method VARCHAR(20) NOT NULL DEFAULT 'card';

ALTER TABLE train
    ADD COLUMN actual_departure DATETIME NULL;

ALTER TABLE train
    ADD COLUMN actual_arrival DATETIME NULL;

ALTER TABLE train
    ADD COLUMN delay_reason VARCHAR(255) NULL;

ALTER TABLE passenger
    DROP COLUMN phone;