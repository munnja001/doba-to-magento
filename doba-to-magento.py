#!/usr/bin/python
import csv
import argparse
import os
import re


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


magento_fieldnames = ["sku","_store","_attribute_set","_type","_category","_product_websites","color","cost","country_of_manufacture","created_at","custom_design","custom_design_from","custom_design_to","custom_layout_update","description","enable_googlecheckout","gallery","gift_message_available","has_options","image","image_label","is_imported","manufacturer","meta_description","meta_keyword","meta_title","minimal_price","msrp","msrp_display_actual_price_type","msrp_enabled","name","news_from_date","news_to_date","options_container","page_layout","price","required_options","short_description","small_image","small_image_label","special_from_date","special_price","special_to_date","status","tax_class_id","thumbnail","thumbnail_label","updated_at","url_key","visibility","weight","qty","min_qty","use_config_min_qty","is_qty_decimal","backorders","use_config_backorders","min_sale_qty","use_config_min_sale_qty","max_sale_qty","use_config_max_sale_qty","is_in_stock","notify_stock_qty","use_config_notify_stock_qty","manage_stock","use_config_manage_stock","stock_status_changed_auto","use_config_qty_increments","qty_increments","use_config_enable_qty_inc","enable_qty_increments","_links_related_sku","_links_related_position","_links_crosssell_sku","_links_crosssell_position","_links_upsell_sku","_links_upsell_position","_associated_sku","_associated_default_qty","_associated_position","_tier_price_website","_tier_price_customer_group","_tier_price_qty","_tier_price_price","_media_attribute_id","_media_image","_media_lable","_media_position","_media_is_disabled"]

def create_magento_dict(row):
  image_url = '/' + row.get('image_file').split('/')[-1]
  weight = '0.00' if not row.get('item_weight') else row.get('item_weight')
  return {
    "sku": row.get('product_sku'),
    "_attribute_set": 'Default',
    "_type": 'simple',
    "_category": 'Patio',
    "url_key": slugify(row.get('item_name')), 
    "cost": row.get('price'),
    "description": row.get('description'),
    "image": image_url,
    "name": row.get('item_name'),
    "price": row.get('msrp'),
    "_media_image": image_url,
    "_media_attribute_id": '88',
    "_media_position": '1',
    "_media_is_disabled": '0',
    "short_description": row.get('title'),
    "small_image": image_url,
    "status": '1',
    "tax_class_id": '2',
    "thumbnail": image_url,
    "visibility": '4',
    "weight": weight,
    "qty": row.get('qty_avail'),
    "backorders": 'No Backorders',
    "is_in_stock": '1',
    "manage_stock": '1'
  }

def create_inventory_dict(row):
  return {
    'sku': row.get('product_sku'),
    'image_file': row.get('image_file'),
    'small_image': row.get('image_file')
  }

parser = argparse.ArgumentParser(description='Process a Doba Product Export.')
parser.add_argument('filename', type=str,
                   help='the name of the file to parse')

args = parser.parse_args()
export_dir = 'magento-export'
if not os.path.exists(export_dir):
    os.mkdir(export_dir)

with open(args.filename, 'rbU') as inputfile, open(export_dir + '/magento.csv', 'w+') as magento_file, open(export_dir + '/urls.txt', 'w+') as urls_file:
    product_reader = csv.DictReader(inputfile, delimiter=',', quotechar='"')
    magento_writer = csv.DictWriter(magento_file, delimiter=',', quotechar='"', fieldnames = magento_fieldnames, quoting=csv.QUOTE_ALL)
    magento_writer.writeheader()
    for row in product_reader:
      urls_file.write(row.get('image_file') + '\n')
      magento_writer.writerow(create_magento_dict(row))
