from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
import hashlib
import tarfile
import os
import yaml

print('Authenticating...')
gauth = GoogleAuth()
gauth.LoadCredentialsFile('creds.txt')
drive = GoogleDrive(gauth)
ms_id = "1gc9F3RhT3RVF9rOK--sDRSJreAAVnSl7"
gains_id = "1pJz9Y0T-BxKiSug1E-MBz6oMdwB2Uuye"

print('Retrieving MS...')
x = [xi for xi in os.listdir() if xi[0:4] == 'KAT7' and xi[-2:] == 'MS']
names = []

if len(x) == 0:
    print('No KAT7 MS found...')
    exit()

print('MS found:')
[print(f"{i + 1}.\t{xi}") for i, xi in enumerate(x)]

print('Zipping MS...')
for xi in x:
    name = xi[:-2] + 'tar.gz'
    names.append(name)
    with tarfile.open(name, 'w:gz') as tar:
        tar.add(xi)

print('Uploading zipped MS...')
for name in names:
    file = drive.CreateFile({'title': name, 'parents': [{'id': ms_id}]})
    file.SetContentFile(name)
    file.Upload()

print('Getting MS File IDs...')
file_ids = dict()
file_list = drive.ListFile({'q': f"'{ms_id}' in parents and trashed=false"}).GetList()
for file in file_list:
    file_ids[file['title']] = file['id']



print('Calculating zipped MS hashes...')
hashes = dict()
BUFFER = 65536

for name, file_id in file_ids.items():
    sha256 = hashlib.sha256()
    with open(name, 'rb') as file:
        while True:
            data = file.read(BUFFER)
            if not data:
                break
            sha256.update(data)
    
    hashes[name] = sha256.hexdigest()

print('Writing info to registry style format...')
data = []
for name in names:
    fname = '/MSC_DATA/MS/' + name

    params = name.split('_')[1:4]
    n_time = params[0]
    n_ant = params[1]
    n_chan = params[2].split('.')[0]
    desc = f'KAT7 measurement set with n_time={n_time}, n_ant={n_ant} and n_chan={n_chan}.'

    data.append({
        fname : {
               'type' : 'google',
            'file_id' : file_ids[name],
               'hash' : hashes[name],
        'description' : desc
        }})

with open('ms.yaml', 'w') as file:
    yaml.dump(data, file, sort_keys=False, default_flow_style=False, default_style="'")