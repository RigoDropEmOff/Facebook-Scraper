from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import re
from IPython.display import HTML
import os
import webbrowser

from bs4 import BeautifulSoup as soup
import re
import pandas as pd
import matplotlib.pyplot as plt
import time

#increase display screen
pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)
pd.set_option('display.max_colwidth', None)


#Set up FireFox options
firefox_options = Options()

#Set up firefox WebDriver
service = Service('/usr/local/bin/geckodriver')
browser = webdriver.Firefox(service = service, options=firefox_options)

#Set up base URl
base_url = "https://www.facebook.com/marketplace/104186169619214/search?"

#Set up search parmeters
min_price = 1000
max_price = 15000

#Set up full url
url = f"{base_url}minPrice={min_price}&maxPrice={max_price}&query=Trucks&exact=false"

#visit the url
browser.get(url)

#Scroll down to load more results
scroll_count = 5
scroll_delay = 2.5
for _ in range(scroll_count):
    browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(scroll_delay)

#Parse the HTML
html = browser.page_source
#print(html)

#Create a BeautifulSoup object from the scraped HTML
market_soup = soup(html, 'html.parser')

#check if HTML was scraped Correctly
market_soup

#Close automated browser session
#browser.quit()

#extract all necessary info and insert into lists
titles_div = market_soup.find_all("span", class_="x1lliihq x6ikm8r x10wlt62 x1n2onr6") 
titles_list = [title.text.strip() for title in titles_div[2:]]
prices_div = market_soup.find_all("span", class_="x193iq5w xeuugli x13faqbe x1vvkbs xlh3980 xvmahel x1n0sxbx x1lliihq x1s928wv xhkezso x1gmr53x x1cpjm7i x1fgarty x1943h6x x4zkp8e x676frb x1lkfr7t x1lbecb7 x1s688f xzsf02u")
prices_list = [price.text.strip() for price in prices_div]
miles_div = market_soup.find_all("span", class_="x1lliihq x6ikm8r x10wlt62 x1n2onr6 xlyipyv xuxw1ft")
miles_list = [miles.text.strip() for miles in miles_div[12:-3]]
miles_list = [
    re.search(r'(\d+(?:\.\d+)?)[Kk]?\s*miles?', item)
    for item in miles_list
    if re.search(r'(\d+(?:\.\d+)?)[Kk]?\s*miles?', item)
]
miles_list = [
    match.group().split()[0]  # This gets the first word of the match, e.g., '12K'
    for match in miles_list
    if match  # This checks if the match object is not None
]
links_list = []
listings = market_soup.find_all('a', class_='x1i10hfl xjbqb8w x1ejq31n xd10rxx x1sy0etr x17r0tee x972fbf xcfux6l x1qhh985 xm0m39n x9f619 x1ypdohk xt0psk2 xe8uvvx xdj266r x11i5rnm xat24cr x1mh8g0r xexx8yu x4uap5 x18d9i69 xkhd6sd x16tdsg8 x1hl2dhg xggy1nq x1a2a7pz x1heor9g x1sur9pj xkrqix3 x1lku1pv')
for listing in listings:
    if listing.has_attr('href'):
        full_link = 'https://www.facebook.com' + listing['href']
        links_list.append(full_link)



# Function to extract year
def extract_year(model_string):
    match = re.search(r'\b(19|20)\d{2}\b', str(model_string))
    return match.group() if match else None

# Print a few samples from titles_list to check the data
print("Sample titles:")
for title in titles_list[:5]:
    print(title)

# Check lengths of all lists
print("\nList lengths:")
print(f"titles_list: {len(titles_list)}")
print(f"prices_list: {len(prices_list)}")
print(f"miles_list: {len(miles_list)}")
print(f"links_list: {len(links_list)}")

# Find the minimum length
min_len = min(len(titles_list), len(prices_list), len(miles_list), len(links_list))

# Truncate all lists to the minimum length
titles_list = titles_list[:min_len]
prices_list = prices_list[:min_len]
miles_list = miles_list[:min_len]
links_list = links_list[:min_len]

# Print lengths again after truncation
print("\nList lengths after truncation:")
print(f"titles_list: {len(titles_list)}")
print(f"prices_list: {len(prices_list)}")
print(f"miles_list: {len(miles_list)}")
print(f"links_list: {len(links_list)}")

# Create DataFrame
df = {
    "Model": titles_list,
    'Price': prices_list,
    'Miles': miles_list,
    "Link": links_list
}

mydf = pd.DataFrame(df)

# Print the first few rows of the DataFrame
print("\nFirst few rows of the DataFrame:")
print(mydf.head())

# Now add the Year column
mydf['Year'] = mydf['Model'].apply(extract_year)

# Remove the year from the "Model" column
mydf['Model'] = mydf['Model'].apply(lambda x: re.sub(r'\b(19|20)\d{2}\b', '', str(x)).strip())

# Reorder columns
mydf = mydf[['Year', 'Model', 'Price', 'Miles', 'Link']]

# Print the final DataFrame
print("\nFinal DataFrame:")
print(mydf.head())
print(f"\nDataFrame shape: {mydf.shape}")

#Find the length of the shortest list
min_len = min(len(titles_list), len(prices_list), len(miles_list), len(links_list))
#Truncate all lists to the minimum length
#year_list = year_list[:min_len]
titles_list = titles_list[:min_len]
prices_list = prices_list[:min_len]
miles_list = miles_list[:min_len]
links_list = links_list[:min_len]
year_list = mydf['Year'].tolist()

#handle potential non-numeric values
mydf['Year'] = pd.to_numeric(mydf['Year'], errors= 'coerce')
#convert to INt64
mydf['Year'] = mydf['Year'].fillna(0).astype(int)

#clean price column
mydf['Price']= mydf['Price'].replace('[\$,]','', regex = True)
mydf['Price'] = pd.to_numeric(mydf['Price'], errors= 'coerce')
#Format prices with columns
def format_price(price):
    return f"${price:,.0f}"
mydf['Price'] = mydf['Price'].apply(format_price)

#clean miles column
def convert_miles(miles_str):
    if pd.isna(miles_str):
        return pd.NA
    miles_str = str(miles_str).upper()
    if miles_str.endswith('K'):
        return float(miles_str[:-1]) * 1000
    return float(miles_str)

#convert miles to numeric
mydf["Miles"] = mydf['Miles'].apply(convert_miles)
#Format miles with commas
mydf['Miles'] = mydf['Miles'].apply((lambda x: f"{x:,.0f}" if pd.notna(x) else ''))

print(len(titles_list))
print(len(prices_list))
print(len(miles_list))
print(len(links_list))
print(len(mydf['Year']))
#print(titles_list)
#print(prices_list)
#print(miles_list)
#print(links_list)

# Print the first few rows to verify
print(mydf[['Year', 'Model']].head())
#Save the dataframe as an HTML file
#mydf.to_html('listings.html', render_links=True, escape=False)
print(mydf)
#open the HTML file with Lynx
#os.system('lynx listings.html')

print(mydf.columns)
year_list = mydf['Year'].tolist()
print(mydf.dtypes)

def get_mileage_color(miles):
    if miles <= 99000:
        return "#2ecc71"
    elif miles <= 199000:
        return "#f39c12"
    else:
        return "#e74c3c"


css_styles = '''
<style>
    body{
    font-family: Arial, sans-serif;
    line-height: 1.5;
    color: #333;
    max-width: 800px;
    margin: 0 auto;
    padding: 20px
    }
    h1 {
        color: #2c3e50;
        text-align: center;
        font-weight: bold;
        padding-top: 10px;
        padding-bottom: 10px;
    }
    .truck-listing {
        background-color: #f9f9f9;
        border: 1px solid #ddd;
        border-radius: 5px;
        padding: 15px;
        margin-bottom: 20px;
    }
    .truck-model {
        font-size: 18px;
        font-weight: bold;
        color: #3498db;
    }
    .truck-details {
        margin-top: 10px;
    }
    .truck-price {
        font-weight: bold;
        color: black;
        padding-right: 5px
    }
    .view-listing {
        display: inline-block;
        background-color: #3498db;
        color: white;
        padding: 8px 15px;
        text-decoration: none;
        border-radius: 3px;
        margin-top: 10px;
    }
    .view-listing:hover {
        background-color: #2980b9;
    }
    a {
            color: #3498db;
            text-decoration: none;
        }
        a:hover {
            text-decoration: underline;
        }
    a:visited {
        text-decoration: none;
        color: violet;}
</style>
'''
    
#After creating the data frame
html_content = f"""
<html>
<head>
    <title>Facebook Trucks</title>
    {css_styles}
    </head>
<body>
    <h1>Facebook Trucks</h1>
    """
for index, row in mydf.iterrows():
    miles = int(row['Miles'].replace(',', ''))
    mileage_color = get_mileage_color(miles)
    html_content += f"""
    <div class="truck-listing">
        <div class="truck-model">{row['Model']} ({row['Year']})</div>
        <div class="truck-details">
            <span class="truck-price">{row['Price']}</span>
            <span style="color: {mileage_color};">{row['Miles']} miles</span>
        </div>
        <a href='{row['Link']}' target='_blank'>View Listing</a>
    </div>
        """
    
html_content += '''
</body>
</html>
'''
    
#write the html content to a file
with open('listings.html', 'w') as f:
    f.write(html_content)

print("An HTML file 'listings.html' has been created. You can open it in your web browser.")

#opening the file
filename = 'listings.html'
with open(filename, 'w') as f:
    f.write(html_content)

print(f"An HTML file {filename} has been created and will open on a web browser.")
webbrowser.open('file://' + os.path.realpath(filename))