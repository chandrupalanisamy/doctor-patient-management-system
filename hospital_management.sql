-- phpMyAdmin SQL Dump
-- version 3.3.9
-- http://www.phpmyadmin.net
--
-- Host: localhost
-- Generation Time: Oct 31, 2025 at 07:43 AM
-- Server version: 5.5.8
-- PHP Version: 5.3.5

SET SQL_MODE="NO_AUTO_VALUE_ON_ZERO";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;

--
-- Database: `hospital_management`
--

-- --------------------------------------------------------

--
-- Table structure for table `admin`
--

CREATE TABLE IF NOT EXISTS `admin` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `username` varchar(50) NOT NULL,
  `password` varchar(255) NOT NULL,
  `latitude` varchar(20) DEFAULT NULL,
  `longitude` varchar(20) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB  DEFAULT CHARSET=latin1 AUTO_INCREMENT=2 ;

--
-- Dumping data for table `admin`
--

INSERT INTO `admin` (`id`, `username`, `password`, `latitude`, `longitude`) VALUES
(1, 'admin', 'admin', '10.358225311432397', '77.9845632');

-- --------------------------------------------------------

--
-- Table structure for table `allot_patient`
--

CREATE TABLE IF NOT EXISTS `allot_patient` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `patient_id` int(11) NOT NULL,
  `doctor_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `patient_id` (`patient_id`),
  KEY `doctor_id` (`doctor_id`)
) ENGINE=InnoDB  DEFAULT CHARSET=latin1 AUTO_INCREMENT=7 ;

--
-- Dumping data for table `allot_patient`
--

INSERT INTO `allot_patient` (`id`, `patient_id`, `doctor_id`) VALUES
(1, 1, 1),
(2, 1, 1),
(3, 1, 1),
(4, 3, 2),
(5, 1, 1),
(6, 4, 2);

-- --------------------------------------------------------

--
-- Table structure for table `doctor`
--

CREATE TABLE IF NOT EXISTS `doctor` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(100) NOT NULL,
  `email` varchar(100) NOT NULL,
  `password` varchar(255) NOT NULL,
  `mobile` varchar(20) NOT NULL,
  `specialist` varchar(100) NOT NULL,
  `latitude` varchar(20) DEFAULT NULL,
  `longitude` varchar(20) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `email` (`email`)
) ENGINE=InnoDB  DEFAULT CHARSET=latin1 AUTO_INCREMENT=6 ;

--
-- Dumping data for table `doctor`
--

INSERT INTO `doctor` (`id`, `name`, `email`, `password`, `mobile`, `specialist`, `latitude`, `longitude`) VALUES
(1, 'doctor 1', 'doctor1@gmail.com', '123', '9876542310', 'ortho', '10.3579648', '77.9845632'),
(2, 'Doctor2', 'doctor2@gmail.com', '123', '9876542310', 'skin', NULL, NULL),
(3, 'tester', 'tester2@gmail.com', '123', '9876542310', 'ortho', NULL, NULL),
(5, 'admin', 'tester@gmail.com', '123', '9876542310', 'liver', NULL, NULL);

-- --------------------------------------------------------

--
-- Table structure for table `nurse`
--

CREATE TABLE IF NOT EXISTS `nurse` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(100) NOT NULL,
  `email` varchar(100) NOT NULL,
  `password` varchar(255) NOT NULL,
  `mobile` varchar(20) NOT NULL,
  `key` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `email` (`email`)
) ENGINE=InnoDB  DEFAULT CHARSET=latin1 AUTO_INCREMENT=6 ;

--
-- Dumping data for table `nurse`
--

INSERT INTO `nurse` (`id`, `name`, `email`, `password`, `mobile`, `key`) VALUES
(1, 'nurse 1', 'nurse1@gmail.com', '123', '9876542310', '123'),
(2, 'Nurse2', 'ascentztech@gmail.com', '123', '9876542310', '171225'),
(3, 'kishore', 'employee1@gmail.com', '123', '9876542310', '171225'),
(5, 'admin', 'owner3@gmail.com', '123', '9876542310', '2004');

-- --------------------------------------------------------

--
-- Table structure for table `patient`
--

CREATE TABLE IF NOT EXISTS `patient` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(100) NOT NULL,
  `age` int(11) NOT NULL,
  `gender` varchar(10) NOT NULL,
  `email` varchar(100) DEFAULT NULL,
  `mobile` varchar(20) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB  DEFAULT CHARSET=latin1 AUTO_INCREMENT=5 ;

--
-- Dumping data for table `patient`
--

INSERT INTO `patient` (`id`, `name`, `age`, `gender`, `email`, `mobile`) VALUES
(1, 'pat 1', 54, 'Male', 'kamalesh@gmail.com', '9876542310'),
(2, 'admin', 54, 'Female', 'kamalesh@gmail.com', '9876542310'),
(3, 'admin', 54, 'Female', 'kamalesh@gmail.com', '9876542310'),
(4, 'kishore', 54, 'Female', 'ascentztech@gmail.com', '9876542310');

-- --------------------------------------------------------

--
-- Table structure for table `report`
--

CREATE TABLE IF NOT EXISTS `report` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `patient_id` int(11) NOT NULL,
  `temperature` varchar(10) DEFAULT NULL,
  `pulse_rate` varchar(10) DEFAULT NULL,
  `spo2` varchar(10) DEFAULT NULL,
  `height_cm` varchar(10) DEFAULT NULL,
  `weight_kg` varchar(10) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `patient_id` (`patient_id`)
) ENGINE=InnoDB  DEFAULT CHARSET=latin1 AUTO_INCREMENT=4 ;

--
-- Dumping data for table `report`
--

INSERT INTO `report` (`id`, `patient_id`, `temperature`, `pulse_rate`, `spo2`, `height_cm`, `weight_kg`) VALUES
(1, 1, '98 c', '120', '95%', '165', '60'),
(2, 2, '98 c', '120', '95%', '165', '60'),
(3, 2, '98 c', '120', '95%', '165', '60');

-- --------------------------------------------------------

--
-- Table structure for table `report_enc`
--

CREATE TABLE IF NOT EXISTS `report_enc` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `report_id` int(11) NOT NULL,
  `nurse_id` int(11) NOT NULL,
  `enc_temperature` text,
  `enc_pulse_rate` text,
  `enc_spo2` text,
  `enc_height_cm` text,
  `enc_weight_kg` text,
  PRIMARY KEY (`id`),
  KEY `report_id` (`report_id`),
  KEY `nurse_id` (`nurse_id`)
) ENGINE=InnoDB  DEFAULT CHARSET=latin1 AUTO_INCREMENT=4;

--
-- Dumping data for table `report_enc`
--

INSERT INTO `report_enc` (`id`, `report_id`, `nurse_id`, `enc_temperature`, `enc_pulse_rate`, `enc_spo2`, `enc_height_cm`, `enc_weight_kg`) VALUES
(1, 1, 1, 'gAAAAABpBER2LvCpL2BDWD_xulxF0LadIHF6b9FUCYViqoUs9q6qBiJsOUh0lEEn5mX9ILoQtzkzv4cbU8fgMMBD7LaNhnXJDA==', 'gAAAAABpBER29mMZIAo86MpZDJNqKZDFxL9-wHP4RXo08xC4XqDghtLF6D6v1IlGRrG9rfN8PZ0KF5x_GHaj2Z3pvDfwY85DkQ==', 'gAAAAABpBER2LGh68FcXOIPBjZT8Y3MykkYKXAb-YaXmXl_HswHlKt5BLwdHbyljRIJL7OuOHgrZ3L7TeNgDBMVNeQdzVm_eLg==', 'gAAAAABpBER2s_VW7uJ9gEkiDznJLIjgT9O67h8zTDHXY8Hh0S38AVmHi2ehLSXFRISLnLxsoihuQJDgMh5RBQfsUjQkZzkYYQ==', 'gAAAAABpBER2ycJN8apObStV6112vZb9kId8QFpTyMailV6zTKsqhHlX2k4it5H2MYJaD4bMoS2aL2ZNG8JGl5GR0lefh8_Rhg=='),
(2, 1, 1, 'gAAAAABpBER7Zodc48Bs4WdygKrjYZO-u713riq_7Rc8kq91JU4piX0_01L6imsgkO5xl1BqkGCy7_ZkWbP3jcXrpDnsqeEEqw==', 'gAAAAABpBER76zLLYih43uyAwKU382wap3ZdBj-pLczlNeVWVUJA6Kbdz5ngkTC-3-8zwgQaSoDc9Q75OdtGmuZGbV0tjufDBg==', 'gAAAAABpBER7POCUObcqyovVHrT3qL-yfJfmt_R9ClzgHumQcpJyqZJ0RtCQlPhetY9qZp6iMWaSz4Iz4WG3U8loYz2S67K-wA==', 'gAAAAABpBER78DRtKamS1KNogp49qQKng3uk37Ln97qsgjSeBcu64T8rc-axhw-K_eCXY9EpWtxJjNvOkdG4SXpk2X1bdFodww==', 'gAAAAABpBER7hiCbJwIAHP6t108P8EXuo3knTTVWzbSNl3I6HGhqHFKE3Y4hrXv1Q1ILYG1M1oS37WHZC4m8HsEM4RamsfInuQ=='),
(3, 1, 1, 'gAAAAABpBESV2sLXHYXdXxEI1u33tF7d_y4ATpsqYsaT6hYMDMoID4vmDkoTvvNrMYlYp_WCjgwTtWlH3I_aPKkE35mbitRs9Q==', 'gAAAAABpBESVxas1p7JmCvBc2o-MX5StvLZ6husVM1tKCrtIcCk0cUrZiF07iX9DgDQPykN4V8fQGTYK75XS0JRA_Xml8U6WuA==', 'gAAAAABpBESV2_1gU8fGd0dW6qL-x57QT73dTAt5Y4BAJiK8WW6LqpNLZQzpTo_akZQqwuUYjIT4LBLbGnFRL3cGvwKE7AffdQ==', 'gAAAAABpBESVBFNzThiYDJDf_-6_jOHABTCk7KC64t36u8Xrhpp9bBqayeC3cIC73UrCfSBsv8wTd-huR6Hk2PolMQGN_rIJBA==', 'gAAAAABpBESVPzy77XdSqL_oXGQcF08hIv0RaFdGNqV71dOUZrPept0GkCcrMAa2yzFzWuP_FByRBAkzfbCPt83p73oQAbeHPQ==');

--
-- Constraints for dumped tables
--

--
-- Constraints for table `allot_patient`
--
ALTER TABLE `allot_patient`
  ADD CONSTRAINT `allot_patient_ibfk_1` FOREIGN KEY (`patient_id`) REFERENCES `patient` (`id`),
  ADD CONSTRAINT `allot_patient_ibfk_2` FOREIGN KEY (`doctor_id`) REFERENCES `doctor` (`id`);

--
-- Constraints for table `report`
--
ALTER TABLE `report`
  ADD CONSTRAINT `report_ibfk_1` FOREIGN KEY (`patient_id`) REFERENCES `patient` (`id`);

--
-- Constraints for table `report_enc`
--
ALTER TABLE `report_enc`
  ADD CONSTRAINT `report_enc_ibfk_1` FOREIGN KEY (`report_id`) REFERENCES `report` (`id`),
  ADD CONSTRAINT `report_enc_ibfk_2` FOREIGN KEY (`nurse_id`) REFERENCES `nurse` (`id`);
