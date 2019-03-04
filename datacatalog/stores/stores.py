from datacatalog import settings

__all__ = ['STORES']

STORES = [
    {'level': '0', 'prefix': '/uploads',
     'storage_system': settings.STORAGE_SYSTEM,
     'manager': settings.TACC_MANAGER_ACCOUNT,
     'database': settings.MONGODB_DATABASE},
    {'level': '1', 'prefix': '/products',
     'storage_system': settings.STORAGE_SYSTEM,
     'manager': settings.TACC_MANAGER_ACCOUNT,
     'database': settings.MONGODB_DATABASE},
    {'level': '2', 'prefix': '/products',
     'storage_system': settings.STORAGE_SYSTEM,
     'manager': settings.TACC_MANAGER_ACCOUNT,
     'database': settings.MONGODB_DATABASE},
    {'level': '3', 'prefix': '/products',
     'storage_system': settings.STORAGE_SYSTEM,
     'manager': settings.TACC_MANAGER_ACCOUNT,
     'database': settings.MONGODB_DATABASE},
    {'level': 'Reference', 'prefix': '/reference',
     'storage_system': settings.STORAGE_SYSTEM,
     'manager': settings.TACC_MANAGER_ACCOUNT,
     'database': settings.MONGODB_DATABASE}

]
