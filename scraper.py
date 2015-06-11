# This is a template for a Python scraper on morph.io (https://morph.io)
# including some code snippets below that you should find helpful

import requests
import json
import scraperwiki
from datetime import date, timedelta

limit = 0
api_url = 'https://beta-api.contractfinder2.com'

def search_notices(s_type ='Contract',s_status=['Open'],s_publishedFrom=None,s_publishedTo=None):
    """Query the search endpoint and return a list of notices. Documentation of options available from API URL at /api/Help/Api/POST-Searches-Search"""
    search_object = {'searchCriteria':{}}
    if s_type:
        search_object['searchCriteria']['type'] = s_type
    if s_status:
        search_object['searchCriteria']['statuses'] = s_status
    if s_publishedFrom:
        search_object['searchCriteria']['publishedFrom'] = s_publishedFrom
    if s_publishedTo:
        search_object['searchCriteria']['publishedFrom'] = s_publishedTo
    print(search_object)
    
    r = requests.post(api_url+'/Searches/Search',data=json.dumps(search_object),headers={'content-type': 'application/json'},verify=False)
    return r.json()

from_date = str(date.today() - timedelta(days=3))
contract_list = search_notices(s_type ='Contract',s_status=['Open','Closed','Withdrawn','Awarded'],s_publishedFrom=from_date)
print "Total results found: " + str(contract_list['hitsCount'])

for notice in contract_list['noticeList']:
    limit += 1
    if limit > 9999:
        break
        
    notice_id = notice['item']['id']
    
    print api_url+'/Published/Notice/OCDS/'+str(notice_id)
    r = requests.get(api_url+'/Published/Notice/OCDS/'+notice_id,headers={'content-type': 'application/json'},verify=False)
    if r.status_code == 200:
        release = r.json()
        release_id = str(release['releases'][0]['id'])
        ocid = str(release['releases'][0]['ocid'])
        scraperwiki.sqlite.save(unique_keys=['id'], data={"id": release_id, "ocid": ocid,"release": json.dumps(release)})
    else:
        # We should extend the scraper to log failed notices somewhere
        scraperwiki.sqlite.save(unique_keys=['id'], table_name="errors", data={"id": notice_id, "date": str(date.today())})
        print "Error fetching " + notice_id

