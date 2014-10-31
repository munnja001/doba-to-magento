#!/usr/bin/env python
import urllib2, csv, argparse, os, re, config

parser = argparse.ArgumentParser(description='Process a Doba Product Export.')
parser.add_argument('filename', type=str,
                   help='the name of the file to parse')
parser.add_argument('-c', '--category', nargs=1, default=[''])
parser.add_argument('-q', '--qty-only', dest='quantityonly', action='store_true')

args = parser.parse_args()

quantity_lower_bound = 0

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

# gets the filename from a URL
def get_filename_from_url(url):
    return url.split('/')[-1]

def is_in_stock(row):
  if int(row.get('qty_avail')) > quantity_lower_bound:
    return "1"
  else:
    return "0"

def get_name(row):
    return row.get('title')

def get_short_description(row):
    short_desc = row.get('item_name')
    if short_desc:
        return short_desc
    else:
        return get_name(row)

def get_description(row):
    desc = row.get('description')
    if desc:
        return desc
    else:
        return get_short_description(row)
        

    
def create_magento_dict(row):
  image_url = '/' + get_filename_from_url(row.get('image_file'))
  weight = '0.00' if not row.get('item_weight') else row.get('item_weight')
  result = {
      "sku": row.get('item_sku'),
      "qty": row.get('qty_avail'),
      "is_in_stock": is_in_stock(row),
      "manage_stock": '1'
  }

  if not args.quantityonly:
    other_attributes = {
        "_attribute_set": 'Default',
        "_type": 'simple',
        "_category": args.category[0],
        "_product_websites": 'base',
        "url_key": slugify(row.get('item_name')), 
        "cost": row.get('price'),
        "description": get_description(row),
        "image": image_url,
        "name": get_name(row),
        "price": row.get('msrp'),
        "_media_image": image_url,
        "_media_attribute_id": '88',
        "_media_position": '1',
        "_media_is_disabled": '0',
        "short_description": get_short_description(row),
        "small_image": image_url,
        "status": '1',
        "tax_class_id": '2',
        "thumbnail": image_url,
        "visibility": '4',
        "weight": weight,
        "backorders": 'No Backorders'
    }

    result = dict(result.items() + other_attributes.items())
    
  return result

magento_qty_fieldnames = ["sku","qty", "is_in_stock", "manage_stock"]

magento_fieldnames = magento_qty_fieldnames + ["_attribute_set", "_type", "_category",
                      "_product_websites", "url_key", "cost", "description",
                      "image", "name", "price", "_media_image",
                      "_media_attribute_id", "_media_position",
                      "_media_is_disabled", "short_description", "small_image",
                      "status", "tax_class_id", "thumbnail", "visibility",
                      "weight", "backorders"]

def create_full_magento_writer():
    return create_magento_writer(magento_fieldnames)

def create_qty_magento_writer():
    return create_magento_writer(magento_qty_fieldnames)

def create_magento_writer(fields):
    return csv.DictWriter(magento_file, delimiter=',', quotechar='"', fieldnames = fields, quoting=csv.QUOTE_ALL, lineterminator = '\n')


# Ensure export dir exists
if not os.path.exists(config.export_dir):
    os.mkdir(config.export_dir)

image_urls = []
# Create Magento CSV from Doba CSV
with open(args.filename, 'rbU') as inputfile, open(config.magento_filename, 'w+') as magento_file:
    product_reader = csv.DictReader(inputfile, delimiter=',', quotechar='"')
    if args.quantityonly:
        magento_writer = create_qty_magento_writer()
    else:
        magento_writer = create_full_magento_writer()
    magento_writer.writeheader()
    for row in product_reader:
      image_urls.append(row.get('image_file'))
      magento_writer.writerow(create_magento_dict(row))
    
# Upload images via FTP  
from ftplib import FTP
if image_urls:
    ftp = FTP(config.ftp_host, config.ftp_username, config.ftp_password)
    ftp.cwd('/media/import')
    ftp_files = ftp.nlst()
    images_to_download = [x for x in image_urls if get_filename_from_url(x) not in ftp_files]
    if image_urls: 
        print "There are %s images to upload" % len(images_to_download)
        for image_url in images_to_download:
            print "Uploading: %s" % image_url
            ftp.storbinary('STOR ' + get_filename_from_url(image_url), urllib2.urlopen(image_url))
        print "Finished!"
    else: print "No Images to Upload"
else: print "No Images to Upload"
