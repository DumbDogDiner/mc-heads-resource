import requests, re, urllib.parse, json, zipfile, io, os, fnmatch, yaml, nbtlib, glob

webapi = "https://api.ashcon.app/mojang/v2/user/"

def gems(gemsfolder):
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
                    textures.append(process_gem(loot_table['functions'][0]['tag']))
                else:
                    print()
                    print("wtf")
                # print()
    textures = dict((name, texture) for (name, texture) in textures)
    # print(textures)
    return textures

def process_gem(nbttag):
    tag = nbtlib.parse_nbt(nbttag)
    # print(nbttag)
    name = json.loads(tag['display']['Name'])[1]['text']
    name = name.replace('\u00c2\u00a7\u0072\u00c2\u00a7\u0065', '').upper().replace('GEM', '').strip().replace(' ', '_')

    texture = tag['SkullOwner']['Properties']['textures'][0]['Value']
    print(name)
    return name, str(texture)

def miniblocks(blocksfolder):
    textures = list()
    with open(os.path.join(blocksfolder,"data", "wandering_trades", "functions", "add_trade.mcfunction")) as mcfunc:
        for line in mcfunc.readlines():
            if 'execute' in line and not any(ex in line.upper() for ex in excluded):
                trade = nbtlib.parse_nbt(line.split('value')[1])
                pairing = process_block(nbtlib.serialize_tag(trade['sell']['tag']))
                textures.append(pairing)
        return textures

def process_block(nbttag):
    tag = nbtlib.parse_nbt(nbttag)
    # print(nbttag)
    name = json.loads(tag['display']['Name'])['text']
    name = re.sub(r'\u00A7([0-9a-ek-or])', '', name).upper().replace('GEM', '').strip().replace(' ', '_')

    texture = tag['SkullOwner']['Properties']['textures'][0]['Value']
    print(name)
    return name, str(texture)

def mobheads(headsfolder):
    textures = list()
    for filename in glob.glob(os.path.join(headsfolder, 'data','minecraft','loot_tables','entities','**','*.json') , recursive=True):
        data = json.load(open(filename))
        #print(data)
        #print('\n')
        if 'ender_dragon' in filename or 'shulker' in filename:
            continue

        loot_tables = data['pools']
        for table in loot_tables:
            loot_table = table['entries'][0]
            if not((loot_table['type'] == 'item' and loot_table['name'] == 'minecraft:player_head') or loot_table['type'] == 'minecraft:alternatives'):
                #print(filename)
                continue
            #print(loot_table)
            if loot_table['type'] == 'minecraft:alternatives':
                for child in loot_table['children']:
                    textures.append(process_head(child['functions'][0]['tag']))
                    #print(child)
                    #print('\n')
            elif loot_table['type'] == 'item':
                textures.append(process_head(loot_table['functions'][0]['tag']))
            else:
                print()
                print("wtf")
            #print()
    return textures

def process_head(nbttag):
    tag = nbtlib.parse_nbt(nbttag)
    #print(nbttag)
    name = tag['SkullOwner']['Name']
    name = name.upper().split(' ')

    # Unfuckerate names
    if not('ZOMBI' in name[0] ):
        name.insert(0, name.pop())
    elif name[0] == 'TOAST':
        name.insert(0,'RABBIT')
    name = '_'.join(name)

    texture = tag['SkullOwner']['Properties']['textures'][0]['Value']
    print(name)
    return name, texture

def mhf():
    textures = dict()
    resp = [s.replace('*','').strip() for s in requests.get("https://pastebin.com/raw/5mug6EBu").text.splitlines() if (s and not(s.startswith(';')))]
    for line in resp:
        print(line)
        resp = requests.get(webapi + line.strip()).json()
        textures[line.upper().replace('MHF_','')] = (resp['textures']['raw']['value'])

    return textures


def main():
    textures_data = yaml.load(open('res/textures_BASE.yml'), Loader=yaml.SafeLoader)
    with open('res/excluded.txt') as f:
        global excluded
        excluded = f.read().splitlines()

    with open('res/vt_packs.json') as packslist:
        packs_json = json.load(packslist)
        datapacks = packs_json['packs']
        mcversion = packs_json['version']

        baseurl = "https://vanillatweaks.net/"

        genurl = "assets/server/zipdatapacks.php"
        payload = {'packs': json.dumps(datapacks, separators=(',', ':')), 'version': mcversion}


        headers = {
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        }

        r = requests.request("POST", urllib.parse.urljoin(baseurl, genurl), headers=headers, data=payload)

        resp = r.json()
        if resp['status'] == 'success':
            r = requests.get(urllib.parse.urljoin(baseurl, resp['link']))
            bio = io.BytesIO(r.content)
            zipfile_obj = zipfile.ZipFile(bio)
            if (not os.path.exists('./data/')):
                os.mkdir('./data')
            zipfile_obj.extractall('./data/')
            origdir = os.getcwd()
            os.chdir('data')
            pattern = '*.zip'
            for root, dirs, files in os.walk('.'):
                for filename in fnmatch.filter(files, pattern):
                    zipfile.ZipFile(os.path.join(root, filename)).extractall(
                        os.path.join(root, os.path.splitext(filename)[0]))
            subdirs = [f.path for f in os.scandir() if f.is_dir()]
            headsfolder = [s for s in subdirs if "mob heads" in s]
            blocksfolder = [s for s in subdirs if "trades" in s]
            gemsfolder = [s for s in subdirs if "gems" in s]

            if (textures_data['GEM'] is None):
                textures_data['GEM'] = dict()
            textures_data['GEM'].update(gems(gemsfolder[0]))
            if(textures_data['BLOCK'] is None):
                textures_data['BLOCK'] = dict()
            textures_data['BLOCK'].update(miniblocks(blocksfolder[0]))
            if (textures_data['MOB'] is None):
                textures_data['MOB'] = dict()
            textures_data['MOB'].update(mobheads(headsfolder[0]))
            if (textures_data['MHF'] is None):
                textures_data['MHF'] = dict()
            textures_data['MHF'].update(mhf())

            os.chdir(origdir)
            if (not os.path.exists('./out/')):
                os.mkdir('./out')
            json.dump(textures_data, open('./out/textures.json', 'w'))


if __name__ == '__main__':
    main()
