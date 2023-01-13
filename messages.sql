CREATE TABLE `Netzfrequenmessung`.`Messages` (
  `Chat_Id` BIGINT NULL,
  `First_Name` VARCHAR(45) NULL,
  `idMessages` INT NOT NULL AUTO_INCREMENT,
  `Land_Code` VARCHAR(45) NULL,
  `Last_Name` VARCHAR(45) NULL,
  `Message_Id` INT NULL,
  `Message_Text` VARCHAR(45) NULL,
  `Time` DATETIME NULL,
  `User_Id` BIGINT NULL,
  `Username` VARCHAR(45) NULL,
  PRIMARY KEY (`idMessages`));