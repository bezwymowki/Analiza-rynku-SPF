import requests
from bs4 import BeautifulSoup
import numpy as np
import pandas as pd
import re
import time


main_page = "https://wizaz.pl"
pages_to_scrap = ["https://wizaz.pl/kosmetyki/kremy-z-filtrem-do-twarzy" if x == 0 else "https://wizaz.pl/kosmetyki/kremy-z-filtrem-do-twarzy?page=" + str(x) for x in range(54)]
products_url = []
products_data = []


def crawler_products():
    while pages_to_scrap:
        current_url = pages_to_scrap.pop(0)
        response = requests.get(current_url)
        soup = BeautifulSoup(response.content, "html.parser")
        links = soup.select("a[href]")
        for link in links:
            url = link["href"]
            if "/kosmetyki/produkt" in url:
                final_url = main_page + url
                products_url.append(final_url)

def product_data_scrapping():
    count = 0
    while products_url:
        current_url = products_url.pop(0)
        response = requests.get(current_url)
        soup = BeautifulSoup(response.content, "html.parser")

        brand = soup.find("a", attrs={"class": "font-bold"}).text
        name = str((soup.find("h1").text))
        name = name.replace(f"{brand} ", "")
        second_name = str(soup.find(class_="mt-5"))
        name = name.replace(str(f"\xa0{second_name}"), "")

        try:
            rating = soup.find("div", attrs={"data-test-id": "heading-text-rating"}).text
            rating = re.search(r"[0-9],?[0-9]?", rating)[0].replace(",", ".")
            rating_count = soup.find("span", attrs={"class":"ml-10 text-primary"}).text
            rating_count = re.search(r"[0-9]+", rating_count)[0]
        except:
            rating = None
            rating_count = None

        offer = soup.find_all("span", attrs={"class":"text-24 font-bold leading-tight"})
        prices = []
       
        for o in offer:
            of = float(o.string.replace(",", "."))
            prices.append(of)
        if len(prices) == 0:
            median_price = None
        else:
            median_price = round(float(np.median(prices)), 2)
        
        info = soup.find_all("td")
        info_dict = {}
        for i in range(0, len(info), 2):
            key = info[i].string.replace(":", "")
            value = info[i+1].text
            info_dict[key] = value

        if spf := re.search(r"SPF\s?[0-9]+", name):
            spf = spf[0].replace("SPF", "").strip()
        elif spf:= re.search(r"SPF\s?[0-9]+", second_name):
            spf = spf[0].replace("SPF", "").strip()
        else:
            spf = None

        if "Konsystencja" in info_dict.keys():
            p_type = info_dict["Konsystencja"]
        else:
            p_type = None
            
        if "Typ cery" in info_dict.keys():
            skin_type = info_dict["Typ cery"]
        else:
            skin_type = None

        if "Właściwości" in info_dict.keys():
            properties = info_dict["Właściwości"]
        else:
            properties = None

        data = {"brand": brand,
                "name": name,
                "price": median_price,
                "rating": rating,
                "rating_count": rating_count,
                "product_type": p_type,
                "skin_type": skin_type,
                "properties": properties,
                "SPF": spf
                }

        products_data.append(data)

crawler_products()
product_data_scrapping()
data = pd.DataFrame(products_data)
data.to_csv("./spf_data.csv", encoding="utf-8-sig")
print("done")

            