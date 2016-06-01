#!/usr/bin/env python
import urllib2
import json

# url opener
cookies = ('Cookie', '_ga=GA1.2.1862213469.1457357349')
artelia = urllib2.build_opener()
artelia.addheaders.append(cookies)

# api call parameters
address = "https://payg.angazadesign.com/api/"
org = '29'
num = '10'
#org = str(input('Organization number: '))
#num = str(input('Number of lines: '))

# Fetches the Json file at a given url and converts it to a dictionary
def to_dict(url):
    call = artelia.open(url)
    str_json = call.readline()
    return json.loads(str_json)

# Grabbing the organization link
org_dict = to_dict(address + "organizations/OR" + org)
org_name = org_dict['name']
org_products = org_dict['available_product_types']
org_smsPrice = org_dict['sms_price']['value']

dump={}
invalid_keys=['za:intake_report','za:replacements_report','za:units','za:sms_messages_report','za:refunds', 'za:users','za:units_sold_by_type_data','za:revenue_data','type','za:call_sequences','za:credit_adjustments_received','za:logo','za:accounts_data','za:agents_by_units_sold_data','za:accounts_by_state_data']
ok_keys = [u'za:activations', u'za:portals', u'za:sms_messages', u'za:ledger_register', u'za:summary_data', u'za:accounts', u'self', u'za:receipts', u'za:groups', u'za:registration_config', u'za:remittances', u'za:post_user', u'za:ledger_balance', u'za:metrics_data', u'za:post_accounts', u'za:payments', u'za:replacements', u'za:exchange_data']

for key in ok_keys:
    if ((key in invalid_keys) or ('report' in key)):
        print 'invalid ' + key
        print org_dict['_links'][key]['href']
        print org_dict['_links'][key]['href'].split('{')[0]
    else:
        print 'fetching ' + key
        print org_dict['_links'][key]['href']
        print org_dict['_links'][key]['href'].split('{')[0]
        dump['key']=to_dict(org_dict['_links'][key]['href'].split('{')[0])

for key in dump:
    print 'high level key ' + key
    for key2 in dump['key']:
        print key2

# 2.Payments

# 3.Accounts

# 4.Agents

# Outputs
print org_name
print 'available products: ' + str(org_products)
print 'sms price: ' + str(org_smsPrice)

#for i in range(0,len(payments)-1):
#    data = payments[i]
#    print data['recorded']['value'] + " " + data['amount']['value'] + " " + data['currency']
