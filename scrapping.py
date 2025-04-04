import requests
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup

def extract_urls_from_sitemap(sitemap_url):

    urls = []
    headers = {'User-Agent': 'Mozilla/5.0'}

    response = requests.get(sitemap_url, headers=headers, timeout=30)
    response.raise_for_status()
    xml_content = response.text

    namespaces = {'sm': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
    root = ET.fromstring(xml_content)

    for url_element in root.findall('sm:url', namespaces):
        loc_element = url_element.find('sm:loc', namespaces)
        if loc_element is not None and loc_element.text:
            urls.append(loc_element.text.strip())

    return urls

def subset_urls(urls):
    return [u for u in urls if "www.meilleurtaux.com/credit-immobilier" in u]

def download_page_source(url):
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        return response.text

    except Exception as e:
        print(f"Une erreur inattendue est survenue pour l'URL {url} : {e}")
        return None
    
def extract_and_clean_content(html_content):

    try:
        soup = BeautifulSoup(html_content, 'html.parser')

        extracted_data = {'description': None, 'main_content_text': None, 'main_content_html': None}

        meta_tag = soup.find('meta', attrs={'name': 'description'})
        if meta_tag and meta_tag.get('content'):
            extracted_data['description'] = meta_tag['content'].strip()
        else:
            print("Avertissement : Balise meta description non trouvée.")

        balises = ['div.item-page.actusDetail', 'div.item-page', 'div.article-full', 'div.ct-sidebar-right']
        for balise in balises:
            main_div = soup.select_one(balise)
            if main_div:
                extracted_data['main_content_text'] = main_div.get_text(separator=' ', strip=True)
                extracted_data['main_content_html'] = str(main_div)
                break
            else:
                print(f"Avertissement : La div '{balise}' n'a pas été trouvée.")

        return extracted_data

    except Exception as e:
        print(f"Erreur lors de l'analyse HTML avec BeautifulSoup : {e}")
        return {'description': None, 'main_content_text': None, 'main_content_html': None}