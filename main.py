import requests
import urllib.parse
import json
import zipfile
from io import BytesIO
import os
import fnmatch
import ruamel.yaml
import nbtlib
import glob

java_constant_format = "NAME: \"VALUE\"\n"
yaml = ruamel.yaml.YAML()


def gems(gemsfolder):
    gemsfile = 'gemsfile.yml'
    java_gems_file = open(gemsfile, 'w')

    for filename in glob.glob(os.path.join(gemsfolder, 'data', 'minecraft', 'loot_tables', 'chests', '**', '*.json'),
                              recursive=True):
        data = json.load(open(filename))
        # print(data)
        # print('\n')
        if 'ender_dragon' in filename or 'shulker' in filename:
            continue
        textures = list()
        loot_tables = data['pools']
        for table in loot_tables:
            for loot_table in table['entries']:
                if not ((loot_table['type'] == 'item' and loot_table['name'] == 'minecraft:player_head') or loot_table[
                    'type'] == 'minecraft:alternatives'):
                    # print(filename)
                    continue
                # print(loot_table)
                if loot_table['type'] == 'item':
                    textures.append(process_block(loot_table['functions'][0]['tag']))
                else:
                    print()
                    print("wtf")
                # print()
    textures = dict((name, texture) for (name, texture) in textures)
    print(textures)
    ruamel.yaml.dump(textures, java_gems_file, default_flow_style=False)

def process_block(nbttag):
    tag = nbtlib.parse_nbt(nbttag)
    # print(nbttag)
    name = json.loads(tag['display']['Name'])[1]['text']
    name = name.replace('\u00c2\u00a7\u0072\u00c2\u00a7\u0065','').replace(' ', '_').upper()

    # Unfuckerate names
    #if not ('ZOMBI' in name[0]):
    #    name.insert(0, name.pop())
    #elif name[0] == 'TOAST':
    #    name.insert(0, 'RABBIT')
    #name = '_'.join(name)

    texture = tag['SkullOwner']['Properties']['textures'][0]['Value']
    return name, str(texture)

def main():
    textures_data = yaml.load(open('res/textures_BASE.yml'))
    

    print(textures_data['PLAYER']['Steve'])

    with open('vt_packs.json') as packslist:
        packs_json = json.load(packslist)
        datapacks = packs_json['packs']
        mcversion = packs_json['version']

        baseurl = "https://vanillatweaks.net/"

        genurl = "assets/server/zipdatapacks.php"
        payload = {'packs': json.dumps(datapacks, separators=(',', ':')), 'version': mcversion}

        print(urllib.parse.urlencode(payload, quote_via=urllib.parse.quote_plus, encoding='UTF-8', ))

        headers = {
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        }

        r = requests.request("POST", urllib.parse.urljoin(baseurl, genurl), headers=headers, data=payload)

        resp = r.json()
        if resp['status'] == 'success':
            r = requests.get(urllib.parse.urljoin(baseurl, resp['link']))
            bio = BytesIO(r.content)
            zipfile_obj = zipfile.ZipFile(bio)
            if (not os.path.exists('./data/')):
                os.mkdir('./data')
            zipfile_obj.extractall('./data/')
            os.chdir('data')
            print(os.listdir('.'))
            pattern = '*.zip'
            for root, dirs, files in os.walk('.'):
                for filename in fnmatch.filter(files, pattern):
                    print(os.path.join(root, filename))
                    zipfile.ZipFile(os.path.join(root, filename)).extractall(
                        os.path.join(root, os.path.splitext(filename)[0]))
            subdirs = [f.path for f in os.scandir() if f.is_dir()]
            headsfolder = [s for s in subdirs if "mob heads" in s]
            blocksfolder = [s for s in subdirs if "trades" in s]
            gemsfolder = [s for s in subdirs if "gems" in s]
            gems(gemsfolder[0])


if __name__ == '__main__':
    main()