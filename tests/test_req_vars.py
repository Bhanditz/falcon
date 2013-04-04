import datetime

import falcon
from falcon.request import Request
import falcon.testing as testing


class TestReqVars(testing.TestBase):

    def before(self):
        self.qs = 'marker=deadbeef&limit=10'

        self.headers = {
            'Host': 'falcon.example.com',
            'Content-Type': 'text/plain',
            'Content-Length': '4829',
            'Authorization': ''
        }

        self.app = '/test'
        self.path = '/hello'
        self.relative_uri = self.path + '?' + self.qs
        self.uri = 'http://falcon.example.com' + self.app + self.relative_uri
        self.uri_noqs = 'http://falcon.example.com' + self.app + self.path

        self.req = Request(testing.create_environ(
            app=self.app,
            path='/hello',
            query_string=self.qs,
            headers=self.headers))

        self.req_noqs = Request(testing.create_environ(
            app=self.app,
            path='/hello',
            headers=self.headers))

    def test_missing_qs(self):
        env = testing.create_environ()
        if 'QUERY_STRING' in env:
            del env['QUERY_STRING']

        # Should not cause an exception when Request is instantiated
        Request(env)

    def test_empty(self):
        self.assertIs(self.req.auth, None)

    def test_reconstruct_url(self):
        req = self.req

        scheme = req.protocol
        host = req.get_header('host')
        app = req.app
        path = req.path
        query_string = req.query_string

        actual_url = ''.join([scheme, '://', host, app, path,
                              '?', query_string])
        self.assertEquals(actual_url, self.uri)

    def test_uri(self):
        self.assertEquals(self.req.url, self.uri)

        self.assertEquals(self.req.uri, self.uri)
        self.assertEquals(self.req_noqs.uri, self.uri_noqs)

    def test_relative_uri(self):
        self.assertEqual(self.req.relative_uri, self.app + self.relative_uri)
        self.assertEqual(
            self.req_noqs.relative_uri, self.app + self.path)

        req_noapp = Request(testing.create_environ(
            path='/hello',
            query_string=self.qs,
            headers=self.headers))

        self.assertEqual(req_noapp.relative_uri, self.relative_uri)

    def test_accept_xml(self):
        headers = {'Accept': 'application/xml'}
        req = Request(testing.create_environ(headers=headers))
        self.assertTrue(req.client_accepts_xml)

        headers = {'Accept': '*/*'}
        req = Request(testing.create_environ(headers=headers))
        self.assertTrue(req.client_accepts_xml)

        headers = {'Accept': 'application/json'}
        req = Request(testing.create_environ(headers=headers))
        self.assertFalse(req.client_accepts_xml)

        headers = {'Accept': 'application/xm'}
        req = Request(testing.create_environ(headers=headers))
        self.assertFalse(req.client_accepts_xml)

    def test_range(self):
        headers = {'Range': '10-'}
        req = Request(testing.create_environ(headers=headers))
        self.assertEquals(req.range, (10, -1))

        headers = {'Range': '10-20'}
        req = Request(testing.create_environ(headers=headers))
        self.assertEquals(req.range, (10, 20))

        headers = {'Range': '-10240'}
        req = Request(testing.create_environ(headers=headers))
        self.assertEquals(req.range, (-10240, -1))

        headers = {'Range': ''}
        req = Request(testing.create_environ(headers=headers))
        self.assertIs(req.range, None)

        headers = {'Range': None}
        req = Request(testing.create_environ(headers=headers))
        self.assertIs(req.range, None)

    def test_range_invalid(self):
        headers = {'Range': '10240'}
        req = Request(testing.create_environ(headers=headers))
        self.assertRaises(falcon.HTTPBadRequest, lambda: req.range)

        headers = {'Range': '-'}
        req = Request(testing.create_environ(headers=headers))
        self.assertRaises(falcon.HTTPBadRequest, lambda: req.range)

        headers = {'Range': '--'}
        req = Request(testing.create_environ(headers=headers))
        self.assertRaises(falcon.HTTPBadRequest, lambda: req.range)

        headers = {'Range': '-3-'}
        req = Request(testing.create_environ(headers=headers))
        self.assertRaises(falcon.HTTPBadRequest, lambda: req.range)

        headers = {'Range': '-3-4'}
        req = Request(testing.create_environ(headers=headers))
        self.assertRaises(falcon.HTTPBadRequest, lambda: req.range)

        headers = {'Range': '3-3-4'}
        req = Request(testing.create_environ(headers=headers))
        self.assertRaises(falcon.HTTPBadRequest, lambda: req.range)

        headers = {'Range': '3-3-'}
        req = Request(testing.create_environ(headers=headers))
        self.assertRaises(falcon.HTTPBadRequest, lambda: req.range)

        headers = {'Range': '3-3- '}
        req = Request(testing.create_environ(headers=headers))
        self.assertRaises(falcon.HTTPBadRequest, lambda: req.range)

        headers = {'Range': 'fizbit'}
        req = Request(testing.create_environ(headers=headers))
        self.assertRaises(falcon.HTTPBadRequest, lambda: req.range)

        headers = {'Range': 'a-'}
        req = Request(testing.create_environ(headers=headers))
        self.assertRaises(falcon.HTTPBadRequest, lambda: req.range)

        headers = {'Range': 'a-3'}
        req = Request(testing.create_environ(headers=headers))
        self.assertRaises(falcon.HTTPBadRequest, lambda: req.range)

        headers = {'Range': '-b'}
        req = Request(testing.create_environ(headers=headers))
        self.assertRaises(falcon.HTTPBadRequest, lambda: req.range)

        headers = {'Range': '3-b'}
        req = Request(testing.create_environ(headers=headers))
        self.assertRaises(falcon.HTTPBadRequest, lambda: req.range)

        headers = {'Range': 'x-y'}
        req = Request(testing.create_environ(headers=headers))
        self.assertRaises(falcon.HTTPBadRequest, lambda: req.range)

        headers = {'Range': 'bytes=0-0,-1'}
        req = Request(testing.create_environ(headers=headers))
        self.assertRaises(falcon.HTTPBadRequest, lambda: req.range)

    def test_missing_attribute_header(self):
        req = Request(testing.create_environ())
        self.assertEquals(req.range, None)

        req = Request(testing.create_environ())
        self.assertEquals(req.content_length, None)

    def test_content_length(self):
        headers = {'content-length': '5656'}
        req = Request(testing.create_environ(headers=headers))
        self.assertEquals(req.content_length, 5656)

        headers = {'content-length': ''}
        req = Request(testing.create_environ(headers=headers))
        self.assertEquals(req.content_length, None)

    def test_bogus_content_length_nan(self):
        headers = {'content-length': 'fuzzy-bunnies'}
        req = Request(testing.create_environ(headers=headers))
        self.assertRaises(falcon.HTTPBadRequest, lambda: req.content_length)

    def test_bogus_content_length_neg(self):
        headers = {'content-length': '-1'}
        req = Request(testing.create_environ(headers=headers))
        self.assertRaises(falcon.HTTPBadRequest, lambda: req.content_length)

    def test_date(self):
        date = datetime.datetime(2013, 4, 4, 5, 19, 18)
        headers = {'date': 'Thu, 04 Apr 2013 05:19:18 GMT'}
        req = Request(testing.create_environ(headers=headers))
        self.assertEquals(req.date, date)

    def test_date_invalid(self):
        headers = {'date': 'Thu, 04 Apr 2013'}
        req = Request(testing.create_environ(headers=headers))
        self.assertRaises(falcon.HTTPBadRequest, lambda: req.date)

    def test_attribute_headers(self):
        date = testing.httpnow()
        hash = 'fa0d1a60ef6616bb28038515c8ea4cb2'
        auth = 'HMAC_SHA1 c590afa9bb59191ffab30f223791e82d3fd3e3af'
        agent = 'curl/7.24.0 (x86_64-apple-darwin12.0)'

        self._test_attribute_header('Accept', 'x-falcon', 'accept')

        self._test_attribute_header('Authorization', auth, 'auth')

        self._test_attribute_header('Content-Type', 'text/plain',
                                    'content_type')
        self._test_attribute_header('Expect', '100-continue', 'expect')

        self._test_attribute_header('If-Match', hash, 'if_match')
        self._test_attribute_header('If-Modified-Since', date,
                                    'if_modified_since')
        self._test_attribute_header('If-None-Match', hash, 'if_none_match')
        self._test_attribute_header('If-Range', hash, 'if_range')
        self._test_attribute_header('If-Unmodified-Since', date,
                                    'if_unmodified_since')

        self._test_attribute_header('User-Agent', agent, 'user_agent')

    def test_method(self):
        self.assertEquals(self.req.method, 'GET')

        self.req = Request(testing.create_environ(path='', method='HEAD'))
        self.assertEquals(self.req.method, 'HEAD')

    def test_empty_path(self):
        self.req = Request(testing.create_environ(path=''))
        self.assertEquals(self.req.path, '/')

    def test_content_type_method(self):
        self.assertEquals(self.req.get_header('content-type'), 'text/plain')

    def test_content_length_method(self):
        self.assertEquals(self.req.get_header('content-length'), '4829')

    # -------------------------------------------------------------------------
    # Helpers
    # -------------------------------------------------------------------------

    def _test_attribute_header(self, name, value, attr):
        headers = {name: value}
        req = Request(testing.create_environ(headers=headers))
        self.assertEquals(getattr(req, attr), value)

        headers = {name: None}
        req = Request(testing.create_environ(headers=headers))
        self.assertEqual(getattr(req, attr), None)
