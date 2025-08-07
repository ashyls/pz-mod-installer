import requests
from bs4 import BeautifulSoup

def get_mod_dependencies(mod_id):
    """Fetches and returns a list of dependency mod IDs from a Steam Workshop page."""
    url = f"https://steamcommunity.com/sharedfiles/filedetails/?id={mod_id}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        required_items = []
        required_div = soup.find("div", class_="requiredItemsContainer")
        if required_div:
            required_items = [
                a["href"].split("id=")[1] 
                for a in required_div.find_all("a", href=True) 
                if "id=" in a["href"]
            ]
        
        if not required_items:
            required_items = list(set([
                tag["data-publishedfileid"] 
                for tag in soup.find_all(attrs={"data-publishedfileid": True})
                if tag["data-publishedfileid"] != mod_id
            ]))
        
        return required_items

    except Exception as e:
        print(f"Error fetching dependencies for mod {mod_id}: {e}")
        return []