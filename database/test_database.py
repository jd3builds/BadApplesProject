import unittest
import database

blueberries = ('blueberries', 21, 'fruit', 'berries', 'fridge', False, 2, 4, 'days')
wild_blueberries = ('wild blueberries', 24, 'fruit', 'berries', 'fridge', False, 1, 5, 'days')
strawberries = ('strawberries', 22, 'fruit', 'berries', 'fridge', False, 1, 3, 'weeks')
blackberries = ('blackberries', 23, 'fruit', 'berries', 'fridge', False, 2, 5, 'months')
blue_lollipops = ('blue lollipops', 25, 'candy', None, None, False, 999, None, 'years')


class TestUserItems(unittest.TestCase):
    def setUp(self):
        database.create_user_table()

    def test_add_unique_item_and_remove(self):
        self.assertTrue(database.insert_user_table(blueberries))
        self.assertTrue(database.delete_user_item(blueberries[1]))

    def test_delete_all(self):
        self.assertTrue(database.insert_user_table(blueberries))
        self.assertTrue(database.insert_user_table(strawberries))
        self.assertTrue(database.insert_user_table(blackberries))
        self.assertTrue(database.delete_all_user_items())

    def test_query_by_id(self):
        self.assertTrue(database.insert_user_table(strawberries))
        self.assertTrue(database.insert_user_table(blueberries))
        self.assertTrue(database.insert_user_table(blackberries))
        result = database.query_user_item_by_id(blueberries[1])
        self.assertIsNotNone(result)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0][1], blueberries[1])

    def test_query_multiple_items_by_name(self):
        self.assertTrue(database.insert_user_table(blueberries))
        self.assertTrue(database.insert_user_table(wild_blueberries))
        self.assertTrue(database.insert_user_table(blue_lollipops))
        result = database.query_user_item_by_name('blue')
        self.assertIsNotNone(result)
        self.assertEqual(len(result), 3)

    def tearDown(self):
        database.delete_all_user_items()


if __name__ == "__main__":
    unittest.main()
