-- MySQL dump 10.13  Distrib 5.6.10, for osx10.8 (x86_64)
--
-- Host: 127.0.0.1    Database: evopminer
-- ------------------------------------------------------
-- Server version	5.6.10-log

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `CleanedSentences`
--

CREATE DATABASE evopminer;

use evopminer;


DROP TABLE IF EXISTS `CleanedSentences`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `CleanedSentences` (
  `ProdDateSentHash` varchar(255) NOT NULL,
  `Product` text NOT NULL,
  `sentence` text NOT NULL,
  `Date` datetime NOT NULL,
  PRIMARY KEY (`ProdDateSentHash`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `GroundTruth`
--

DROP TABLE IF EXISTS `GroundTruth`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `GroundTruth` (
  `ProdDateSentHash` varchar(255) NOT NULL,
  `Feature` varchar(255) NOT NULL,
  `Label` text NOT NULL,
  PRIMARY KEY (`ProdDateSentHash`,`Feature`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `HybridCars`
--

DROP TABLE IF EXISTS `HybridCars`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `HybridCars` (
  `BaseSite` text NOT NULL,
  `Content` text NOT NULL,
  `Title` text NOT NULL,
  `Url` varchar(255) NOT NULL,
  `Body` text,
  `NumComments` int(11) NOT NULL,
  `Comments` text,
  PRIMARY KEY (`Url`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `LeafReviews`
--

DROP TABLE IF EXISTS `LeafReviews`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `LeafReviews` (
  `BaseSite` text NOT NULL,
  `Content` text NOT NULL,
  `Title` text NOT NULL,
  `Url` varchar(255) NOT NULL,
  `NumComments` int(11) NOT NULL,
  `Comments` text NOT NULL,
  PRIMARY KEY (`Url`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `Results`
--

DROP TABLE IF EXISTS `Results`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `Results` (
  `ProdDateSentHash` varchar(255) NOT NULL DEFAULT '-1',
  `Feature` varchar(255) NOT NULL,
  `Label` text NOT NULL,
  `Num` int(11) NOT NULL,
  `Outof` int(11) NOT NULL,
  PRIMARY KEY (`ProdDateSentHash`,`Feature`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `TeslaReviews`
--

DROP TABLE IF EXISTS `TeslaReviews`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `TeslaReviews` (
  `BaseSite` text NOT NULL,
  `Content` text NOT NULL,
  `Title` text NOT NULL,
  `Url` varchar(255) NOT NULL,
  `NumComments` int(11) NOT NULL,
  `Comments` text NOT NULL,
  PRIMARY KEY (`Url`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `VoltReviews`
--

DROP TABLE IF EXISTS `VoltReviews`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `VoltReviews` (
  `BaseSite` text NOT NULL,
  `Content` text NOT NULL,
  `Title` text NOT NULL,
  `Url` varchar(255) NOT NULL,
  `NumComments` int(11) NOT NULL,
  `Comments` text NOT NULL,
  PRIMARY KEY (`Url`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2014-07-15 20:49:02
