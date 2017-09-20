import unittest
import struct
from igvjs import app

class TestIGV(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        app.config['ALLOWED_EMAILS'] = 'test_emails.txt'
        app.config['USES_OAUTH'] = True
        app.config['PUBLIC_DIR'] = None
        self.app = app.test_client()

    def test_page_loads(self):
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'<title>IGV - Integrative Genomics Viewer</title>', response.data)

    def test_get_data_not_auth(self):
        response = self.app.get('static/data/public/gstt1_sample.bam')
        self.assertNotEqual(response, None)
        self.assertEqual(response.status_code, 401)

    def test_get_data_auth_disabled(self):
        app.config['USES_OAUTH'] = False
        response = self.app.get('static/data/public/gstt1_sample.bam')
        self.assertEqual(response.status_code, 200)

    def test_get_data_from_private_dir(self):
        app.config['PUBLIC_DIR'] = '/static/js'
        response = self.app.get('static/data/public/gstt1_sample.bam')
        self.assertEqual(response.status_code, 401)
        self.assertIn(b'Unauthorized', response.data)

    def test_get_data_range_header(self):
        start = 25
        size = 100
        response = self.app.get('../test/BufferedReaderTest.bin',
            headers={"Range": "bytes={}-{}".format(start, start+size)})
        for i in range(size):
            expected_value = -128 + start + i
            value = int(struct.unpack('b', response.data[i])[0])
            self.assertEqual(value, expected_value)


if __name__ == "__main__":
    unittest.main()
