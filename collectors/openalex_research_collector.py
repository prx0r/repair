"""OpenAlex Research Collector — repair/sustainability/circular economy papers.

Fetches latest research that maps the repair knowledge frontier.
Layer 2: knowledge source, not core repair data.
"""

import json
import requests
from .base import BaseCollector, CollectorResult
from shared.persist import insert_source_record

QUERIES = [
    'electronics repair sustainability',
    'circular economy electronics',
    'right to repair',
    'component obsolescence',
    'product repairability',
    'refurbishment electronics',
    'e-waste recycling recovery',
    'spare parts availability',
    'modular design repair',
    'semiconductor supply chain',
    'gpu mining hardware lifecycle',
    'robot maintenance lifecycle',
]


class OpenAlexCollector(BaseCollector):
    SOURCE_ID = 'openalex'
    DATASET = 'research_papers'
    PARSER_ID = 'openalex_api_v1'

    def fetch(self):
        """Fetch papers from OpenAlex for all queries."""
        all_items = []
        for query in QUERIES:
            items = self._search_openalex(query)
            all_items.extend(items)
        return json.dumps(all_items).encode()

    def _search_openalex(self, query, per_page=10):
        """Search OpenAlex for a query."""
        try:
            url = f'https://api.openalex.org/works?search={query}&per_page={per_page}&sort=cited_by_count:desc'
            acq = self._fetch_url(url, timeout=15)
            if acq and acq.status == 200:
                return json.loads(acq.content).get('results', [])
        except Exception as e:
            print(f'    OpenAlex error for {query}: {e}')
        return []

    def parse(self, raw_content, raw_hash, result):
        """Parse OpenAlex papers. Mutates result."""
        items = json.loads(raw_content)
        for paper in items:
            native_id = paper.get('id', '')
            if not native_id:
                result.records_invalid += 1
                continue

            topics = [t.get('display_name', '') for t in paper.get('topics', [])[:5]]
            normalized = {
                'source_native_id': native_id,
                'title': paper.get('title', ''),
                'cited_by': paper.get('cited_by_count', 0),
                'year': paper.get('publication_year'),
                'topics': topics,
                'doi': paper.get('doi', ''),
            }

            ir = insert_source_record(
                self.SOURCE_ID, self.DATASET, native_id,
                normalized, raw_hash, self.PARSER_ID, self.PARSER_VERSION
            )
            if ir.inserted:
                if ir.duplicate_of:
                    result.records_changed += 1
                else:
                    result.records_new += 1
            else:
                result.records_unchanged += 1


if __name__ == '__main__':
    OpenAlexCollector().run()
