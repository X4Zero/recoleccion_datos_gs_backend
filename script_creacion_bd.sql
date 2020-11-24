-- MySQL Workbench Forward Engineering

SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0;
SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0;
SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION';

-- -----------------------------------------------------
-- Schema mydb
-- -----------------------------------------------------
-- -----------------------------------------------------
-- Schema bd_ws
-- -----------------------------------------------------

-- -----------------------------------------------------
-- Schema bd_ws
-- -----------------------------------------------------
CREATE SCHEMA IF NOT EXISTS `bd_ws` ;
USE `bd_ws` ;

-- -----------------------------------------------------
-- Table `bd_ws`.`investigador`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `bd_ws`.`investigador` (
  `idinvestigador` INT NOT NULL AUTO_INCREMENT,
  `nombres` VARCHAR(100) NULL,
  `informacion` VARCHAR(255) NULL,
  `url_imagen` VARCHAR(255) NULL,
  `url_perfil` VARCHAR(255) NOT NULL,
  PRIMARY KEY (`idinvestigador`),
  UNIQUE INDEX `url_perfil_UNIQUE` (`url_perfil` ASC) )
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `bd_ws`.`topico`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `bd_ws`.`topico` (
  `idtopico` INT NOT NULL AUTO_INCREMENT,
  `topico` VARCHAR(100) NULL,
  `investigador_idinvestigador` INT NOT NULL,
  PRIMARY KEY (`idtopico`),
  INDEX `fk_topico_investigador1_idx` (`investigador_idinvestigador` ASC) ,
  CONSTRAINT `fk_topico_investigador1`
    FOREIGN KEY (`investigador_idinvestigador`)
    REFERENCES `bd_ws`.`investigador` (`idinvestigador`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `bd_ws`.`investigacion`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `bd_ws`.`investigacion` (
  `idinvestigacion` INT NOT NULL AUTO_INCREMENT,
  `titulo` VARCHAR(200) NULL,
  `revista` VARCHAR(200) NULL,
  `autores` VARCHAR(200) NULL,
  `año` INT NULL,
  `numero_citaciones` INT NULL,
  `investigador_idinvestigador` INT NOT NULL,
  PRIMARY KEY (`idinvestigacion`),
  INDEX `fk_investigacion_investigador_idx` (`investigador_idinvestigador` ASC) ,
  CONSTRAINT `fk_investigacion_investigador`
    FOREIGN KEY (`investigador_idinvestigador`)
    REFERENCES `bd_ws`.`investigador` (`idinvestigador`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `bd_ws`.`cita`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `bd_ws`.`cita` (
  `idcita` INT NOT NULL AUTO_INCREMENT,
  `modalidad` VARCHAR(45) NULL,
  `desde_2015` INT NULL,
  `total` INT NULL,
  `investigador_idinvestigador` INT NOT NULL,
  PRIMARY KEY (`idcita`),
  INDEX `fk_cita_investigador1_idx` (`investigador_idinvestigador` ASC) ,
  CONSTRAINT `fk_cita_investigador1`
    FOREIGN KEY (`investigador_idinvestigador`)
    REFERENCES `bd_ws`.`investigador` (`idinvestigador`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


SET SQL_MODE=@OLD_SQL_MODE;
SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS;
SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS;
