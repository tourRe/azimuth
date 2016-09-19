from __future__ import print_function
#!/usd/bin/env python3
import mysql.connector
from mysql.connector import errorcode

# DEFINING DATABASE CONFIG
config_accounts = {
        'user': 'azimuth3_alex',
        'password': 'Songo2016',
        'host': 'box1164.bluehost.com',
        'database': 'azimuth3_accounts'}

config_payments = {
        'user': 'azimuth3_alex',
        'password': 'Songo2016',
        'host': 'www.azimuth-solar.com',
        'database': 'azimuth3_payments'}

DB_NAME = 'azimuth3_payments'

# ESTABLISHING A CONNECTION
try:
    cnx = mysql.connector.connect(**config_payments)
    cursor = cnx.cursor()

except mysql.connector.Error as err:
    if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
        print("Something is wrong with your user name or password")
    elif err.errno == errorcode.ER_BAD_DB_ERROR:
        print("Database does not exist")
    else:
        print(err)

# DEFINING TEST TABLES
TABLES = {}

TABLES['accounts'] = (
        "CREATE TABLE `accounts` ("
        "  `account_no` int(11) NOT NULL AUTO_INCREMENT,"
        "  `account_GLP` int(7) NOT NULL,"
        "  `account_Angaza` varchar(8) NOT NULL,"
        "  `client_id` int(11) NOT NULL,"
        "  `plan` varchar(20) NOT NULL,"
        "  `reg_date` date NOT NULL,"
        "  `reg_agent` varchar(30) NOT NULL,"
        "  `paid` int(10) NOT NULL,"
        "  `paid_thisMonth` int(10) NOT NULL,"
        "  `paid_expect` int(10) NOT NULL,"
        "  `paid_expect_thisMonth_eom` int(10) NOT NULL,"
        "  `paid_expect_thisMonth_today` int(10) NOT NULL,"
        "  `payment_deficit` int(10) NOT NULL,"
        "  `payment_deficit_thisMonth` int(10) NOT NULL,"
        "  `lastPay_date` date NOT NULL,"
        "  `lastPay_amount` int(10) NOT NULL,"
        "  `lastlastPay_date` date,"
        "  `lastlastPay_amount` int(10),"
        "  `pay_count` int(3) NOT NULL,"
        "  `pay_count_thisMonth` int(3) NOT NULL,"
        "  `sPoints` int(2) NOT NULL,"
        "  `sPoints_thisMonth` int(2) NOT NULL,"
        "  `next_disable` date NOT NULL,"
        "  `credit` int(3) NOT NULL,"
        "  `unlocked_thisMonth` int(1) NOT NULL,"
        "  `writeOff_date` date,"
        "  `status` enum('active','disabled','unlocked','written_off') NOT NULL,"
        "  PRIMARY KEY (`account_no`)"
        ") ENGINE=InnoDB")

TABLES['employees'] = (
        "CREATE TABLE `employees` ("
        "  `emp_no` int(11) NOT NULL AUTO_INCREMENT,"
        "  `birth_date` date NOT NULL,"
        "  `first_name` varchar(14) NOT NULL,"
        "  `last_name` varchar(16) NOT NULL,"
        "  `gender` enum('M','F') NOT NULL,"
        "  `hire_date` date NOT NULL,"
        "  PRIMARY KEY (`emp_no`)"
        ") ENGINE=InnoDB")

TABLES['departments'] = (
        "CREATE TABLE `departments` ("
        "  `dept_no` char(4) NOT NULL,"
        "  `dept_name` varchar(40) NOT NULL,"
        "  PRIMARY KEY (`dept_no`), UNIQUE KEY `dept_name` (`dept_name`)"
        ") ENGINE=InnoDB")

TABLES['salaries'] = (
        "CREATE TABLE `salaries` ("
        "  `emp_no` int(11) NOT NULL,"
        "  `salary` int(11) NOT NULL,"
        "  `from_date` date NOT NULL,"
        "  `to_date` date NOT NULL,"
        "  PRIMARY KEY (`emp_no`,`from_date`), KEY `emp_no` (`emp_no`),"
        "  CONSTRAINT `salaries_ibfk_1` FOREIGN KEY (`emp_no`) "
        "     REFERENCES `employees` (`emp_no`) ON DELETE CASCADE"
        ") ENGINE=InnoDB")

TABLES['dept_emp'] = (
        "CREATE TABLE `dept_emp` ("
        "  `emp_no` int(11) NOT NULL,"
        "  `dept_no` char(4) NOT NULL,"
        "  `from_date` date NOT NULL,"
        "  `to_date` date NOT NULL,"
        "  PRIMARY KEY (`emp_no`,`dept_no`), KEY `emp_no` (`emp_no`),"
        "  KEY `dept_no` (`dept_no`),"
        "  CONSTRAINT `dept_emp_ibfk_1` FOREIGN KEY (`emp_no`) "
        "     REFERENCES `employees` (`emp_no`) ON DELETE CASCADE,"
        "  CONSTRAINT `dept_emp_ibfk_2` FOREIGN KEY (`dept_no`) "
        "     REFERENCES `departments` (`dept_no`) ON DELETE CASCADE"
        ") ENGINE=InnoDB")

TABLES['dept_manager'] = (
        "  CREATE TABLE `dept_manager` ("
        "  `dept_no` char(4) NOT NULL,"
        "  `emp_no` int(11) NOT NULL,"
        "  `from_date` date NOT NULL,"
        "  `to_date` date NOT NULL,"
        "  PRIMARY KEY (`emp_no`,`dept_no`),"
        "  KEY `emp_no` (`emp_no`),"
        "  KEY `dept_no` (`dept_no`),"
        "  CONSTRAINT `dept_manager_ibfk_1` FOREIGN KEY (`emp_no`) "
        "     REFERENCES `employees` (`emp_no`) ON DELETE CASCADE,"
        "  CONSTRAINT `dept_manager_ibfk_2` FOREIGN KEY (`dept_no`) "
        "     REFERENCES `departments` (`dept_no`) ON DELETE CASCADE"
        ") ENGINE=InnoDB")

TABLES['titles'] = (
        "CREATE TABLE `titles` ("
        "  `emp_no` int(11) NOT NULL,"
        "  `title` varchar(50) NOT NULL,"
        "  `from_date` date NOT NULL,"
        "  `to_date` date DEFAULT NULL,"
        "  PRIMARY KEY (`emp_no`,`title`,`from_date`), KEY `emp_no` (`emp_no`),"
        "  CONSTRAINT `titles_ibfk_1` FOREIGN KEY (`emp_no`)"
        "     REFERENCES `employees` (`emp_no`) ON DELETE CASCADE"
        ") ENGINE=InnoDB")

# CREATING THE DATABASE
def create_database(cursor):
    try:
        cursor.execute(
                "CREATE DATABASE {} DEFAULT CHARACTER SET 'utf8'".format(DB_NAME))
    except mysql.connector.Error as err:
        print("Failed creating database: {}".format(err))
        exit(1)

try:
    cnx.database = DB_NAME
except mysql.connector.Error as err:
    if err.errno == errorcode.ER_BAD_DB_ERROR:
        create_database(cursor)
        cnx.database = DB_NAME
    else:
        print(err)
        exit(1)

for name, ddl in TABLES.items():
    try:
        print("Creating table {}: ".format(name), end='')
        cursor.execute(ddl)
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_TABLE_EXISTS_ERROR:
            print("already exists.")
        else:
            print(err.msg)
    else:
        print("OK")
cursor.close()
cnx.close()
