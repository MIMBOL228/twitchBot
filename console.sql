CREATE DATABASE mimbol;
CREATE TABLE IF NOT EXISTS `mimbol`.`users` (
    `id` INT NOT NULL AUTO_INCREMENT,
    `uuid` VARCHAR(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
    `tg_id` TEXT CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
    `balance` INT NOT NULL,
    PRIMARY KEY (`id`)
) ENGINE = InnoDB;