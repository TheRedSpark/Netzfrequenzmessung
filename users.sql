CREATE TABLE `Netzfrequenmessung`.`Users` (
  `idUser` BIGINT NOT NULL AUTO_INCREMENT,
  `User_Id` BIGINT NULL,
  `Username` VARCHAR(45) NULL,
  `Email` VARCHAR(150) NULL,
  `Push` TINYINT NULL DEFAULT 0,
  `Push_Toggle` TINYINT NULL DEFAULT 1,
  `Zugelassen` TINYINT NULL DEFAULT 1,
  PRIMARY KEY (`idUser`));