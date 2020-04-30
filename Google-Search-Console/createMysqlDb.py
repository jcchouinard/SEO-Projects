# -*- coding: utf-8 -*-
"""
This Script will help create a mySQL database using Python.

@author: Jean-Christophe Chouinard: Technical SEO / Data Scientist. 
Twitter > https://www.twitter.com/ChouinardJC, 
LinkedIn > https://www.linkedin.com/in/jeanchristophechouinard/, 
Blog > https://www.jcchouinard.com/


Install packages: conda install -c anaconda pymysql
"""

import pymysql.cursors

# Create a mySQL Database
# Establish connection
connection = pymysql.connect(host='localhost',
                             user='root',
                             port='',
                             password='')

# Simulate the CREATE DATABASE function of mySQL
try:
    with connection.cursor() as cursor:
        cursor.execute('CREATE DATABASE gsc_db')

finally:
    connection.close()
    
    
# Create a table
connection = pymysql.connect(host='localhost',
                             user='root',
                             port='',
                             password='',
                             db='gsc_db',
                             cursorclass=pymysql.cursors.DictCursor)

try:
    with connection.cursor() as cursor:
        sqlQuery = '''CREATE TABLE IF NOT EXISTS backup_gsc(Date DATE, 
                                                            Page LONGTEXT, 
                                                            Query LONGTEXT, 
                                                            Clicks INT, 
                                                            Impressions INT, 
                                                            Ctr DECIMAL(10,2), 
                                                            Position DECIMAL(3,2))''' #Set-up the Schema datatype. DECIMAL(3,2) = 3 digits before the decimal, 2 after the decimal 
        cursor.execute(sqlQuery)
finally:
    connection.close()
    
    
