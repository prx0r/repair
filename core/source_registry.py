"""Source Registry — metadata about every data source.

Every source must declare:
- what it provides
- how often it updates
- whether it can be reconstructed
- its licence
- its current health
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone, timedelta
from typing import Optional


@dataclass
class SourceMetadata:
    """Metadata about a data source."""
    id: str
    name: str
    owner: str
    access_method: str
    licence: str
    update_frequency: str
    reliability: str  # very_high, high, medium, low
    recoverability: str  # canonical, ephemeral, partial, third_party
    max_age_hours: int
    url: str = ""
    schema_version: str = "1.0"

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "owner": self.owner,
            "url": self.url,
            "access_method": self.access_method,
            "licence": self.licence,
            "update_frequency": self.update_frequency,
            "reliability": self.reliability,
            "schema_version": self.schema_version,
            "recoverability": self.recoverability,
            "max_age_hours": self.max_age_hours,
        }


class SourceRegistry:
    """Registry of all data sources with freshness and reliability metadata."""

    def __init__(self):
        self._sources: dict[str, SourceMetadata] = {}
        self._load_defaults()

    def _load_defaults(self):
        """Load the built-in UKGraph sources."""
        defaults = [
            SourceMetadata(
                id="planning_data_api",
                name="Planning Data API",
                owner="MHCLG",
                access_method="REST API (no key)",
                url="https://www.planning.data.gov.uk",
                licence="OGL v3",
                update_frequency="varies by LPA",
                reliability="high",
                schema_version="1.0",
                recoverability="canonical",
                max_age_hours=168,  # 7 days
            ),
            SourceMetadata(
                id="contracts_finder",
                name="Contracts Finder",
                owner="Crown Commercial Service",
                access_method="REST API (no key)",
                url="https://www.contractsfinder.service.gov.uk",
                licence="OGL v3",
                update_frequency="daily",
                reliability="high",
                recoverability="canonical",
                max_age_hours=72,
            ),
            SourceMetadata(
                id="ebay_uk_sold",
                name="eBay UK Sold Listings",
                owner="eBay",
                access_method="Apify scraper or public search",
                licence="transformative use",
                update_frequency="daily",
                reliability="medium",
                recoverability="ephemeral",
                max_age_hours=48,
            ),
            SourceMetadata(
                id="ons_labour",
                name="ONS Labour Market Statistics",
                owner="Office for National Statistics",
                access_method="CSV download",
                url="https://www.ons.gov.uk",
                licence="OGL v3",
                update_frequency="monthly",
                reliability="very_high",
                recoverability="canonical",
                max_age_hours=720,  # 30 days
            ),
        ]
        for source in defaults:
            self._sources[source.id] = source

    def get_source(self, source_id: str) -> Optional[SourceMetadata]:
        """Look up a source by ID."""
        return self._sources.get(source_id)

    def check_freshness(self, source_id: str, last_collected_at: Optional[datetime] = None) -> dict:
        """Check if data from a source is stale.

        Returns a dict with:
        - source_id: the source identifier
        - max_age_hours: the freshness threshold
        - last_collected: when data was last collected (or None)
        - staleness_hours: hours since last collection (or None)
        - is_fresh: whether data is within the freshness window
        - status: "fresh", "stale", or "unknown"
        """
        source = self.get_source(source_id)
        if source is None:
            return {
                "source_id": source_id,
                "max_age_hours": None,
                "last_collected": None,
                "staleness_hours": None,
                "is_fresh": None,
                "status": "unknown",
            }

        if last_collected_at is None:
            return {
                "source_id": source_id,
                "max_age_hours": source.max_age_hours,
                "last_collected": None,
                "staleness_hours": None,
                "is_fresh": None,
                "status": "unknown",
            }

        now = datetime.now(timezone.utc)
        staleness = now - last_collected_at
        staleness_hours = staleness.total_seconds() / 3600
        is_fresh = staleness_hours <= source.max_age_hours

        return {
            "source_id": source_id,
            "max_age_hours": source.max_age_hours,
            "last_collected": last_collected_at.isoformat(),
            "staleness_hours": round(staleness_hours, 2),
            "is_fresh": is_fresh,
            "status": "fresh" if is_fresh else "stale",
        }

    def list_sources(self, garden: Optional[str] = None) -> list[SourceMetadata]:
        """List all registered sources.

        Args:
            garden: optional filter (currently all sources are garden-agnostic)
        """
        return list(self._sources.values())

    def register_source(self, source_dict: dict) -> SourceMetadata:
        """Add a new source to the registry.

        Args:
            source_dict: dict with keys matching SourceMetadata fields.
                         Required keys: id, name, owner, access_method, licence,
                         update_frequency, reliability, recoverability, max_age_hours.

        Returns:
            The registered SourceMetadata.
        """
        required_keys = {
            "id", "name", "owner", "access_method", "licence",
            "update_frequency", "reliability", "recoverability", "max_age_hours",
        }
        missing = required_keys - source_dict.keys()
        if missing:
            raise ValueError(f"Missing required keys: {missing}")

        source = SourceMetadata(
            id=source_dict["id"],
            name=source_dict["name"],
            owner=source_dict["owner"],
            access_method=source_dict["access_method"],
            licence=source_dict["licence"],
            update_frequency=source_dict["update_frequency"],
            reliability=source_dict["reliability"],
            recoverability=source_dict["recoverability"],
            max_age_hours=source_dict["max_age_hours"],
            url=source_dict.get("url", ""),
            schema_version=source_dict.get("schema_version", "1.0"),
        )
        self._sources[source.id] = source
        return source
