import scrapy


class MarketSpider(scrapy.Spider):
    name = "market"
    allowed_domains = ["market.urbanfood.ru"]
    start_urls = ["https://market.urbanfood.ru"]

    def parse(self, response, **kwargs):
        products = response.css('li.product.type-product')
        for product in products:
            name = product.css('h2.woocommerce-loop-product__title::text').get()
            price = float(product.css('span.price bdi::text').get().replace(" ", ""))
            url = product.css('a::attr(href)').get()
            img = product.css('img::attr(src)').get()
            yield {
                'name': name,
                'price': price,
                'url': url,
                'image': img,
            }
        categories = response.css('li.product-category.product a::attr(href)').getall()
        # if not categories:
        #     return
        # self.log(response.urljoin(categories[0]))
        # yield scrapy.Request(response.urljoin(categories[0]), callback=self.parse)
        for link in categories:
            cat = response.urljoin(link)
            yield scrapy.Request(cat, callback=self.parse)
