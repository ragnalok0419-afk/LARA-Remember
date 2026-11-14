import unittest
from unittest.mock import patch
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import server

class RoutingTest(unittest.TestCase):
    def test_unknown_city_refused(self):
        r=server.calculate_route('없는 도시','서울')
        self.assertFalse(r['ok'])
    def test_same_city_refused(self):
        r=server.calculate_route('서울','서울')
        self.assertFalse(r['ok'])
    def test_unsupported_station_type_refused(self):
        r=server.nearby_stations('서울','부산','wrong',160)
        self.assertFalse(r['ok'])
    def test_unknown_station_origin_refused(self):
        r=server.nearby_stations('미지원','부산','fuel',160)
        self.assertFalse(r['ok'])
    def test_offline_network_failure_does_not_fabricate_distance(self):
        # No live internet and no guessed route distance.
        server.ROUTE_CACHE.clear()
        with patch.object(server.urllib.request,'urlopen',side_effect=OSError('offline')):
            with self.assertRaises(OSError):
                server.calculate_route('서울','부산')
    def test_endpoint_failure_return_503(self):
        from http.server import ThreadingHTTPServer
        from threading import Thread
        from urllib.request import urlopen
        from urllib.error import HTTPError
        with patch.object(server,'calculate_route',side_effect=OSError('offline')):
            httpd=ThreadingHTTPServer(('127.0.0.1',0),server.Handler)
            thread=Thread(target=httpd.serve_forever,daemon=True);thread.start()
            try:
                with self.assertRaises(HTTPError) as ctx:
                    urlopen(f'http://127.0.0.1:{httpd.server_port}/route?origin=%EC%84%9C%EC%9A%B8&destination=%EB%B6%80%EC%82%B0')
                self.assertEqual(ctx.exception.code,503)
                self.assertIn('임의 거리',ctx.exception.read().decode())
            finally:
                httpd.shutdown();httpd.server_close();thread.join(timeout=2)
if __name__=='__main__':unittest.main()
