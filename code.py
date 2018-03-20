import json
from bs4 import BeautifulSoup
import urllib.request
import re

def getSqlType(data):
    if data == "timestamp":
        return "SQL_TIMESTAMP"
    elif data == "boolean":
        return "SQL_BIT"
    elif data == "string":
        return "SQL_VARCHAR"
    else:
        return "SQL_INTEGER"

def getSourceType(data):
    if(data[0] == '"'):
        data = data[1:-1]
    print(data)
    if re.match( r'(\d{4})-(\d\d)-(\d\d)T(\d\d):(\d\d):(\d\d.)$', data):
        return "timestamp"
    elif data == 'false' or data == 'true':
        return "boolean"
    elif data[0]>='a' and data[0]<='z':
        return "string"
    else:
        return "integer"

def makeFirstCapital(data):
    if str(data[0] == '"'):
        data = data[1:-1]
        if (data[0]>='a' and data[0]<='z') or (data[0]>='A' and data[0]<='Z'):
            return data.title()
    return data

tableName = str(input())
soup = BeautifulSoup(urllib.request.urlopen('https://developer.twitter.com/en/docs/ads/campaign-management/api-reference/' + tableName) , "html5lib")
div = soup.find(id = "get-accounts-account-id-" + tableName).find(id = "example-response")

value = []
start = False;

for val in div.find_all('span' , {'class' : ['s2', 'mi' , 'n', 'p']}):
    if start and not (val.get('class')[0] == "p" and val.text == ","):
        value.append(val)
    if(val.text == '"data"'):
        start = True

columnArray = []
virtualTable = []
stable = 0
i=0

while i<len(value):
    if value[i].text == "[" or value[i].text == "{":
        stable+=1
        i+=1
    elif value[i].text == "]," or value[i].text == "}," or value[i].text == "]" or value[i].text == "}":
        stable-=1
        i+=1
        if stable == 0:
            break
    elif value[i].text == ":":
        i+=1
    #print (str(value[i].text) +  " " + str(value[i+1].text) + " " + str(value[i+2].text)),
    elif value[i+2].text == "[],":
        print ("Currently Empty Virtual Table")
        i+=3
    elif value[i+2].text == "[":
        i+=1
        while (value[i+2].text) != "],":
            #print (value[i+2].text),
            i+=1
        #print ("]"),
        print ("some Fields in Virtual table")
        i+=3
    else:
        column = {}
        colName = makeFirstCapital(value[i].text)
        sourceType = getSourceType(value[i+2].text)
        sqlType = getSqlType(sourceType)
        passdownable = False
        column['Name'] = colName
        column['Metadata'] = {}
        column['Metadata']['SourceType'] = sourceType
        column['Metadata']['SQLType'] = sqlType
        if sqlType == "SQL_VARCHAR":
            column['Metadata']['Length'] = 255
        column["Nullable"] = False
        column["Updatable"] = True
        column["SvcRespAttr_ListResult"] = "data." + value[i].text
        column["SvcRespAttr_ItemResult"] = "data." + value[i].text
        column["SvcReqParam_QueryMapping"] = value[i].text
        columnArray.append(column)
        #print ("\n")
        i+=3

print ("test name " + columnArray[0]['Name'])
fs = open('columns.txt','w')
fs.write('{ "Columns" : [')
for obj in columnArray:
    #print(obj['Name'])
    fs.write(json.dumps(obj))
    fs.write(",")
fs.write("]}")
