CREATES = [
    ('NovelChassis-NAND-Gate.1', {'experiment_id': 'experiment.ginkgo.10001',
                                  'child_of': ['114e742e-e67a-5e99-bc04-c60d1eec9a41']},
        '102edd93-29d6-5483-b60b-8dfd4d094b9c'),
    ('Riboswitches.1', {'experiment_id': 'experiment.ginkgo.10002',
                        'child_of': ['11417253-69fe-5902-bcb4-033a2f1ba784']},
        '102d8a08-034d-5c27-8d9c-a24bfcc94858'),
    ('FlamingUniJuggler.1', {'experiment_id': 'experiment.tacc.10003',
                             'child_of': ['114bb9f2-1483-5195-9dd6-78ea91b70291']},
        '1027aa77-d524-5359-a802-a8008adaecb5')
]

DELETES = CREATES

UPDATES = [('NovelChassis-NAND-Gate.1',
            {'experiment_id': 'experiment.ginkgo.10001',
             'title': 'NAND Gate Expt 1',
             'child_of': ['114e742e-e67a-5e99-bc04-c60d1eec9a41']},
            '102edd93-29d6-5483-b60b-8dfd4d094b9c'),
           ('Riboswitches.1',
            {'experiment_id': 'experiment.ginkgo.10002',
             'title': 'RiboSwitch it good (1)',
             'child_of': ['11417253-69fe-5902-bcb4-033a2f1ba784']},
            '102d8a08-034d-5c27-8d9c-a24bfcc94858'),
           ('Contestant.1',
            {'experiment_id': 'experiment.tacc.10003',
             'title': 'Contestant Number One',
             'child_of': ['11417253-69fe-5902-bcb4-033a2f1ba784']},
            '1027aa77-d524-5359-a802-a8008adaecb5')
           ]
