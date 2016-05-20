from tornado import gen, ioloop, web
from tornado.httpclient import AsyncHTTPClient
import json

class SearchApiHandler(web.RequestHandler):

    @gen.coroutine
    def get(self):
        http_client = AsyncHTTPClient()
        all_listings = []
        sites = ['expedia', 'orbitz', 'priceline', 'travelocity', 'united']

        for i in range(0, 4):
            response = yield http_client.fetch("http://localhost:9000/scrapers/" + sites[i], self.handle_request)
            json_resp = json.loads(response.body)
            all_listings += json_resp['results']

        all_listings.sort(key=lambda x: (x['agony'])),

        self.write({
            "results": all_listings,
        })


    def handle_request(self, response):
        if response.error:
            self.set_status(400)
            self.write({
                "Error:", response.error
            })


ROUTES = [
    (r"/flights/search", SearchApiHandler),
]


def run():
    app = web.Application(
        ROUTES,
        debug=True,
    )

    app.listen(8000)
    print "Server (re)started. Listening on port 8000"

    ioloop.IOLoop.current().start()


if __name__ == "__main__":
    run()
