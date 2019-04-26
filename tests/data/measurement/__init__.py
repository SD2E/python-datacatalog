CREATES = [
    ('meas1a', {'measurement_id': 'biofab.measurement.90000', 'child_of': ['103dfcc6-7dd8-54a1-b5d7-c36129511173']},
        '1049d8dd-e879-53e8-a916-f975f1785c29'),
    ('meas1b', {'measurement_id': 'biofab.measurement.90001', 'child_of': ['103dfcc6-7dd8-54a1-b5d7-c36129511173']},
        '104af61c-3367-58b4-a19c-d3faf67aaeea'),
    ('meas2', {'measurement_id': 'ginkgo.measurement.ABCDEFG', 'child_of': ['103b4050-f7dc-5680-8445-cd14e092445a']},
        '10476c48-7753-55a4-8529-d56f0b502896'),
    ('meas3a', {'measurement_id': 'measurement.ginkgo.sample.ginkgo.5511784.1', 'child_of': ['1031e39a-ac24-57b6-8fb3-b8fb65708654']},
        '104e6c18-e464-501c-882c-7c571ebe50d6'),
    ('meas3b', {'measurement_id': 'measurement.ginkgo.sample.ginkgo.5511781.1', 'child_of': ['1031e39a-ac24-57b6-8fb3-b8fb65708654']},
        '10464ba4-6760-5ea9-ba3c-2d7d2742533d'),
    ('meas4', {'measurement_id': 'measurement.tacc.chocolate-rum-raisin-splat', 'child_of': ['103b4050-f7dc-5680-8445-cd14e092445a']},
     '104c3414-73a5-553d-8e25-86cf8a92f881')
]

DELETES = CREATES

UPDATES = [
    ('meas1a', {'measurement_id': 'biofab.measurement.90000',
                'child_of': ['103dfcc6-7dd8-54a1-b5d7-c36129511173'], 'measurement_type': 'RNA_SEQ'}, '1049d8dd-e879-53e8-a916-f975f1785c29'),
    ('meas1b', {'measurement_id': 'biofab.measurement.90001',
                'child_of': ['103dfcc6-7dd8-54a1-b5d7-c36129511173'], 'measurement_type': 'RNA_SEQ'}, '104af61c-3367-58b4-a19c-d3faf67aaeea'),
    ('meas2', {'measurement_id': 'ginkgo.measurement.ABCDEFG',
               'child_of': ['103b4050-f7dc-5680-8445-cd14e092445a'], 'measurement_type': 'EXPERIMENT_DESIGN'}, '10476c48-7753-55a4-8529-d56f0b502896'),
    ('meas3a', {'measurement_id': 'measurement.ginkgo.sample.ginkgo.5511784.1',
                'child_of': ['1031e39a-ac24-57b6-8fb3-b8fb65708654'], 'measurement_type': 'SEQUENCING_CHROMATOGRAM'}, '104e6c18-e464-501c-882c-7c571ebe50d6'),
    ('meas3b', {'measurement_id': 'measurement.ginkgo.sample.ginkgo.5511781.1',
                'child_of': ['1031e39a-ac24-57b6-8fb3-b8fb65708654'], 'measurement_type': 'SEQUENCING_CHROMATOGRAM'}, '10464ba4-6760-5ea9-ba3c-2d7d2742533d'),
    ('meas4', {'measurement_id': 'measurement.tacc.chocolate-rum-raisin-splat',
               'child_of': ['103b4050-f7dc-5680-8445-cd14e092445a'], 'measurement_type': 'FLOW',
               'measurement_name': 'Free text field'}, '104c3414-73a5-553d-8e25-86cf8a92f881')
]
