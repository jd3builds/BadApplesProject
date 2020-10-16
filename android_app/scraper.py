import requests
from bs4 import BeautifulSoup
from bs4 import Tag
from android_app.database import insert_general_table

counter = 0

def get_unopened(raw):
    val = None
    if raw == '(Unopened/Opened)' or raw == '-':
        val = None
    elif "unopened" in raw.lower():
        val = False
    elif "opened" in raw.lower():
        val = True
    # print(str(val) + " for " + raw + " and " + str("opened" in raw.lower()) + " and " + str("unopened" in raw.lower()))
    return val

def get_lower_and_upper_range(raw):
    if '(' in raw:
        raw = raw[0: raw.index('(')]
    # Fix this case
    if '--' in raw:
        return None
    if '-' == raw:
        return None
    # Fix this case
    if "Year" in raw and "Months" in raw:
        return None

    if "date" in raw:
        raw = ' '.join(raw.split()[0:2])

    if raw == 'Same Day':
        return (1, 1, 'Day')
    elif '-' in raw:
        index = raw.index('-')
        return (int(raw[0:index]), int(raw[index + 1:index + 2]), raw[index + 3:].replace(" ", ""))
    else:
        index = raw.index(' ')
        return (int(raw[0:index]), None, raw[index + 1:].replace(" ", ""))


def scrape_category_of_items(URL, category, subcategory):
    r = requests.get(url=URL)

    soup = BeautifulSoup(r.text)

    for list in soup.find_all('div', {'class': 'arrow-list'}):
        for li in filter(lambda x: type(x) is Tag, list.ul.contents):
            name = li.a.contents[0]
            url = li.a['href']
            scrape_single_item_from_page(url, name, category, subcategory)

# Working for fruit pages
def scrape_single_item_from_page(URL, general_name, category,subcategory):
    global counter
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
                unopened = get_unopened(categories[0])
                ranges = get_lower_and_upper_range(current_contents[i].contents[0])
                if ranges is None:
                    pass
                    print("Unable to add item " + name)
                else:
                    item = (name, counter, category, subcategory, categories[i], unopened, ranges[0], ranges[1], ranges[2])
                    items.append(items)
                    insert_general_table(item)
                    print("Inserted: " + str(item))
                    counter += 1


if __name__ == '__main__':
    scrape_category_of_items("https://www.eatbydate.com/fruits/fresh/", "Fruits", "Fresh Fruits")