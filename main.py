import requests
import urllib.parse
import json
from zipfile import ZipFile
from io import BytesIO
import os

with open('vt_packs.json') as packslist:
    packs_json = json.load(packslist)
    datapacks = packs_json['packs']
    mcversion = packs_json['version']

    baseurl = "https://vanillatweaks.net/"

    genurl = "assets/server/zipdatapacks.php"
    payload = {'packs':json.dumps(datapacks, separators=(',', ':')), 'version':mcversion}


    print(urllib.parse.urlencode(payload,quote_via=urllib.parse.quote_plus, encoding='UTF-8',))

    headers = {
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
    }

    r = requests.request("POST", urllib.parse.urljoin(baseurl, genurl), headers=headers, data=payload)

    resp = r.json()
    if resp['status'] == 'success':
        r = requests.get(urllib.parse.urljoin(baseurl, resp['link']))
        bio = BytesIO(r.content)
        zipfile_obj = ZipFile(bio)
        os.mkdir('./data')
        zipfile_obj.extractall('./data/')





        # with open('test.zip', 'wb') as testzip:
        #     testzip.write(r.content)
