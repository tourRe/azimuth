#!/usr/bin/env python
import urllib2
import json

# url opener
cookies = ('Cookie', '_ga=GA1.2.1862213469.1457357349')
artelia = urllib2.build_opener()
artelia.addheaders.append(cookies)

# api call parameters
address = "https://payg.angazadesign.com/api/"
org = str(input('Organization number: '))
num = str(input('Number of lines: '))

# Fetches the Json file at a given url and converts it to a dictionary
def to_dict(url):
    call = artelia.open(url)
    str_json = call.readline()
    return json.loads(str_json)

# 1.Organization
org_dict = to_dict(address + "organizations/OR" + org)
org_name = org_dict['name']
org_products = org_dict['available_product_types']
org_smsPrice = org_dict['sms_price']['value']

# 2.Payments
pay_dict = to_dict(address + "payments?organization_qid=OR0000" + org +  "&offset=0&sort_by=recorded&limit=" + num + "&descending=true")
payments = pay_dict['_embedded']['item']

# 3.Accounts

# 4.Agents

# Outputs
print org_name
print 'available products: ' + str(org_products)
print 'sms price: ' + str(org_smsPrice)

for i in range(0,len(payments)-1):
    data = payments[i]
    print data['recorded']['value'] + " " + data['amount']['value'] + " " + data['currency']
