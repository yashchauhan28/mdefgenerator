import json
from bs4 import BeautifulSoup
import urllib.request
import re
import sys

def makeName(data):
    newData = ""
    for i in range(len(data)):
        if (data[i]>='a' and data[i]<='z') or (data[i]<='A' and data[i]>='Z'):
            newData += data[i]
    return newData.title()

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
    #print(data)
    if re.match( r'(\d{4})-(\d\d)-(\d\d)T(\d\d):(\d\d):(\d\d.)$', data):
        return "timestamp"
    elif data == 'false' or data == 'true':
        return "boolean"
    elif data[0]>='a' and data[0]<='z':
        return "string"
    else:
        return "integer"

def makeFirstCapital(data,flag=True):
    if str(data[0] == '"'):
        data = data[1:-1]
        if (data[0]>='a' and data[0]<='z') or (data[0]>='A' and data[0]<='Z'):
            if flag:
                return data.title()
    return data
if __name__ == '__main__':
    tables = []
    tableList = []
    # while True:
    #     inp = str(input())
    #     if inp != "-1":
    #         tableList.append(inp)
    #     else:
    #         break
    tableList = [line.rstrip('\n') for line in open('inputs.txt')]
    for tableName in tableList:
        blocks = tableName.split(" ")
        tableName = blocks[0]
        divId = ""
        if len(blocks) > 1:
            divId = blocks[1]
        #print(tableName,divId)
        soup = BeautifulSoup(urllib.request.urlopen('https://developer.twitter.com/en/docs/ads/campaign-management/api-reference/' + tableName) , "html5lib")
        if divId == "" :
            div = soup.find(id = tableName).find(id = "example-response")
        else :
            div = soup.find(id = divId).find(id = "example-response")
        value = []
        start = False;

        for val in div.find_all('span' , {'class' : ['s2', 'mi' , 'n', 'p', 'o']}):
            if start and not (val.get('class')[0] == "p" and val.text == ","):
                value.append(val)
            if(val.text == '"data"'):
                start = True

        columnArray = []
        virtualTableArray = []
        stable = 0
        i=0

        while i<len(value):
            if value[i].text == ",":
                i+=1
            elif value[i].text == "[" or value[i].text == "{":
                stable+=1
                i+=1
            elif value[i].text == "]," or value[i].text == "}," or value[i].text == "]" or value[i].text == "}":
                stable-=1
                i+=1
                if stable == 0:
                    break
            elif value[i].text == ":":
                i+=1
            elif value[i+2].text == "[],":
                virtualTable = {}
                virtualTable['TableName'] = makeName(tableName) + "_" + makeName(value[i].text)
                virtualTable['SvcRespAttr_ListResult'] = "data." + makeFirstCapital(value[i].text)
                virtualTable['SvcRespAttr_ItemResult'] = "data." + makeFirstCapital(value[i].text)
                virtualTable['PKeyColumn'] = {}
                virtualTable['PKeyColumn']['pk_Reasons_Not_Servable'] = []
                pkDict = {'PKColumnName' : 'Id' , 'RelatedFKColumns' : []}
                virtualTable['PKeyColumn']['pk_Reasons_Not_Servable'].append(pkDict)
                column['FKeyColumn'] = []
                column['Columns'] = []
                virtualTableArray.append(virtualTable)
                i+=3
            elif value[i+2].text == "[":
                virtualTable = {}
                virtualTable['TableName'] = makeName(tableName) + "_" + makeName(value[i].text)
                virtualTable['SvcRespAttr_ListResult'] = "data." + makeFirstCapital(value[i].text,False)
                virtualTable['SvcRespAttr_ItemResult'] = "data." + makeFirstCapital(value[i].text,False)
                virtualTable['PKeyColumn'] = {}
                virtualTable['PKeyColumn']['pk_Reasons_Not_Servable'] = []
                pkDict = {'PKColumnName' : 'Id' , 'RelatedFKColumns' : []}
                virtualTable['PKeyColumn']['pk_Reasons_Not_Servable'].append(pkDict)
                column['FKeyColumn'] = []
                column['Columns'] = []
                virtualTableArray.append(virtualTable)
                i+=1
                while (value[i+2].text) != "]," and value[i+2].text != "]":
                    i+=1
                i+=3
            elif value[i+2].text == "{":
                stable+=1
                parentColumnName = makeFirstCapital(value[i].text,False)
                i+=3
                while(value[i].text!='}' and value[i].text!='},'):
                    column = {}
                    colName = parentColumnName.title() + "_" + makeFirstCapital(value[i].text)
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
                    column["SvcRespAttr_ListResult"] = "data." + parentColumnName + "." + makeFirstCapital(value[i].text,False)
                    column["SvcRespAttr_ItemResult"] = "data." + parentColumnName + "." + makeFirstCapital(value[i].text,False)
                    column["SvcReqParam_QueryMapping"] = makeFirstCapital(value[i].text,False)
                    columnArray.append(column)
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
                column["SvcRespAttr_ListResult"] = "data." + makeFirstCapital(value[i].text,False)
                column["SvcRespAttr_ItemResult"] = "data." + makeFirstCapital(value[i].text,False)
                column["SvcReqParam_QueryMapping"] = makeFirstCapital(value[i].text,False)
                columnArray.append(column)
                i+=3

        table = {}
        table['TableName'] = makeName(tableName)
        table['Sortable'] = True
        table['Pagable'] = True
        table['PKeyColumn'] = {}
        table['FKeyColumn'] = {}
        table['Parameters'] = {}
        table['Parameters']['AcceptedKeys'] = []
        table['ItemEndpointColumnNames'] = []
        table['ColumnPushdown'] = {}
        table['ColumnPushdown']['Support'] = False
        table['ColumnPushdown']['SvcReqParam_Key'] = []
        table['Columns'] = []
        for i in range(len(columnArray)):
            table['Columns'].append(columnArray[i])
        table['VirtualTables'] = virtualTableArray
        table['APIAccess'] = {}

        table['APIAccess']['CreateAPI'] = {}
        table['APIAccess']['CreateAPI']['Method'] = "POST"
        table['APIAccess']['CreateAPI']['ColumnRequirements'] = []
        table['APIAccess']['CreateAPI']['Accept'] = "application/json"
        table['APIAccess']['CreateAPI']['ContentType'] = "application/json"
        table['APIAccess']['CreateAPI']['ParameterFormat'] = "Query"

        table['APIAccess']['ReadAPI'] = {}
        table['APIAccess']['ReadAPI']['Method'] = "GET"
        table['APIAccess']['ReadAPI']['ColumnRequirements'] = []
        table['APIAccess']['ReadAPI']['Accept'] = "application/json"
        table['APIAccess']['ReadAPI']['ContentType'] = "application/json"
        table['APIAccess']['ReadAPI']['ParameterFormat'] = "Query"

        table['APIAccess']['UpdateAPI'] = {}
        table['APIAccess']['UpdateAPI']['Method'] = "GET"
        table['APIAccess']['UpdateAPI']['ColumnRequirements'] = []
        table['APIAccess']['UpdateAPI']['Accept'] = "application/json"
        table['APIAccess']['UpdateAPI']['ContentType'] = "application/json"
        table['APIAccess']['UpdateAPI']['ParameterFormat'] = "Query"

        table['APIAccess']['DeleteAPI'] = {}
        table['APIAccess']['DeleteAPI']['Method'] = "GET"
        table['APIAccess']['DeleteAPI']['ColumnRequirements'] = []
        table['APIAccess']['DeleteAPI']['Accept'] = "application/json"
        table['APIAccess']['DeleteAPI']['ContentType'] = "application/json"
        table['APIAccess']['DeleteAPI']['ParameterFormat'] = "Query"
        print ("done")
        tables.append(table)

    fs = open('0002.txt','w')
    tempObj = {}
    tempObj['temp'] = tables
    fs.write(json.dumps(tempObj))
