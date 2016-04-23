import unittest

from sdklib.renderers import FormRender


class TestFormRender(unittest.TestCase):

    def test_encode_form_data_files(self):
        files = {"file_upload": "resources/file.pdf", "file_upload2": "resources/file.png"}
        data = {"param1": "value1", "param2": "value2"}

        r = FormRender()
        body, content_type = r.encode_params(data, files=files)
        self.assertEqual(content_type, "application/x-www-form-urlencoded")
        self.assertIn("param2=value2", body)
        self.assertIn("param1=value1", body)
        self.assertNotIn("file_upload", body)

    def test_encode_form_data_as_2tuple_parameter(self):
        data = [("param1", "value1"), ("param2", "value2"), ("param2", "value3")]

        r = FormRender()
        body, content_type = r.encode_params(data)
        self.assertEqual(content_type, "application/x-www-form-urlencoded")
        self.assertEqual(body, "param1=value1&param2=value2&param2=value3")

    def test_encode_form_data_no_data(self):
        r = FormRender()
        body, content_type = r.encode_params()
        self.assertEqual(content_type, "application/x-www-form-urlencoded")
        self.assertEqual(body, "")

    def test_encode_form_data_array_default(self):
        data = {"param1": "value 1", "param2": ["value2", "value3"]}

        r = FormRender()
        body, content_type = r.encode_params(data)
        self.assertEqual(content_type, "application/x-www-form-urlencoded")
        self.assertIn("param2=value2", body)
        self.assertIn("param1=value+1", body)
        self.assertIn("param2=value3", body)

    def test_encode_form_data_array_multi(self):
        data = {"param1": "value 1", "param2": ["value2", "value3"]}

        r = FormRender(collection_format='multi')
        body, content_type = r.encode_params(data)
        self.assertEqual(content_type, "application/x-www-form-urlencoded")
        self.assertIn("param2=value2", body)
        self.assertIn("param1=value+1", body)
        self.assertIn("param2=value3", body)

    def test_encode_form_data_array_encoded(self):
        data = {"param1": "value 1", "param2": ["value2","value3"]}

        r = FormRender(collection_format='encoded')
        body, content_type = r.encode_params(data)
        self.assertEqual(content_type, "application/x-www-form-urlencoded")
        self.assertIn("param2=%5B%27value2%27%2C+%27value3%27%5D", body)
        self.assertIn("param1=value+1", body)

    def test_encode_form_data_array_csv(self):
        data = {"param1": "value 1", "param2": ["value2", "value3"]}

        r = FormRender(collection_format='csv')
        body, content_type = r.encode_params(data)
        self.assertEqual(content_type, "application/x-www-form-urlencoded")
        self.assertIn("param2[]=value2,value3", body)
        self.assertIn("param1=value+1", body)

    def test_encode_form_data_array_ssv(self):
        data = {"param1": "value 1", "param2": ["value2", "value3"]}

        r = FormRender(collection_format='ssv')
        body, content_type = r.encode_params(data)
        self.assertEqual(content_type, "application/x-www-form-urlencoded")
        self.assertIn("param2[]=value2 value3", body)
        self.assertIn("param1=value+1", body)

    def test_encode_form_data_array_tsv(self):
        data = {"param1": "value 1", "param2": ["value2", "value3"]}

        r = FormRender(collection_format='tsv')
        body, content_type = r.encode_params(data)
        self.assertEqual(content_type, "application/x-www-form-urlencoded")
        self.assertIn("param2[]=value2\tvalue3", body)
        self.assertIn("param1=value+1", body)

    def test_encode_form_data_array_pipes(self):
        data = {"param1": "value 1", "param2": ["value2", "value3"]}

        r = FormRender(collection_format='pipes')
        body, content_type = r.encode_params(data)
        self.assertEqual(content_type, "application/x-www-form-urlencoded")
        self.assertIn("param2[]=value2|value3", body)
        self.assertIn("param1=value+1", body)

