#!/usr/bin/env python

import urllib2;

# cookies
cookies = ('Cookie', '_ga=GA1.2.1862213469.1457357349');

# url opener
artelia = urllib2.build_opener();
artelia.addheaders.append(cookies);

# interesting urls
# "https://payg.angazadesign.com/api/accounts/2646511"
# "https://payg.angazadesign.com/api/organizations/OR29"
# "https://payg.angazadesign.com/api/payments?organization_qid=OR000028&offset=0&sort_by=recorded&limit=20&descending=true"

# opener calls
print artelia("https://payg.angazadesign.com/api/payments?organization_qid=OR000028&offset=0&sort_by=recorded&limit=20&descending=true").read();

