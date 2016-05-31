#!/usr/bin/env python

import urllib2;

# cookies
cookies = ('Cookie', '_ga=GA1.2.1862213469.1457357349');

# url opener
artelia = urllib2.build_opener();
artelia.addheaders.append(cookies);
address = "https://payg.angazadesign.com/api/";

# interesting urls
# "https://payg.angazadesign.com/api/accounts/2646511"
# "https://payg.angazadesign.com/api/organizations/OR29"
# "https://payg.angazadesign.com/api/payments?organization_qid=OR000028&offset=0&sort_by=recorded&limit=20&descending=true"

org = str(input('Organization number: '));

# opener calls
call_0 = artelia.open(address + "organizations/OR" + org);
print call_0.read();

call_1 = artelia.open(address + "payments?organization_qid=OR0000" + org +  "&offset=0&sort_by=recorded&limit=10&descending=true");
print call_1.read();
