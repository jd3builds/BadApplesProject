import requests
from bs4 import BeautifulSoup
from bs4 import Tag

def scrape_category_of_items(URL):
    r = requests.get(url=URL)

    soup = BeautifulSoup(r.text)

    for list in soup.find_all('div', {'class': 'arrow-list'}):
        for li in filter(lambda x: type(x) is Tag, list.ul.contents):
            name = li.a.contents[0]
            url = li.a['href']
            scrape_single_item_from_page(url, name)

# Working for fruit pages
def scrape_single_item_from_page(URL, general_name):
    r = requests.get(url=URL)

    soup = BeautifulSoup(r.text, "html.parser")
    categories = []
    items = []

    possible_storages = ['Counter', 'Refrigerator', 'Freezer', 'Pantry', 'Shelf', 'Fridge']

    for tr in filter(lambda x: type(x) is Tag, soup.select('div table')[0].tbody.children):
        current_contents = list(filter(lambda x: type(x) is Tag, tr.contents))

        if len(current_contents) == 0:
            if len(tr.contents) != 0 and "opened" in str(tr.contents[0]).lower():
                categories[0] = str(tr.contents[0])
            continue
        if len(current_contents) > 1 and len(current_contents[1].contents) != 0 and str(current_contents[1].contents[0]) in possible_storages:
            categories.clear()
            for th in current_contents:
                categories.extend(list(map(lambda x: str(x), th.contents)))
            if len(current_contents[0].contents) == 0:
                categories.insert(0, '-')
        else:
            if "Date" in current_contents[1].contents[0]:
                continue
            name = current_contents[0].contents[0].contents[0]
            for i in range(1, len(categories)):
                items.append((general_name, name, categories[0], categories[i], current_contents[i].contents[0], URL))
    print(items)

if __name__ == '__main__':
    scrape_category_of_items("https://www.eatbydate.com/fruits/fresh/")
