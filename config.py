import re
# FTP config
ftp_host="ftp.partyshipper.com"
ftp_username="patiotoparlor@partyshipper.com"
ftp_password="credera1!"


login_url = 'https://www.doba.com/login'
doba_email = 'omoran@credera.com'
doba_password = 'credera1!'
team_prefix = 'P2P'

# export config
export_dir = 'magento-export'
magento_filename_prefix = 'magento'
batch_size = 150


# Method to generate URL Slug (Copied from Internets)
_slugify_strip_re = re.compile(r'[^\w\s-]')
_slugify_hyphenate_re = re.compile(r'[-\s]+')
def slugify(value):
    """
    Normalizes string, converts to lowercase, removes non-alpha characters,
    and converts spaces to hyphens.

    From Django's "django/template/defaultfilters.py".
    """
    import unicodedata
    if not isinstance(value, unicode):
        value = unicode(value)
    value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore')
    value = unicode(_slugify_strip_re.sub('', value).strip().lower())
    return _slugify_hyphenate_re.sub('-', value)