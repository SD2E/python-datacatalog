CREATES = [
    ('expt1', {'sample_id': 'biofab.sample.900000', 'child_of': ['102edd93-29d6-5483-b60b-8dfd4d094b9c']}, '103dfcc6-7dd8-54a1-b5d7-c36129511173'),
    ('expt2', {'sample_id': 'ginkgo.sample.ABCDEFG', 'child_of': ['102d8a08-034d-5c27-8d9c-a24bfcc94858']}, '1031e39a-ac24-57b6-8fb3-b8fb65708654'),
    ('expt3', {'sample_id': 'tacc.sample.8675309', 'child_of': ['1027aa77-d524-5359-a802-a8008adaecb5']}, '103b4050-f7dc-5680-8445-cd14e092445a')
]

CLEAN = [
    ('expt41', {'sample_id': 'sample1.lab.experiment.lab.4', 'control_type': 'HIGH_FITC', 'standard_type':'BEAD_FLUORESCENCE', 'child_of': ['102edd93-29d6-5483-b60b-8dfd4d094b9c']}, '1dcbf4fc-63f0-403d-9a3b-a4d9838b00b0'),
    ('expt42', {'sample_id': 'sample2.lab.experiment.lab.4', 'child_of': ['102edd93-29d6-5483-b60b-8dfd4d094b9c']}, '596521f3-a72c-4b05-a315-34b51cde25de'),
    ('expt51', {'sample_id': 'sample1.lab.experiment.lab.5', 'child_of': ['102d8a08-034d-5c27-8d9c-a24bfcc94858']}, '22d9781d-3a53-4258-8d0b-948c28fc02f6'),
    ('expt52', {'sample_id': 'sample2.lab.experiment.lab.5', 'child_of': ['102d8a08-034d-5c27-8d9c-a24bfcc94858']}, '84ce0cfb-5240-4e4a-9642-0d37df354337')
]

DELETES = CREATES

UPDATES = [
    ('expt1', {'sample_id': 'biofab.sample.900000', 'replicate': 0, 'child_of': ['102edd93-29d6-5483-b60b-8dfd4d094b9c']}, '103dfcc6-7dd8-54a1-b5d7-c36129511173'),
    ('expt2', {'sample_id': 'ginkgo.sample.ABCDEFG', 'control_type': 'BASELINE', 'child_of': ['102d8a08-034d-5c27-8d9c-a24bfcc94858']},
        '1031e39a-ac24-57b6-8fb3-b8fb65708654'),
    ('expt3', {'sample_id': 'tacc.sample.8675309', 'replicate': 3, 'child_of': ['1027aa77-d524-5359-a802-a8008adaecb5']}, '103b4050-f7dc-5680-8445-cd14e092445a')
]
