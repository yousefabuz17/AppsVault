# MacAppsVault

This Python script is designed to extract information about applications installed on a macOS system and store this information in a PostgreSQL database. The script serves as a personal tool to keep track of all installed applications. Please note that it is currently designed to run on macOS systems and may not work on other platforms.

## Table of Contents
- [Features](#features)
- [How it Works](#how-it-works)
    - [Scanning the /Applications Directory](#scanning-the-applications-directory)
    - [Extracting Application Information](#extracting-application-information)
    - [Connecting to the PostgreSQL Database](#connecting-to-the-postgresql-database)
    - [Closing the Database Connection](#closing-the-database-connection)
        - [Note](#note)
- [Results](#results)
- [Progress](#progress)

## Features
- Extracts application information from the Info.plist files of installed applications.
- Extracts the application name, version, minimum system version, and size.
    - Calculates the total file size by summing the sizes of all files within the applications contents.
    - Converts the size of applications to a human-readable format.
    - If minimum system version information is not available, the script sets it to `0` for better readability.
- Stores the extracted information in a PostgreSQL database.
- Prevents duplicate entries in the database.


## How it Works

The script operates through the following steps to gather and store application information:

#### Scanning the /Applications Directory
- The script begins by scanning the `/Applications` directory, collecting the paths of all `Info.plist` files. This file contains essential metadata about macOS applications.

#### Extracting Application Information
- Each `Info.plist` file is read, and the script extracts details such as the application name, version, minimum system version, and size. This information provides insights into the applications installed on the system.
- Calculates the total size of the application by summing the sizes of all files within the application contents. This step ensures that the total size of the application is accurate.

#### Connecting to the PostgreSQL Database
- The script establishes a connection to the PostgreSQL database using the credentials provided in the `config.json` file. This file contains the necessary information to establish a secure connection to the database.
- If the required tables do not already exist in the database, the script creates them. These tables are essential for storing the application information efficiently.
- Checks whether the application already exists in the database. This step ensures that duplicate entries are not inserted into the database.
- If the application does not exist in the database, the script inserts the extracted application information into the appropriate table. However, if the application already exists, the script updates the contents of the existing entry with the latest information. This approach ensures that the database remains up-to-date with the most recent application details.

#### Closing the Database Connection
- Once all the necessary operations are completed, the script closes the connection to the PostgreSQL database. Properly closing the connection is crucial for maintaining the integrity and security of the database.
    #### Note:
    - The script incorporates a mechanism to prevent duplicate entries in the database, ensuring data consistency.
    - In the case of an existing application, only the contents of the entry are updated, avoiding unnecessary duplication of information.
    - It is important to note that this script is specifically designed to work on macOS systems for now. Support for other operating systems may be added in the future.

## Results
![SQL DB](https://github.com/yousefabuz17/WeatherForecast/assets/68834704/e8db4cfe-1592-4898-8dd6-ddd7e2a819b6)

## Progress
- [x] Extract application information from Info.plist files.
- [x] Convert application size to a human-readable format.
- [x] Store application information in a PostgreSQL database.
- [x] Prevent duplicate entries in the database.
- [x] Update existing entries with the latest information.
- [ ] Add support for other operating systems.
- [ ] Add support for other database management systems.
