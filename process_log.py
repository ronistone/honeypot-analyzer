
import json
from .database_utils import connectToDatabase, executeInsert


logs = []

while True:
    try:
        log = input()
        log = json.loads(log)
        # print(log)
        logs.append(log)
    except Exception as e:
        # print(e)
        break

allFields = {}
fields = []

biggiestField = -1
biggiestFieldName = None

db = connectToDatabase()


for log in logs:
    executeInsert(log, db)
    for field in log.keys():
        if allFields.get(field) is not True:
            allFields[field] = True
            fieldValueType = type(log[field])
            fields.append((field, fieldValueType))
            if(fieldValueType == str):
                if len(log[field]) > biggiestField:
                    biggiestField = len(log[field])
                    biggiestFieldName = field
            if(fieldValueType == list):
                for value in log[field]:
                    if type(value) is not str:
                        print("List has value without str type: ", value, " field -> ", field)

fields.sort()
print("Logs list size: ",len(logs))
print("Size of all fields:", len(fields))
print("All fields in log:", fields)
print("The biggiest field is: ", biggiestFieldName, " with size ", biggiestField)


db.close()
