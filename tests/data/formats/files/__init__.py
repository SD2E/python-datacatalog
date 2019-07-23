from datacatalog.tenancy import Projects
projects = Projects.sync()

CLASSIFY = [('bio-15901_op82951.json', 'Biofab', projects.SD2.tenant, projects.SD2.tacc_name),
            ('bio-20249.json', 'Biofab', projects.SD2.tenant, projects.SD2.tacc_name),
            ('gk-YeastSTATES-DNAseq-of-Yeastgates1-Strains_samples.json', 'Ginkgo', projects.SD2.tenant, projects.SD2.tacc_name),
            ('gk-controls.json', 'Ginkgo', projects.SD2.tenant, projects.SD2.tacc_name),
            ('tx-samples.json', 'Transcriptic', projects.SD2.tenant, projects.SD2.tacc_name),
            ('tx-r1c9pjzjs2c9k_r1c9wva2tpwj7.json', 'Transcriptic', projects.SD2.tenant, projects.SD2.tacc_name),
            ('sa-r1bbktv6x4xke.json', 'SampleAttributes', projects.SD2.tenant, projects.SD2.tacc_name),
            ('sa-r1bgtnn6nxy85.json', 'SampleAttributes', projects.SD2.tenant, projects.SD2.tacc_name),
            ('20181009-top-4-A-B-cell-variants-A-B-sampling-exp-1.xlsx', 'Caltech', projects.SD2.tenant, projects.BIOCON.tacc_name),
            ('20190214-A-B-mar-1.xlsx', 'Caltech', projects.SD2.tenant, projects.BIOCON.tacc_name),
            ('TACC_genomics_metadata.xlsx', 'Marshall', projects.SAFEGENES.tenant, projects.SAFEGENES.tacc_name),
            ('34206.json', 'Biofab', projects.SD2.tenant, projects.SD2.tacc_name)
            ]
