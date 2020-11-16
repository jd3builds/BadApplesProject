import numpy as np

def match(target_item, current_items, debug=False):
    max = -1
    curr = None
    for i in current_items:
        first = target_item.lower()
        second = i.lower() if debug else i[0].lower()

        ratio = levenshtein(first, second).item() * 0.3 + dice_coefficient(first, second) * 0.7
        if ratio > max:
            curr = i
            max = ratio
    if debug:
        print("- Target string " + target_item + " matched to " + curr + " with ratio of " + str(max))
    return curr

def match_item(raw_item):
    sql_query_all_item = """SELECT * FROM general_items"""

    connection = create_connection("expirations.db")

    if connection is not None:
        curs = execute_sql(connection, sql_query_all_item, (), commit=False)
        results = curs.fetchall()
        return match(raw_item, results)
    else:
        print("Unable to create expirations.db.")
        return None

def levenshtein(s, t):
    rows = len(s)+1
    cols = len(t)+1
    distance = np.zeros((rows,cols), dtype = int)

    for i in range(1, rows):
        for k in range(1,cols):
            distance[i][0] = i
            distance[0][k] = k

    for col in range(1, cols):
        for row in range(1, rows):
            if s[row-1] == t[col-1]:
                cost = 0
            else:
                cost = 2
            distance[row][col] = min(distance[row-1][col] + 1,      # Cost of deletions
                                 distance[row][col-1] + 1,          # Cost of insertions
                                 distance[row-1][col-1] + cost)     # Cost of substitutions
    Ratio = ((len(s)+len(t)) - distance[row][col]) / (len(s)+len(t))
    return Ratio

def dice_coefficient(a, b):
    """dice coefficient 2nt/(na + nb)."""
    if not len(a) or not len(b): return 0.0
    if len(a) == 1:  a = a + u'.'
    if len(b) == 1:  b = b + u'.'

    a_bigram_list = []
    for i in range(len(a) - 1):
        a_bigram_list.append(a[i:i + 2])
    b_bigram_list = []
    for i in range(len(b) - 1):
        b_bigram_list.append(b[i:i + 2])

    a_bigrams = set(a_bigram_list)
    b_bigrams = set(b_bigram_list)
    overlap = len(a_bigrams & b_bigrams)
    dice_coeff = overlap * 2.0 / (len(a_bigrams) + len(b_bigrams))
    return dice_coeff


""" duplicate bigrams in a word should be counted distinctly
(per discussion), otherwise 'AA' and 'AAAA' would have a
dice coefficient of 1...
"""

def dice_coefficient(a, b):
    if not len(a) or not len(b): return 0.0
    """ quick case for true duplicates """
    if a == b: return 1.0
    """ if a != b, and a or b are single chars, then they can't possibly match """
    if len(a) == 1 or len(b) == 1: return 0.0

    """ use python list comprehension, preferred over list.append() """
    a_bigram_list = [a[i:i + 2] for i in range(len(a) - 1)]
    b_bigram_list = [b[i:i + 2] for i in range(len(b) - 1)]

    a_bigram_list.sort()
    b_bigram_list.sort()

    # assignments to save function calls
    lena = len(a_bigram_list)
    lenb = len(b_bigram_list)
    # initialize match counters
    matches = i = j = 0
    while (i < lena and j < lenb):
        if a_bigram_list[i] == b_bigram_list[j]:
            matches += 2
            i += 1
            j += 1
        elif a_bigram_list[i] < b_bigram_list[j]:
            i += 1
        else:
            j += 1

    score = float(2 * matches) / float(lena + lenb)
    return score

def run_validity_test(current_items):
    rate = 0

    # ---- Walmart website

    # Test 1
    rate += match("Great Value Naturally Hickory Smoked Bacon", current_items, debug=True) == 'Cooked Bacon'

    # Test 2
    rate += match("Libbys Corned Beef 12 Ounce", current_items, debug=True) == 'Corned Beef'

    # Test 3
    rate += match("Almond Breeze Chocolate", current_items, debug=True) == 'Almond Milk'

    # ---- Receipts

    # Test 4
    rate += match("BaNana OG", current_items, debug=True) == 'Fresh Bananas'

    # Test 5
    rate += match("NATRL GROUND BEE!", current_items, debug=True) == 'Ground Beef'

    # Test 6
    rate += match("STRWBRY CC", current_items, debug=True) == 'Fresh Whole Strawberries'

    # Test 7
    rate += match("TOMATOES CRUSHED NO SALT", current_items, debug=True) == 'Canned Tomatoes'

    # Test 8
    rate += match("CHICKEN", current_items, debug=True) == 'Fresh Chicken'

    # Test 9
    rate += match("BULK ORANGES", current_items, debug=True) == 'Fresh Oranges'

    # Test 10
    rate += match("BEANS", current_items, debug=True) == 'Canned Beans'

    # Test 11
    rate += match("SC BLK ANGS", current_items, debug=True) == 'Hamburgers'

    # Test 12
    rate += match("MKS HOT DOGS", current_items, debug=True) == 'Fresh Hot Dogs'

    # Test 13
    rate += match("DELI HOT DOGS", current_items, debug=True) == 'Fresh Hot Dogs'

    # Test 14
    rate += match("RED GRAPE", current_items, debug=True) == 'Grapes'

    # Test 15
    rate += match("GRAPE TOMATO", current_items, debug=True) == 'Fresh Tomatoes'

    # Test 16
    rate += match("PINEAPPLE EACH", current_items, debug=True) == 'Pineapple (Whole)'

    # Test 17
    rate += match("PUBLIX STRAWBERRY", current_items, debug=True) == 'Fresh Whole Strawberries'

    # Test 18
    rate += match("GM WHOLE CHICKEN", current_items, debug=True) == 'Fresh Chicken'

    print(rate)

    print("Accuracy rate: ", rate / 18)

if __name__ == '__main__':
    current_items = {'Cooked Bacon', 'All Milk Alternatives', 'Lemon Juice', 'Pre-packaged Deli Meats', 'Fresh Hot Dogs', 'Thanksgiving Turkey', 'Fresh Lemons', 'Homemade Guacamole', 'Chia Gel', 'Fresh Pea Pods', 'Fresh Cut Pumpkins', 'Dried Split Peas (with O2 absorbers)', 'Chicken Broth', 'Packaged Fresh Cut Apples', 'Grapes', 'Pomegranate Seeds', 'Peaches (Cut)', 'Canned Clams', 'Fresh Squeezed Lemonade', 'Fresh Ground Pork', 'Natural Peanut Butter', 'Applesauce', 'Fresh Pumpkins', 'Cooked Peas', 'Bean Sprouts', 'Fresh Coconuts', 'Fresh Beef', 'Fresh Tomatoes', 'Fresh Pork Shoulder', 'Fresh Pork Loin', 'Fresh Green Beans', 'Cooked Hot Dogs', 'Bacon Bits', 'Fresh Whole Strawberries', 'Hummus', 'Custard Pie', 'Spam', 'Quiche', 'Fresh Avocados', 'Cooked Turkey', 'Canned Peas', 'Lime Juice', 'Pumpkin Pie', 'Canned Chicken', 'Homemade Turkey Soup', 'Fresh Figs', 'Sunflower Seeds (Roasted - In-Shell)', 'Cooked Beans', 'Cut Oranges', 'Fresh Pork Chops', 'Corned Beef', 'Refrigerator Pie Crust', 'Cocount Milk', 'Homemade Roasted Coconut', 'Fresh Bacon', 'Pomegranates', 'Walnuts', 'Roasted Sesame Seeds', 'Fresh Snap Peas', 'Almonds', 'Ham', 'Tofu', 'Flax Seeds ', 'Tahini Paste', 'Fresh Limes', 'Homemade Peanut Butter', 'Homemade Chicken Broth', 'Sesame Seeds (Raw)', 'Pecans', 'Cooked Pumpkin', 'Flax Meal ', 'Canned Corn Beef', 'Deviled Ham', 'Frozen Puff Pastry', 'Processed Limeade', 'Pot Pie', 'Cashews', 'Macadamias', 'Lentils (Dried)', 'Soy Milk', 'Nectarines (Whole)', 'Brazil Nuts', 'Cut Limes', 'Chia Meal', 'Tahini', 'Packaged Coconut', 'Fresh Oranges', 'Packaged (Dried) Coconut', 'Pork Sausage ', 'Pine Nuts', 'Cooked Pork Shoulder/Loin/Chops/Sausage', 'Fresh Whole Blueberries', 'Dried Split Peas (regular packaging)', 'Fresh Bananas', 'Fruit Pie', 'Hamburgers', 'Pineapple (Cut)', 'Fresh Lemon Juice', 'Fresh Cut Strawberries', 'Fresh Apples', 'Pepperoni', 'Bacon', 'Packaged Lunch Meat', 'Fresh Chicken', 'Canned Beef (Opened)', 'Canned Beans', 'Crunchy Peanut Butter', 'Bologna', 'Pie with fresh fruit', 'Pie Crust Mix', 'Sunflower Seeds (Roasted - Shelled)', 'Beef or Steak', 'Chic Peas', 'Processed Lemonade', 'Hazelnuts', 'Pineapple (Whole)', 'Ground Turkey', 'Cream Pie', 'Chia Seeds', 'Sunflower Seeds (Raw)', 'Fresh Whole Cherries', 'Dried Beans', 'Rice Milk', '(Raw) Ground Turkey', 'Cut Lemons', 'Pistachios', 'Canned Tomatoes', 'Peaches (Whole)', 'Peanuts', 'Roasted Chicken', 'Processed Lemonade (Opened)', 'Coconut Oil', 'Steak ', 'Deli Turkey', 'Canned Tuna', 'Coconut Milk', 'Corned Beef ', 'Ground Beef', 'Hemp Milk', 'Cooked Chicken', 'Turkey Salad', 'Canned Pumpkin', 'Chicken bullion cubes', 'Baked Puff Pastry ', 'Almond Milk', 'Sun Butter ', 'Fresh Deli Meats', 'Apple Pie', '(Raw) Fresh Turkey', 'Salami ', 'Smooth Peanut Butter'}
    run_validity_test(current_items)
