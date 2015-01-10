
DROP TABLE IF EXISTS `users`;
CREATE TABLE `users` (
	`uid` MEDIUMINT(8) unsigned NOT NULL AUTO_INCREMENT,
	`username` varchar(140) NOT NULL,
	`real_name` varchar(140) NOT NULL,
	`email` VARCHAR(140) NOT NULL,
	`password` CHAR(56) NOT NULL,
	`bio` text NOT NULL,
  	`status` enum('inactive','active') NOT NULL,
  	`role` enum('administrator','editor','user') NOT NULL,

	PRIMARY KEY (`uid`),
	UNIQUE KEY (`email`)

) ENGINE=InnoDB DEFAULT CHARSET=utf8;


DROP TABLE IF EXISTS `posts`;
CREATE TABLE `posts` (
  `pid` int(6) NOT NULL AUTO_INCREMENT,
  `title` varchar(150) NOT NULL,
  `slug` varchar(150) NOT NULL,
  `description` text NOT NULL,
  `html` text NOT NULL,
  `css` text NOT NULL,
  `js` text NOT NULL,
  `created` datetime NOT NULL,
  `author` int(6) NOT NULL,
  `category` int(6) NOT NULL,
  `status` enum('draft','published','archived') NOT NULL,
  `comments` tinyint(1) NOT NULL,

  PRIMARY KEY (`pid`),
  KEY `status` (`status`),
  KEY `slug` (`slug`)
) ENGINE=InnoDB CHARSET=utf8;