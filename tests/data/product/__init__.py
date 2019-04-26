CREATES = [('file1', {'id': '.100', 'name': '0x8BADF00D.fcs'}, '105723d4-b27e-55af-b053-63f702c4ad32'), ('file2', {'name': '0xCEFAEDFE.fastq', 'child_of': ['1040f664-0b71-54a6-8941-05ac277a6fa7']}, '10546119-4ed9-5cda-ab18-2c829c9d3ed4')
           ]

DELETES = CREATES

UPDATES = [('file1', {'id': '.100', 'name': '0x8BADF00D.fcs', 'type': 'FLOW'}, '105723d4-b27e-55af-b053-63f702c4ad32'), ('file2', {'name': '0xCEFAEDFE.fastq', 'level': '2', 'child_of': ['1040f664-54a6-0b71-8941-277a05ac6fa7']}, '10546119-4ed9-5cda-ab18-2c829c9d3ed4'), ('file2', {'name': '0xCEFAEDFE.fastq', 'level': '2', 'child_of': ['1040f664-54a6-0b71-8941-277a05ac6fa7', '1040f664-44a6-1b71-9941-377a05ac6fa7']}, '10546119-4ed9-5cda-ab18-2c829c9d3ed4')]

REPLACES = [('file1', {'id': '.100', 'name': '0x8BADF00D.fcs', 'child_of': []}, '105723d4-b27e-55af-b053-63f702c4ad32'), ('file2', {'name': '0xCEFAEDFE.fastq', 'child_of': ['10546119-4ed9-5cda-ab18-2c829c9d3ed4']}, '10546119-4ed9-5cda-ab18-2c829c9d3ed4')]
