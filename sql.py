import os
from dotenv import load_dotenv
import mysql.connector

load_dotenv()

sql_password=os.getenv("MY_SQL_PASSWORD")

try:
    mydb=mysql.connector.connect(
        host="localhost",
        user="root",
        password=sql_password,
        database="student"
    )
    cur=mydb.cursor()
    
    table_info='''
        create table if NOT EXISTS Student(Name varchar(25) PRIMARY KEY NOT NULL,Class varchar(25) NOT NULL,Section varchar(25),Age int NOT NULL)
        '''
    
    cur.execute(table_info)

    #Insert records

    cur.execute("insert into Student values('Krish','Data Science','A',90)")
    cur.execute("insert into Student values('John','Data Science','A',100)")
    cur.execute("insert into Student values('Mukesh','Data Science','B',86)")
    cur.execute("insert into Student values('Jacob','Devops','C',50)")
    cur.execute("insert into Student values('Dipesh','Devops','D',35)")

    print("The inserted records are:")
    cur.execute("Select * from Student")
    data=cur.fetchall()
    for row in data:
        print(row)
    mydb.commit()
    mydb.close()
except mysql.connector.Error as err:
    print(f"Error: {err}")