import os
HERE = os.path.dirname(os.path.abspath(__file__))
PARENT = os.path.dirname(HERE)
DATADIR = os.path.join(PARENT, 'file', 'files')

CREATES = [
    ('file1',
        {'file_id': 'file.uw_biofab.100',
         'name': '0x8BADF00D.fcs',
         'child_of': ['104c3414-73a5-553d-8e25-86cf8a92f881']}, '105723d4-b27e-55af-b053-63f702c4ad32'),
    ('file2',
     {'name': '0xCEFAEDFE.fastq',
      'child_of': ['104c3414-73a5-553d-8e25-86cf8a92f881']}, '10546119-4ed9-5cda-ab18-2c829c9d3ed4')
]

DELETES = CREATES

UPDATES = [('file1', {'file_id': 'file.uw_biofab.100', 'name': '0x8BADF00D.fcs', 'type': 'FCS'}, '105723d4-b27e-55af-b053-63f702c4ad32'), ('file2', {'name': '0xCEFAEDFE.fastq', 'level': '2', 'child_of': ['1040f664-54a6-0b71-8941-277a05ac6fa7']}, '10546119-4ed9-5cda-ab18-2c829c9d3ed4'), ('file2', {'name': '0xCEFAEDFE.fastq', 'level': '2', 'child_of': ['1040f664-54a6-0b71-8941-277a05ac6fa7', '1040f664-44a6-1b71-9941-377a05ac6fa7']}, '10546119-4ed9-5cda-ab18-2c829c9d3ed4')]

REPLACES = [('file1', {'file_id': 'file.uw_biofab.100', 'name': '0x8BADF00D.fcs', 'child_of': []}, '105723d4-b27e-55af-b053-63f702c4ad32'), ('file2', {'name': '0xCEFAEDFE.fastq', 'child_of': ['10546119-4ed9-5cda-ab18-2c829c9d3ed4']}, '10546119-4ed9-5cda-ab18-2c829c9d3ed4')]

LOADS = [
    ('file1a.json', '105c0c55-62d0-50ed-a6eb-aa9cd8038d72'),
    ('file1b.json', '1052ac87-7d61-50d1-8a04-2412b2695beb'),
    ('file2a.json', '1050e16b-d81c-54f7-ad82-36ed4de27c11'),
    ('file3a.json', '1050fc59-1363-51eb-8686-f24e0b3d0d86'),
    ('file4a.json', '10564142-a403-58ba-af9e-5b80e8f17d57'),
]
