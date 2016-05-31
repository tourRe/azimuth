#!/usr/bin/env python
import urllib2
import json

# cookies
cookies = ('Cookie', '_ga=GA1.2.1862213469.1457357349')

# url opener
artelia = urllib2.build_opener()
artelia.addheaders.append(cookies)
address = "https://payg.angazadesign.com/api/"

# interesting urls
# "https://payg.angazadesign.com/api/accounts/2646511"
# "https://payg.angazadesign.com/api/organizations/OR29"
# "https://payg.angazadesign.com/api/payments?organization_qid=OR000028&offset=0&sort_by=recorded&limit=20&descending=true"

org = str(input('Organization number: '))
num = str(input('Number of lines: '))

# opener calls
call0 = artelia.open(address + "organizations/OR" + org)
call1 = artelia.open(address + "payments?organization_qid=OR0000" + org +  "&offset=0&sort_by=recorded&limit=" + num + "&descending=true")

# converting json to dict
str0 = call0.readline()
data0 = json.loads(str0)

str1 = call1.readline()
data1 = json.loads(str1)

# printing payment data
print data0['name']
payments = data1['_embedded']['item']
for i in range(0,len(payments)-1):
    data = payments[i]
    print data['recorded']['value'] + " " + data['amount']['value'] + " " + data['currency']
