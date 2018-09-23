import re
from .filetype import FileType, FileTypeError

# TODO: Protein Mass Spec bestiary https://www.ncbi.nlm.nih.gov/pmc/articles/PMC3518119/
# TODO: Replace rules with local additions to local xdg mime catalog
FILETYPES = [
    ('BAM', 'Binary SAM', ['\.bam$']),
    ('VCF', 'Variant Call Format', ['\.vcf$']),
    ('BCF', 'Binary Variant Call Format', ['\.bcf$']),
    ('SAM', 'Sequence Alignment/MAP', ['\.sam$']),
    ('FASTQ', 'FASTQ sequence file', [
        '\.fastq$', '\.fastq.gz$', '\.fq$', '\.fq.gz$']),
    ('FCS', 'Flow Cytometry Standard', ['\.fcs$']),
    ('SRAW', 'Raw proteomics file', ['\.sraw$']),
    ('MZML', 'Proteomics mzML file', ['\.mzML$']),
    ('MSF', 'Magellan storage file', ['\.msf$']),
    ('SAMPLES', 'SD2 Samples Metadata JSON', ['^metadata-[0-9-]+.json$']),
    ('BPROV', 'Biofab Provenance JSON', ['^provenance_dump.json$']),
    ('INI', 'INI config file', ['\.ini$']),
    ('SECRETS', 'Abaco secrets file', ['^secrets.json$']),
    ('CONFIG', 'Config file', ['reactor.rc', 'config.yml$']),
    ('JENKINS', 'Jenkins Pipeline file', ['^Jenkinsfile$']),
    ('DOCKERFILE', 'Docker build file', ['^Dockerfile$']),
    ('REQUIREMENTS', 'Python requirements file', ['^requirements.txt$']),
    ('COMPOSEFILE', 'Docker compose file', ['^docker-compose.yml$'])]

def listall():
    """Return a list of FileType objects from defined rules"""
    l = []
    for rule in FILETYPES:
        l.append(FileType(label=rule[0], comment=rule[1]))
    return l

def infer(filename):
    for label, comment, globs in FILETYPES:
        for g in globs:
            if re.compile(g, re.IGNORECASE).search(filename):
                return FileType(label, comment)
    raise FileTypeError('File matched no rules')
