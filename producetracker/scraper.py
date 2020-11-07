import requests
from bs4 import BeautifulSoup
from bs4 import Tag
from database import insert_general_table

counter = 0

def normalize_name(name):
    if ' lasts' in name:
        name = name.replace(' lasts', '')
    if ' last' in name:
        name = name.replace(' last', '')
    if '(hard)*' in name:
        name = name.replace('(hard)*', '')
    return name

def get_unopened(raw):
    val = None
    if raw == '(Unopened/Opened)' or raw == '-':
        val = None
    elif "unopened" in raw.lower():
        val = False
    elif "opened" in raw.lower():
        val = True
    return val

# Date amount to days (ex: 1 Year -> 365 days)
def get_bound(normalized, units):
    index = None
    for i, c in enumerate(normalized):
        if not c.isdigit():
            index = i
            break

    return int(normalized[0:index]) * units[normalized[index:]]

# Returns lower bound, upper bound, unit type
def get_lower_and_upper_range(raw):
    # Infinite amount of time
    if raw == 'Indefinite':
        return (99999, 99999, 'Days')
    # Edge case: contains + in name (ex: 2+ Years -> 2 Years)
    if '+' in raw:
        raw = raw.replace('+', '')
    # Edge case: unsure 'Cook First' means
    if raw == 'Cook first':
        return None
    if '(' in raw:
        raw = raw[0: raw.index('(')]
    # Fix this case
    if '--' in raw:
        return None
    if '-' == raw:
        return None

    # Contains several units of measurement
    if "Year" in raw and "Months" in raw:
        normalized = raw.replace(" ", "").lower()
        units = {
            "year": 365,
            "years": 365,
            "month": 30,
            "months": 30
        }
        dash = normalized.index('-')
        return (get_bound(normalized[0:dash], units), get_bound(normalized[dash + 1:], units), "Days")

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
def scrape_single_item_from_page(URL, general_name, category, subcategory):
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
        # Current row is an invalid header (Past printed date)
        if len(current_contents[1].contents) != 0 and str(current_contents[1].contents[0]) == 'Past Printed Date':
            continue
        # Current row is a header (unopened, pantry, etc...) containing non-product info
        if len(current_contents[1].contents) != 0 and str(current_contents[1].contents[0]) in possible_storages:
            categories.clear()
            for th in current_contents:
                categories.extend(list(map(lambda x: str(x), th.contents)))
            if len(current_contents[0].contents) == 0:
                categories.insert(0, '-')
        # Current row is a product row (item)
        else:
            if "Date" in current_contents[1].contents[0]:
                continue
            name = normalize_name(current_contents[0].contents[0].contents[0])
            for i in range(1, len(categories)):
                unopened = get_unopened(categories[0])
                ranges = get_lower_and_upper_range(current_contents[i].contents[0])
                if ranges is None:
                    print("Unable to add item " + name + " - " + categories[i] + " (range: "  + current_contents[i].contents[0] + ")")
                else:
                    item = (name, counter, category, subcategory, categories[i], unopened, ranges[0], ranges[1], ranges[2])
                    items.append(items)
                    insert_general_table(item)
                    print("Inserted: " + str(item))
                    counter += 1


if __name__ == '__main__':
    scrape_single_item_from_page("https://www.eatbydate.com/fruits/fresh/tomatoes-shelf-life-expiration-date//", "Apples", "Fruits", "Fresh Fruits")
    scrape_category_of_items("https://www.eatbydate.com/fruits/fresh/", "Fruits", "Fresh Fruits")
    scrape_category_of_items("https://www.eatbydate.com/proteins/beans-peas/", "Proteins", "Beans & Peas")
    scrape_single_item_from_page("https://www.eatbydate.com/proteins/meats/deli-meat-shelf-life-expiration-date/", "Deli Meat", "Proteins", "Deli Meat")
    scrape_category_of_items("https://www.eatbydate.com/proteins/meats/", "Proteins", "Meats")
    scrape_category_of_items("https://www.eatbydate.com/proteins/nuts/", "Proteins", "Nuts and Seeds")
    scrape_category_of_items("https://www.eatbydate.com/proteins/poultry/", "Proteins", "Poultry")
    scrape_category_of_items("https://www.eatbydate.com/proteins/poultry/", "Proteins", "Seafood")
    print("Added a total of " + str(counter) + " items to the database")