import unittest
import marlin
import ujson as json


class MarlinTest(unittest.TestCase):

    def setUp(self):
        app = marlin.app
        app.config['TESTING'] = True
        self.client = app.test_client()

    def test_001_ping(self):
        resp = self.client.get("/ping/")
        self.assertTrue(resp.status, 200)

    def test_002_post_item(self):
        resp = self.client.post(path="/api/v1/fruits/", data={"name": "Apple", "calories": 52, "price": 120.00})
        self.assertTrue(json.loads(resp.data), dict(price=120.00, calories=52, name="Apple", id=1))

    def test_003_get_item(self):
        resp = self.client.get("/api/v1/fruits/1/")
        self.assertTrue(json.loads(resp.data), dict(price=120.00, calories=52, name="Apple", id=1))

    def test_004_get_list(self):
        resp = self.client.get("/api/v1/fruits/")
        self.assertTrue(json.loads(resp.data), list(dict(price=120.00, calories=52, name="Apple", id=1)))

    def test_005_delete_item(self):
        resp = self.client.delete("/api/v1/fruits/1/")
        self.assertTrue(resp.status, 200)

    def test_006_delete_all(self):
        resp = self.client.delete("/api/v1/fruits/")
        self.assertTrue(resp.status, 200)
        resp = self.client.post(path="/api/v1/fruits/", data={"name": "Apricot", "calories": 48, "price": 80.00})
        self.assertGreater(json.loads(resp.data).get("id"), 1)

    def test_007_flush_db(self):
        resp = self.client.delete("/api/v1/fruits/", data={'force': 1})
        self.assertTrue(resp.status, 200)
        resp = self.client.get("/api/v1/fruits/")
        self.assertTrue(json.loads(resp.data), {"status": "No data Found"})

if __name__ == '__main__':
    unittest.main()