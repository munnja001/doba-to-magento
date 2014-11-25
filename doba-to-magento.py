#!/usr/bin/env python
import urllib2, csv, argparse, os, json, re, fnmatch, config

parser = argparse.ArgumentParser(description='Process a Doba Product Export.')
parser.add_argument('-f', '--filename', type=str, help='the name of the file to parse', default=[''])
parser.add_argument('-c', '--category', nargs=1, default=[''])
parser.add_argument('-j', '--json', nargs=1, default=[''])
parser.add_argument('-q', '--qty-only', dest='quantityonly', action='store_true')

args = parser.parse_args()

if args.json:
    files_config = json.load(open(args.json[0]))
else:
    files_config[args.category[0]] = args.filename[0]

quantity_lower_bound = 0


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
        

    
def create_magento_dict(row, category):
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
        "_category": category ,
        "_product_websites": 'base',
        "url_key": config.slugify(row.get('item_name')), 
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
                      "_product_websites", "url_key", "cost", "price", 
                      "image", "name", "description", "_media_image",
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

for file in fnmatch.filter(os.listdir(config.export_dir), config.magento_filename_prefix + '*'):
    os.remove(config.export_dir + '/' + file)

image_urls = set()
# Create Magento CSV from Doba CSV
batch_number = 0
batch_count = 0
for category, filename in files_config.iteritems():
    with open(filename, 'rbU') as inputfile:
        product_reader = csv.DictReader(inputfile, delimiter=',', quotechar='"')
        for row in product_reader:
            image_urls.add(row.get('image_file'))
            with open(config.export_dir + '/' + config.magento_filename_prefix + str(batch_number).zfill(3) + '.csv', 'a') as magento_file:
                if args.quantityonly:
                    magento_writer = create_qty_magento_writer()
                else:
                    magento_writer = create_full_magento_writer()
                if batch_count == 0:
                    magento_writer.writeheader()
                magento_writer.writerow(create_magento_dict(row, category))
                batch_count += 1
                if batch_count == config.batch_size:
                    batch_number += 1
                    batch_count = 0
    
# Upload images via FTP  
from ftplib import FTP
if image_urls:
    ftp = FTP(config.ftp_host, config.ftp_username, config.ftp_password)
    ftp.cwd('/media/import')
    ftp_files = ftp.nlst()
    images_to_download = [x for x in image_urls if get_filename_from_url(x) not in ftp_files]
    if image_urls: 
        image_count = len(images_to_download)
        print "There are %s images to upload" % image_count
        for idx, image_url in enumerate(images_to_download):
            try:
                print "Uploading: (" + str(idx + 1) + " of " + str(image_count) + ") - " + str(image_url)
                ftp.storbinary('STOR ' + get_filename_from_url(image_url),
                               urllib2.urlopen(image_url))
            except urllib2.HTTPError:
                print "Image [%s] not found!" % image_url
        print "Finished!"
    else: print "No Images to Upload"
else: print "No Images to Upload"
