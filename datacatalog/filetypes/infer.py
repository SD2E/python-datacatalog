import os
import re
from attrdict import AttrDict
from xdg import Mime

def infer_filetype(filename):
    """Determines canonical 'type' of a file based on simple rules, with
    fallback to using the freedesktop.org MIME catalog
    """
    if not os.path.exists(filename):
        raise OSError('{} does not exist or is not accessible')
    try:
        return __infer_by_rule(filename)
    except FileTypeError:
        return __infer_xdg_mime(filename)
    except Exception as exc:
        raise FileTypeError('Failed to infer file type', exc)

def __infer_xdg_mime(filename):
    mime = Mime.get_type2(filename)
    label = mime.subtype
    if label.startswith('x-'):
        label = str(label.replace('x-', ''))
    comment = str(mime.get_comment())
    return FileType(label, comment)

def __infer_by_rule(filename):
    # TODO: Protein Mass Spec bestiary https://www.ncbi.nlm.nih.gov/pmc/articles/PMC3518119/
    # TODO: Replace rules with local additions to local xdg mime catalog
    FILETYPES = [
        ('FASTQ', 'FASTQ sequence file', ['\.fastq$', '\.fastq.gz$', '\.fq$', '\.fq.gz$']),
        ('FCS', 'Flow Cytometry Standard', ['\.fcs$']),
        ('SRAW', 'Raw proteomics file', ['\.sraw$']),
        ('MZML', 'Proteomics mzML file', ['\.mzML$']),
        ('MSF', 'Magellan storage file', ['\.msf$']),
        ('BPROV', 'Biofab Provenance JSON', ['^provenance_dump.json$']),
        ('INI', 'INI config file', ['\.ini$']),
        ('SECRETS', 'Abaco secrets file', ['^secrets.json$']),
        ('CONFIG', 'Config file', ['reactor.rc', 'config.yml$']),
        ('JENKINS', 'Jenkins Pipeline file', ['^Jenkinsfile$']),
        ('DOCKERFILE', 'Docker build file', ['^Dockerfile$']),
        ('REQUIREMENTS', 'Python requirements file', ['^requirements.txt$']),
        ('COMPOSEFILE', 'Docker compose file', ['^docker-compose.yml$'])]

    for label, comment, globs in FILETYPES:
        for g in globs:
            if re.compile(g, re.IGNORECASE).search(filename):
                return FileType(label, comment)
    raise FileTypeError('File matched no rules')

class FileTypeError(ValueError):
    pass

class FileType(AttrDict):
    def __init__(self, label, comment):
        self.label = label.upper()
        self.comment = comment
