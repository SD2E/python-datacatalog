# TODO: Protein Mass Spec bestiary https://www.ncbi.nlm.nih.gov/pmc/articles/PMC3518119/

__version__ = '1.0.0'

FILETYPES = [
    ('LOG', 'Log file', ['.err$', '.out$', '.log$']),
    ('ENV', 'Environment file', ['.env$', '.rc$']),
    ('FASTQC', 'FASTQC outputs', ['fastqc.html$', 'fastqc.zip$']),
    ('MULITIQC', 'FASTQC outputs', ['multiqc_report.html$']),
    ('FASTA', 'FASTA sequence file', ['.fa$', '.fasta$', '.fa.gz$', '.fasta.gz$', '.fas$']),
    ('TSV', 'Tab-separated values (override TAB-SEPARATED-VALUES)', ['.tab$', '.tsv$']),
    ('BAM', 'Binary SAM', ['.bam$']),
    ('BAM', 'Binary SAM Index', ['.bai$']),
    ('VCF', 'Variant Call Format', ['.vcf$']),
    ('BCF', 'Binary Variant Call Format', ['.bcf$']),
    ('MD5', 'MD5 checksum file', ['.md5$']),
    ('SAM', 'Sequence Alignment/MAP', ['.sam$']),
    ('FASTQ', 'FASTQ sequence file', [
        '.fastq$', '.fastq.gz$', '.fq$', '.fq.gz$']),
    ('FCS', 'Flow Cytometry Standard', ['.fcs$']),
    ('SRAW', 'Raw proteomics file', ['.sraw$']),
    ('MZML', 'Proteomics mzML file', ['.mzML$']),
    ('MSF', 'Magellan storage file', ['.msf$']),
    ('SAMPLES', 'Sample Set Metadata (JSON)', ['^metadata-[a-z0-9-]+.json$']),
    ('BPROV', 'Biofab Provenance (JSON)', ['^provenance_dump.json$']),
    ('INI', 'INI config file', ['.ini$']),
    ('SECRETS', 'Abaco secrets file', ['^secrets.json$']),
    ('CONFIG', 'Config file', ['config.rc$', 'reactor.rc$', 'config.yml$']),
    ('GIT', 'Git file', ['.git']),
    ('JENKINS', 'Jenkins Pipeline file', ['^Jenkinsfile$']),
    ('DOCKERFILE', 'Docker build file', ['^Dockerfile$']),
    ('REQUIREMENTS', 'Python requirements file', ['^requirements.txt$']),
    ('COMPOSEFILE', 'Docker compose file', ['^docker-compose.yml$'])]
"""A list of tuples defining classifcation rules for filenames"""