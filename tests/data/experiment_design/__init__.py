CREATES = [
    ('NovelChassis-NAND-Gate', {'experiment_design_id': 'NovelChassis-NAND-Gate', 'child_of': ['101ba626-e1c4-5beb-bf39-2ed91338379a']},
        '114e742e-e67a-5e99-bc04-c60d1eec9a41'),
    ('Riboswitches', {'experiment_design_id': 'Riboswitches', 'child_of': ['101ba626-e1c4-5beb-bf39-2ed91338379a']},
        '11417253-69fe-5902-bcb4-033a2f1ba784'),
    ('FlamingUniJuggler', {'experiment_design_id': 'FlamingUniJuggler'},
     '114bb9f2-1483-5195-9dd6-78ea91b70291')
]

DELETES = CREATES

UPDATES = [
    ('NovelChassis-NAND-Gate',
        {'experiment_design_id': 'NovelChassis-NAND-Gate', 'title': 'NAND Gate'},
     '114e742e-e67a-5e99-bc04-c60d1eec9a41'),
    ('Riboswitches',
        {'experiment_design_id': 'Riboswitches', 'title': 'Switch it good',
            'uri': 'https://docs.google.com/document/fizzbuzz'},
     '11417253-69fe-5902-bcb4-033a2f1ba784'),
    ('FlamingUniJuggler',
     {'experiment_design_id': 'FlamingUniJuggler', 'title': 'Flaming Cone Juggler on Unicycle',
      'uri': 'https://www.facebook.com/events/156118045244222/'},
        '114bb9f2-1483-5195-9dd6-78ea91b70291')
]
