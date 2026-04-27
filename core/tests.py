from django.test import SimpleTestCase


class HealthTests(SimpleTestCase):
    def test_health(self):
        r = self.client.get("/health/")
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.content, b"ok")
