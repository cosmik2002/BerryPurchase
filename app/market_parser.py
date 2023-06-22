import json
from dataclasses import dataclass
from typing import List

from MarketParser.MarketParser.spiders import market
import scrapy
from scrapy.crawler import CrawlerProcess
from config import Config

Config.SQLALCHEMY_DATABASE_URI_NO_FLASK = 'sqlite:///../clients.sqb'

from app.models import Goods
from database import Session
# @dataclass
# class Market:
#     name: str
#     price: float

if __name__ == "__main__":
    file = r'MarketParser\m.json'
    session = Session()
    with open(file, 'r', encoding='utf-8') as f:
        # market: List[Market] \
        market = json.load(f)
        print (market)
        for good in market:
            db_good = session.query(Goods).filter(Goods.name==good['name']).all()
            if not db_good:
                session.add(Goods(name=good['name']))
                session.commit()



    exit(0)

    process = CrawlerProcess({
        'USER_AGENT': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)'
    })

    process.crawl(market.MarketSpider)
    process.start()  # the script will block here until the crawling is finished