# -*- coding: utf-8 -*-

#    OpenDKIM genkeys tool, freedns.afraid.org API
#    Copyright (C) 2016 Todd Knarr <tknarr@silverglass.org>

#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.

#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.

#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.

# Uses the 'requests' package.

# Requires:
# dnsapi_data][0]       : Cookie value for dns_cookie for freedns.afraid.org from browser
# dnsapi_domain_data[0] : domain_id value for domain
# key_data['chunked']   : TXT record value in chunked (BIND) format

# FreeDNS.afraid.org doesn't have a format API for updating records other than
# A/AAAA records (for dynamic DNS for hosts), but we can use the form submission
# URL to add arbitrary records. To change an existing record we'd need to include
# a data_id parameter with the ID of the specific record being changed, and for
# DKIM we need to be adding a new record for the new selector rather than changing
# an existing record.

# POST URL: https://freedns.afraid.org/subdomain/save.php?step=2

# Sample POST data:
# type=TXT&subdomain=test&domain_id=939393&address=Some+data&ttl=&ref=xxxxxxxxxxxxxxxx&send=Save%21
#
# Parameters (will be URL-encoded):
#   type = "TXT"
#   subdomain = selector + "._domainkey"
#   domain_id = dnsapi_domain_data[0]
#   address = key_data['chunked']
#   ttl = empty
#   ref = unknown, apparently not used
#   send = "Save!"

import logging
import requests

def update( dnsapi_data, dnsapi_domain_data, key_data, debugging = False ):
    if len(dnsapi_data) < 1:
        logging.error( "DNS API freedns: authentication cookie not configured" )
        return False;
    cookie_value = dnsapi_data[0]
    if len(dnsapi_domain_data) < 1:
        logging.error( "DNS API freedns: domain data does not contain domain ID" )
        return False
    domain_id = dnsapi_domain_data[0]
    try:
        selector = key_data['selector']
        data = key_data['chunked']
    except KeyError as e:
        logging.error( "DNS API freedns: required information not present: %s", str(e) )
        return False
    if debugging:
        return True

    result = False
    resp = requests.post( "https://freedns.afraid.org/subdomain/save.php?step=2",
                          data = { 'type': 'TXT',
                                   'subdomain': selector + "._domainkey",
                                   'domain_id': domain_id,
                                   'address': data,
                                   'ttl': '',
                                   'send': "Save!"
                                   },
                          cookies = { 'dns_cookie': cookie_value } )
    logging.info( "HTTP status: %d", resp.status_code )

    if resp.status_code == requests.codes.ok:
        result = True
    else:
        result = False
        logging.error( "DNS API freedns: HTTP error %d", resp.status_code )
        logging.error( "DNS API freedns: error response body:\n%s", resp.text )

    return result
