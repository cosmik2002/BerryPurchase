import subprocess

subprocess.run(r"scrapy runspider MarketParser\MarketParser\spiders\market.py")
# from scrapy.crawler import CrawlerProcess
# from scrapy.utils.project import get_project_settings
# from twisted.internet import reactor
#
# from app.MarketParser.MarketParser.spiders.market import MarketSpider
#
# # process = CrawlerProcess(get_project_settings())
#
# process = CrawlerProcess({
#     'USER_AGENT': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)'
# })
#
# d = process.crawl(MarketSpider)
# d.addBoth(lambda _: reactor.stop())
# process.start() # the script will block here until the crawling is finished