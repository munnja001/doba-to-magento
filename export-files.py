#!/usr/bin/env python
import sys, requests, os, re, json, config
from bs4 import BeautifulSoup


def save_list_as_file(file_name, list_url):
    with open(file_name, 'wb+') as magento_file:
        r = client.get('http://www.doba.com' + list_url)
        export_data = dict(use_search='1',in_inventory='1', format='1', submitted='Download Only')
        r = client.post('http://www.doba.com/members/data-export/instant', data=export_data, stream=True)
        if r.ok:
            for block in r.iter_content(1024):
                if not block:
                    break
                
                magento_file.write(block)
        print 'Done with file ' + file_name


client = requests.session()

# Retrieve the CSRF token first
print 'Hitting Doba.com to establish session'
client.get(config.login_url)  # sets cookie
print 'Session established'
csrftoken = client.cookies['csrftoken']

login_data = dict(username=config.doba_email, password=config.doba_password, csrfmiddlewaretoken=csrftoken)
print 'Logging onto Doba.com'
r = client.post(config.login_url, data=login_data, headers=dict(Referer=config.login_url))
print 'Downloading Inventory List'
r = client.get('http://www.doba.com/win/members/my-inventory/show-lists')
inventory_lists = BeautifulSoup(r.text).find_all('a', text = re.compile(config.team_prefix))
print 'Found ' + str(len(inventory_lists)) + ' lists with the prefix ' + config.team_prefix
category_file_dict = dict()
for inventory_list_elem in inventory_lists:
    list_name = inventory_list_elem.string
    split_name = list_name.split('-')
    team = split_name[0].strip()
    category = split_name[1].strip()
    sub_category = None
    if len(split_name) > 2:
        sub_category = split_name[2].strip()
    
    if sub_category is not None:
        file_dir = config.export_dir + '/' + config.slugify(team) + '/' + config.slugify(category)
        file_name = file_dir + '/' + config.slugify(sub_category) + '.csv'
        category_file_dict[category + "/" + sub_category] = file_name
    else:
        file_dir = config.export_dir + '/' + config.slugify(team) + '/' + config.slugify(category)
        file_name = file_dir + '.csv'
        category_file_dict[category] = file_name
    if not os.path.exists(file_dir):
        os.makedirs(file_dir)
    print 'Saving File with name ' + file_name
    save_list_as_file(file_name, inventory_list_elem.get('href'))

with open('config.json', 'w+') as config_file:
  json.dump(category_file_dict, config_file)