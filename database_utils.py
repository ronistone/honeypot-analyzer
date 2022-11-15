from typing import Union
import MySQLdb
from sqlescapy import sqlescape
from datetime import datetime
import multiprocessing


DATABASE_HOST = '127.0.0.1'
DATABASE_PORT = 3306
DATABASE_USER = 'root'
DATABASE_PASS = 'honeypot'
DATABASE_DB = 'honeypot'

DATABASE_FIELDNAME_OVERRIDE = {
    "key": "keyField",
    "outfile": "outfileField"
}

processing_pool = multiprocessing.Pool(24)

def connectToDatabase() -> MySQLdb.Connection:
    return MySQLdb.connect(
        host=DATABASE_HOST,
        user=DATABASE_USER, 
        passwd=DATABASE_PASS, 
        db=DATABASE_DB)


def format_insert_data(data):
    fields = []
    values = []
    for key in data.keys():
        fields.append(DATABASE_FIELDNAME_OVERRIDE[key] if DATABASE_FIELDNAME_OVERRIDE.get(key) else key)
        valueType = type(data[key])
        if(valueType == str):
            values.append(f"'{sqlescape(data[key])}'")
        elif(valueType == list):
            values.append(f"'{sqlescape(', '.join(data[key]))}'")
        elif(valueType == datetime):
            values.append(f"'{data[key]}'")
        else:
            values.append(str(data[key]))

    fieldsProcessed = ', '.join(fields)
    valuesProcessed = ', '.join(values)
    return fieldsProcessed,valuesProcessed

def executeInsert(data: Union[dict, list], table: str,  db: MySQLdb.Connection):
    cursor = db.cursor()
    
    try:
        if type(data) == list:
            # processing_pool.map(lambda d: doInsert(d, table, cursor), data)
            for d in data:
                doInsert(d, table, cursor)
        else:
            doInsert(data, table, cursor)
        db.commit()
        return True
    except Exception as e:
        print(e)
        db.rollback()
    return False

def saveLastCommit(commitSha: str, repositoryUrl: str, db: MySQLdb.Connection):
    executeInsert({'LAST_COMMIT_PROCESSED': commitSha, 'REPOSITORY_URL': repositoryUrl}, 'TOR_REPO_METADATA', db)

def getLastCommitProcessed(repositoryUrl: str, db: MySQLdb.Connection) -> str:
    sql = f"""
        SELECT LAST_COMMIT_PROCESSED FROM TOR_REPO_METADATA WHERE REPOSITORY_URL = '{repositoryUrl}' order by CREATED_AT desc limit 1;
    """
    result = executeQuery(sql, db)
    if result and len(result):
        return result[0]
    else:
        return None

def executeQuery(query, db: MySQLdb.Connection):
    cursor = db.cursor()
    try:
        cursor.execute(query)
        result =  cursor.fetchone()
        db.commit()
        return result
    except Exception as e:
        print(e)
        raise e
        

def doInsert(data, table, cursor):
    fieldsProcessed, valuesProcessed = format_insert_data(data)

    sql = f"""
                INSERT INTO {table}({fieldsProcessed}) VALUES ({valuesProcessed})
            """
    cursor.execute(sql)