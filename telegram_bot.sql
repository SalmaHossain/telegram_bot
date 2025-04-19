-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: Apr 18, 2025 at 02:19 PM
-- Server version: 10.4.32-MariaDB
-- PHP Version: 8.2.12

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `telegram_bot`
--

-- --------------------------------------------------------

--
-- Table structure for table `users`
--

CREATE TABLE `users` (
  `id` int(11) NOT NULL,
  `email` varchar(255) NOT NULL,
  `password` varchar(255) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `users`
--

INSERT INTO `users` (`id`, `email`, `password`) VALUES
(18, 'ahmed.jovan2000@gmail.com', 'scrypt:32768:8:1$ssf9Qyk5hB1dwtrg$5ce89683697fcf434ca687f00d76cfeac58519ac7ebc8d018309ecd66d174c0fde8d86fcd58562de3d525f8159f8b0513043064ab713e0b8bf809b5f77420bc4'),
(19, 'sharmin.laila1999@gmail.com', 'scrypt:32768:8:1$2sCaEF97V0KWZ2L2$9ed624366a35de0b6fc83b050ce25df2c64e8640eda66711608898b2919140ead8c42f8d5ab36cdcbed98b19f9cafe3a8d0dbaf77c2f6d05757317ba56c150c0'),
(20, 'dummyuser.000111@gmail.com', 'scrypt:32768:8:1$Lje758awunl0VD0H$f63575834f75dcb7f4723cfb0436ade2d5fb47c5c6ada1a5a08c607934b10e4e208ec9e07b9799c8ee9ae73d41e5edb8f97ebd58b27181acc894a08cf7c96077');

--
-- Indexes for dumped tables
--

--
-- Indexes for table `users`
--
ALTER TABLE `users`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `email` (`email`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `users`
--
ALTER TABLE `users`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=21;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
