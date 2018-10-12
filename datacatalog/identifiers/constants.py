from uuid import uuid3, NAMESPACE_DNS

class Constants(object):
    DNS_FOR_NAMESPACE = 'sd2e.org'
    MOCK_DNS_FOR_NAMESPACE = 'sd2e.club'
    UUID_NAMESPACE = uuid3(NAMESPACE_DNS, DNS_FOR_NAMESPACE)
    UUID_MOCK_NAMESPACE = uuid3(NAMESPACE_DNS, MOCK_DNS_FOR_NAMESPACE)
