-- the SQL to generate the code for SCHub
-- version: 1.0.0
-- date:    December 2018

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
SET AUTOCOMMIT = 0;
START TRANSACTION;
SET time_zone = "+00:00";


-- Creating the database 'SCHub'

CREATE DATABASE IF NOT EXISTS `SCHub`
  DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci;
USE `SCHub`;


-- --------------------------------------------------------
-- Table to store data about the system users

CREATE TABLE `users`
(
  `id`              int(11)      NOT NULL AUTO_INCREMENT,
  `first_name`      varchar(255) NOT NULL,
  `second_name`     varchar(255) NOT NULL,
  `email`           varchar(255) NOT NULL,
  `password`        varchar(255) NOT NULL,
  `date_registered` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (id)
) ENGINE = InnoDB;


-- --------------------------------------------------------
-- Table for the list of projects

CREATE TABLE `projects`
(
  `id`          int(11)      NOT NULL AUTO_INCREMENT,
  `name`        varchar(255) NOT NULL,
  `description` text         NULL,
  `owner`       int(11)      NOT NULL,
  `status`      ENUM ('active', 'archived') DEFAULT 'active',
  `date_added`  datetime                    DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  FOREIGN KEY (`owner`) REFERENCES `users` (`id`)
    ON DELETE RESTRICT
    ON UPDATE CASCADE
) ENGINE = InnoDB;


-- --------------------------------------------------------
-- Table of contributors for each project

CREATE TABLE `contributors`
(
  `project_id`  int(11) NOT NULL,
  `user_id`     int(11) NOT NULL,
  `permissions` ENUM ('read', 'write', 'manage') DEFAULT 'read',
  PRIMARY KEY (`project_id`, `user_id`),
  FOREIGN KEY (`project_id`) REFERENCES `projects` (`id`)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  FOREIGN KEY (`user_id`) REFERENCES `users` (`id`)
    ON DELETE CASCADE
    ON UPDATE CASCADE
) ENGINE = InnoDB;


-- --------------------------------------------------------
-- Table to store the test for each project

CREATE TABLE `tests`
(
  `project_id` int(11)      NOT NULL,
  `name`       varchar(255) NOT NULL,
  `code`       text         NOT NULL,
  `date_added` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`project_id`, `name`),
  FOREIGN KEY (`project_id`) REFERENCES `projects` (`id`)
    ON DELETE CASCADE
    ON UPDATE CASCADE
) ENGINE = InnoDB;


-- --------------------------------------------------------
-- Creating the table to store revision
CREATE TABLE revisions
(
  project_id     INTEGER,
  revision_id    INTEGER      NOT NULL,
  contributor_id INTEGER,
  comment        TEXT         NOT NULL,
  diff           TEXT         NOT NULL,
  tag            VARCHAR(255) NULL,
  date_added     DATETIME DEFAULT NOW(),
  PRIMARY KEY (project_id, revision_id),
  FOREIGN KEY (project_id) REFERENCES projects (id)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  FOREIGN KEY (contributor_id) REFERENCES users (id)
);


-- --------------------------------------------------------
-- Creating table for releases
CREATE TABLE releases
(
  project_id   INTEGER,
  revision_id  INTEGER,
  name         VARCHAR(255) NOT NULL,
  notes        TEXT,
  date_created DATETIME DEFAULT NOW(),
  PRIMARY KEY (project_id, revision_id, name),
  FOREIGN KEY (project_id, revision_id)
    REFERENCES revisions (project_id, revision_id)
    ON DELETE CASCADE ON UPDATE CASCADE
);


-- --------------------------------------------------------
-- Creating table for issues
CREATE TABLE issues
(
  project_id   INTEGER,
  issue_id     INTEGER,
  name         VARCHAR(255) NOT NULL,
  description  TEXT,
  status       ENUM ('new', 'resolved', 'closed') DEFAULT 'new',
  date_created DATETIME                           DEFAULT NOW(),
  PRIMARY KEY (project_id, issue_id),
  FOREIGN KEY (project_id)
    REFERENCES projects (id)
    ON DELETE CASCADE
    ON UPDATE CASCADE
);


-- --------------------------------------------------------
-- Creating table for issues
CREATE TABLE issue_comments
(
  project_id   INTEGER,
  issue_id     INTEGER,
  comment_id   INTEGER,
  title        VARCHAR(255) NOT NULL,
  comment      TEXT,
  commenter    INTEGER,
  date_created DATETIME DEFAULT NOW(),
  PRIMARY KEY (project_id, issue_id, comment_id),
  FOREIGN KEY (project_id, issue_id)
    REFERENCES issues (project_id, issue_id)
    ON DELETE CASCADE ON UPDATE CASCADE,
  FOREIGN KEY (commenter)
    REFERENCES users (id)
    ON DELETE CASCADE ON UPDATE CASCADE
);


-- --------------------------------------------------------
  -- Creating a function to return the last issue id
CREATE FUNCTION new_issue_id(proj_id INTEGER)
  RETURNS INTEGER DETERMINISTIC
BEGIN
  DECLARE last_id INTEGER;

  SET last_id = (SELECT MAX(issue_id)
                 FROM issues
                 WHERE project_id = proj_id
                 GROUP BY project_id) + 1;

  RETURN last_id;
END;


-- --------------------------------------------------------
  -- Creating a function to return the last issue comment id
CREATE FUNCTION new_issue_comment_id(proj_id INTEGER, iss_id INTEGER)
  RETURNS INTEGER DETERMINISTIC
BEGIN
  DECLARE last_id INTEGER;

  SET last_id = (SELECT MAX(issue_id)
                 FROM issue_comments
                 WHERE project_id = proj_id
                   AND issue_id = iss_id
                 GROUP BY project_id) + 1;

  RETURN last_id;
END;