"""RobotShop UK Collector — robot parts pricing.

UK/EU source for robot components: actuators, servos, grippers, controllers.
"""

import json
import re
import time
import requests
from .base import BaseCollector, CollectorResult
from shared.persist import insert_source_record

# Robot parts to track
ROBOT_CATEGORIES = {
    'actuators': ['servo motor', 'brushless motor', 'stepper motor', 'linear actuator'],
    'controllers': ['arduino', 'raspberry pi', 'esp32', 'jetson', 'stm32'],
    'sensors': ['lidar', 'depth camera', 'imu', 'encoder', 'force sensor'],
    'grippers': ['robot gripper', 'robotic hand', 'end effector'],
    'power': ['lipo battery', 'bms', 'motor driver', 'esc'],
    'mechanical': ['bearing', 'coupling', 'gearbox', 'linear rail'],
}

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
}


class RobotShopCollector(BaseCollector):
    SOURCE_ID = 'robotshop_uk'
    DATASET = 'robot_parts'
    PARSER_ID = 'robotshop_web_v1'

    def fetch(self):
        """Scrape RobotShop UK for robot parts."""
        all_items = []
        for category, queries in ROBOT_CATEGORIES.items():
            for query in queries:
                items = self._search_robotshop(query, category)
                all_items.extend(items)
                time.sleep(2)
        return json.dumps(all_items).encode()

    def _search_robotshop(self, query, category):
        """Search RobotShop UK."""
        try:
            url = f'https://uk.robotshop.com/search?q={query}'
            resp = self._fetch_url(url, timeout=15)
            if resp and resp.status_code == 200:
                html = resp.text
                # Extract product data from HTML
                items = []
                # RobotShop uses Shopify-style JSON-LD
                json_ld = re.findall(r'<script type="application/ld\+json">(.*?)</script>', html, re.DOTALL)
                for block in json_ld:
                    try:
                        data = json.loads(block)
                        if isinstance(data, dict) and data.get('@type') == 'Product':
                            offers = data.get('offers', {})
                            items.append({
                                'name': data.get('name', ''),
                                'price': offers.get('price', 0),
                                'currency': offers.get('priceCurrency', 'GBP'),
                                'availability': offers.get('availability', ''),
                                'brand': data.get('brand', {}).get('name', ''),
                                'category': category,
                            })
                    except:
                        pass
                return items
        except Exception as e:
            print(f'    RobotShop error for {query}: {e}')
        return []

    def parse(self, raw_content, raw_hash):
        result = CollectorResult()
        items = json.loads(raw_content)
        for item in items:
            native_id = f"{item.get('name', '')}_{item.get('price', 0)}"
            normalized = {
                'source_native_id': native_id,
                'name': item.get('name', ''),
                'price': item.get('price', 0),
                'currency': item.get('currency', 'GBP'),
                'availability': item.get('availability', ''),
                'brand': item.get('brand', ''),
                'category': item.get('category', ''),
            }
            ir = insert_source_record(
                self.SOURCE_ID, self.DATASET, native_id,
                normalized, raw_hash, self.PARSER_ID, self.PARSER_VERSION
            )
            if ir.inserted:
                result.records_new += 1
            else:
                result.records_unchanged += 1
        return result


if __name__ == '__main__':
    RobotShopCollector().run()
