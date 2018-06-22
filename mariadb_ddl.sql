DROP TABLE IF EXISTS `tesco` CASCADE;

CREATE TABLE `tesco` (
  `guid` varchar(36) NOT NULL DEFAULT '',
  `productid` bigint(20) DEFAULT NULL,
  `productdesc` varchar(255) DEFAULT NULL,
  `offerdesc` varchar(255) DEFAULT NULL,
  `validitydesc` varchar(255) DEFAULT NULL,
  `imgsrc90` varchar(255) DEFAULT NULL,
  `imgsrc110` varchar(255) DEFAULT NULL,
  `imgsrc225` varchar(255) DEFAULT NULL,
  `imgsrc540` varchar(255) DEFAULT NULL,
  `ins_ts` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`guid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE DEFINER=`offeruser`@`%` TRIGGER tesco_insert BEFORE INSERT ON `tesco`
FOR EACH ROW
BEGIN
SET NEW.guid = UUID();
END;

DROP TABLE IF EXISTS `sains` CASCADE;

CREATE TABLE `sains` (
  `guid` varchar(36) NOT NULL DEFAULT '',
  `productid` bigint(20) DEFAULT NULL,
  `productdesc` varchar(255) DEFAULT NULL,
  `producturl` varchar(255) DEFAULT NULL,
  `imgsrcl` varchar(255) DEFAULT NULL,
  `offerdesc` varchar(255) DEFAULT NULL,
  `priceunit` varchar(30) DEFAULT NULL,
  `ins_ts` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`guid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE DEFINER=`offeruser`@`%` TRIGGER sains_insert BEFORE INSERT ON `sains`
FOR EACH ROW
BEGIN
SET NEW.guid = UUID();
END;

DROP TABLE IF EXISTS `occad` CASCADE;

CREATE TABLE `occad` (
  `guid` varchar(36) NOT NULL DEFAULT '',
  `productdesc` varchar(255) DEFAULT NULL,
  `producturl` varchar(255) DEFAULT NULL,
  `offerdesc` varchar(255) DEFAULT NULL,
  `offerurl` varchar(255) DEFAULT NULL,
  `imgsrcl` varchar(255) DEFAULT NULL,
  `unitprice` varchar(50) DEFAULT NULL,
  `productprice` varchar(50) DEFAULT NULL,
  `ins_ts` datetime DEFAULT CURRENT_TIMESTAMP,
  `productid` bigint(20) DEFAULT NULL,
  PRIMARY KEY (`guid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE DEFINER=`offeruser`@`%` TRIGGER occad_insert BEFORE INSERT ON `occad`
FOR EACH ROW
BEGIN
SET NEW.guid = UUID();
END;

DROP TABLE IF EXISTS `morri` CASCADE;

CREATE TABLE `morri` (
  `guid` varchar(36) NOT NULL DEFAULT '',
  `productdesc` varchar(255) DEFAULT NULL,
  `producturl` varchar(255) DEFAULT NULL,
  `offerdesc` varchar(255) DEFAULT NULL,
  `offerurl` varchar(255) DEFAULT NULL,
  `imgsrcl` varchar(255) DEFAULT NULL,
  `unitprice` varchar(50) DEFAULT NULL,
  `productprice` varchar(50) DEFAULT NULL,
  `ins_ts` datetime DEFAULT CURRENT_TIMESTAMP,
  `productid` bigint(20) DEFAULT NULL,
  PRIMARY KEY (`guid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE DEFINER=`offeruser`@`%` TRIGGER morri_insert BEFORE INSERT ON `morri`
FOR EACH ROW
BEGIN
SET NEW.guid = UUID();
END;

DROP TABLE IF EXISTS `asda` CASCADE;

CREATE TABLE `asda` (
  `guid` varchar(36) NOT NULL DEFAULT '',
  `producturl` varchar(255) DEFAULT NULL,
  `promodetail` varchar(255) DEFAULT NULL,
  `shelfid` bigint DEFAULT NULL,
  `name` varchar(255) DEFAULT NULL,
  `scene7assetid`  bigint DEFAULT NULL,
  `largeimage`  varchar(255) DEFAULT NULL,
  `promodetailfull` varchar(255) DEFAULT NULL,
  `imageurl` varchar(255) DEFAULT NULL,
  `deptid` bigint DEFAULT NULL,
  `deptname` varchar(255) DEFAULT NULL,
  `wasprice` varchar(15) DEFAULT NULL,
  `shelfname` varchar(255) DEFAULT NULL,
  `id` bigint DEFAULT NULL,
  `category` varchar(50) DEFAULT NULL,
  `price` varchar(15) DEFAULT NULL,
  `brandname` varchar(255) DEFAULT NULL,
  `thumbnailimage` varchar(255) DEFAULT NULL,
  `priceperuom` varchar(15) DEFAULT NULL,
  `ins_ts` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`guid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE DEFINER=`offeruser`@`%` TRIGGER asda_insert BEFORE INSERT ON `asda`
FOR EACH ROW
BEGIN
SET NEW.guid = UUID();
END;
