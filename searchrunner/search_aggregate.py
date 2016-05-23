from tornado import gen, ioloop, web, queues
from tornado.httpclient import AsyncHTTPClient
import json
import datetime
import heapq


URLS = ['http://localhost:9000/scrapers/expedia', 'http://localhost:9000/scrapers/orbitz', 'http://localhost:9000/scrapers/priceline', 'http://localhost:9000/scrapers/travelocity', 'http://localhost:9000/scrapers/united']

class SearchApiHandler(web.RequestHandler):

    @gen.coroutine
    def get(self, page=None):
        http_client = AsyncHTTPClient()
        if not page:
            page = 1
        else:
            page = int(page)
        listings = []
        itemsPerListing = 25
        responses = yield [http_client.fetch(url, self.handle_request) for url in URLS]
        for response in responses:
            json_resp = json.loads(response.body)
            listings.append(map(lambda x: (x['agony'], x), json_resp['results'][25*(page-1):25+25*(page-1)]))

        merged = map(lambda x: x[1], heapq.merge(*listings))

        self.write({
            "results": merged,
        })

        self.finish()

    def handle_request(self, response):
        if response.error:
            self.set_status(400)
            self.write({
            "Error:", response.error
            })


ROUTES = [
    (r"/flights/search/(?P<page>\w+)", SearchApiHandler),
    (r"/flights/search", SearchApiHandler)
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
