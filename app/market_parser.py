import json
import os
import subprocess
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import List, Dict

import scrapy
from scrapy.crawler import CrawlerProcess
from config import Config

# Config.SQLALCHEMY_DATABASE_URI_NO_FLASK = 'sqlite:///../clients.sqb'

from app.models import Goods, Settings, Prices
from database import SessionLocal


# @dataclass
# class Market:
#     name: str
#     price: float
class MarketLoader:
    def __init__(self):
        self.session = None

    def load(self, cwd=r'app\MarketParser'):
        file_name = "markt.json"
        # cwd = r'app\MarketParser'
        full_file_name = os.path.join(cwd, file_name)
        if Path(full_file_name).exists():
            os.remove(full_file_name)
        process = subprocess.run(r"scrapy runspider MarketParser\spiders\market.py", cwd=cwd)
        if process.returncode != 0:
            return {'res': process.stdout or '' + process.stderr or ''}
        self.session = SessionLocal
        self.session.query(Goods).update({'active': 0})
        self.session.commit()
        with open(full_file_name, 'r', encoding='utf-8') as f:
            market = json.load(f)
            for good in market:
                db_good = self.session.query(Goods).filter(Goods.name == good['name']).all()
                if not db_good:
                    db_good = Goods(name=good['name'], price=good['price'], url=good['url'], image=good['image'],
                                    active=True)
                    self.session.add(db_good)
                    self.session.flush()
                    self.session.add(Prices(good_id=db_good.id, price=good['price']))
                    self.session.commit()
                else:
                    db_good = db_good[0]
                    if db_good.price != good['price']:
                        self.session.add(Prices(good_id=db_good.id, price=good['price']))
                    if db_good.price != good['price'] or db_good.url != good['url'] or db_good.image != good['image']:
                        db_good.price = good['price']
                        db_good.url = good['url']
                        db_good.image = good['image']
                    db_good.active = True
                    self.session.commit()
        self.update_setting(str(datetime.now()))

    def update_setting(self, setting):
        if not hasattr(self, "session"):
            return
        s = self.session.query(Settings).filter(Settings.name == Settings.MARKET_LOAD).all()
        if not s:
            s = Settings(name=Settings.MARKET_LOAD, value=setting)
            self.session.add(s)
            self.session.commit()
            return s
        else:
            s[0].value = setting
            self.session.commit()
            return s


if __name__ == "__main__":
    print(os.getcwd())
    MarketLoader().load()
