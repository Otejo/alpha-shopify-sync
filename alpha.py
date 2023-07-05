from ftplib import FTP_TLS
import ftplib
import ftputil
import csv
import shopify
from xml.etree import ElementTree
import requests
import time

APIKEY = "{ShopifyAPI key}"
PASSWORD = "{Shopify API_Password}"
ftpname = "alphabname"
ftppass = "alphabpassword"
shopify_location_id = "location id from Shopify"


#download updated csv from AB
my_session_factory = ftputil.session.session_factory(
                       base_class=ftplib.FTP_TLS,
                       #port=31,
                       encrypt_data_channel=True,
                       encoding="UTF-8")
                       #debug_level=2)



with ftputil.FTPHost('ftp.appareldownload.com', ftpname, ftppass, session_factory=my_session_factory) as host:
    name = 'inventory-can.txt'
    host.download(name, name)


###### Shopify ########
APIKEY = shop_api_key
PASSWORD = shop_password
shop_url1 = "https://%s:%s@{storename}.myshopify.com/admin" % (APIKEY, PASSWORD)

shop_url = "{storename}.myshopify.com"
api_version = '2021-10'
private_app_password = PASSWORD

session = shopify.Session(shop_url, api_version, private_app_password)
shopify.ShopifyResource.activate_session(session)


shop = shopify.Shop.current
shopify.ShopifyResource.set_site(shop_url1)


vendor = 'alphabroder'

def product_to_invID_sku(page):
    for x in page.variants:
        a = x.sku
        b = x.inventory_item_id
        c = {a:b}
        invId_sku.update(c)

#create a dictionary of inventory IDs and current Shopify Inventory levels
def getshopinv(product):
    for x in product.attributes['variants']:
        inv = x.attributes['inventory_quantity']
        pid = x.attributes['inventory_item_id']
        shopinv = {pid: inv}
        shop_variant_inv.update(shopinv)


invId_sku = {}
products = []
shop_variant_inv = {}

def get_product_from_vendor(vendor):
    page = shopify.Product.find(vendor=vendor)
    products.append(page)
    for x in page:
        product_to_invID_sku(x) # creates a dictionary of Alphabroder Sku's and Shopify Inventory Id's
        getshopinv(x) # creates a dictionary of Shopify Ids and current inventory levels
    num = 0
    while 0<1:
        try:
            url = page.next_page_url
            if url != None:
                page = shopify.Product.find(from_=url)
                products.append(page)
                for x in page:
                    product_to_invID_sku(x)
                    getshopinv(x)  
                num=num+1
                print(num)
                print(url)
            else:
                print('done')
                break
        except:
            print('error')


#################################################################################################################3

invId_sku = {}
products = []

get_product_from_vendor(vendor)



alpha = {}
with open('inventory-can.txt', newline='', encoding='utf-8', errors='ignore') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        a = {row['Item Number'] : row['RH']}
        alpha.update(a)

###### Needs to be fixed for Alphabroder


matched = {}

for key,value in invId_sku.items():
    alphaId = key
    inventoryid = value
    inventory = alpha.get(alphaId)
    shop_inv = shop_variant_inv.get(inventoryid)
    if (inventory != None) and (str(inventory) != str(shop_inv)):
        a = {inventoryid: inventory}
        matched.update(a)
print("going to update ",len(matched)," products")
time.sleep(15)



loc = shopify.Location.find(shopify_location_id)
def updateinv():
    stepa = 1
    for invId, inv in matched.items():
        shopify.InventoryLevel.set(location_id=loc.id, inventory_item_id=invId, available=inv)
        print(stepa, "Products updated", invId, "-", inv)
        for invId, inv in matched.items():
            a = invId
            b = inv
        stepa = stepa+1
        time.sleep(.6)
    print('All Done')

updateinv()
shopify.ShopifyResource.clear_session()