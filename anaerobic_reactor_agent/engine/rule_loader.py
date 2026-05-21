"""YAML rule file loading and validation."""

import logging
from pathlib import Path
from typing import List, Optional

import yaml

from ..models.rules import FaultRule
from ..utils.exceptions import ConfigurationError
from ..config.settings import PARAMETER_THRESHOLDS_FILE, FAULT_RULES_FILE, RECOMMENDATIONS_FILE

logger = logging.getLogger(__name__)


class RuleLoader:
    """Loads and caches rule configurations from YAML files."""

    def __init__(self, rules_dir: Optional[Path] = None):
        if rules_dir:
            self.thresholds_file = rules_dir / "parameter_thresholds.yaml"
            self.rules_file = rules_dir / "fault_rules.yaml"
            self.recommendations_file = rules_dir / "recommendations.yaml"
        else:
            self.thresholds_file = PARAMETER_THRESHOLDS_FILE
            self.rules_file = FAULT_RULES_FILE
            self.recommendations_file = RECOMMENDATIONS_FILE

        self._thresholds: Optional[dict] = None
        self._rules: Optional[List[FaultRule]] = None
        self._recommendations: Optional[dict] = None

    @property
    def thresholds(self) -> dict:
        if self._thresholds is None:
            self._thresholds = self._load_yaml(self.thresholds_file)
        return self._thresholds

    @property
    def rules(self) -> List[FaultRule]:
        if self._rules is None:
            raw = self._load_yaml(self.rules_file)
            self._rules = self._parse_rules(raw)
        return self._rules

    @property
    def recommendations(self) -> dict:
        if self._recommendations is None:
            self._recommendations = self._load_yaml(self.recommendations_file)
        return self._recommendations

    def _load_yaml(self, path: Path) -> dict:
        if not path.exists():
            raise ConfigurationError(f"Configuration file not found: {path}")
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)
            logger.debug("Loaded YAML: %s", path)
            return data
        except yaml.YAMLError as e:
            raise ConfigurationError(f"Invalid YAML in {path}: {e}") from e

    def _parse_rules(self, raw: dict) -> List[FaultRule]:
        rules_data = raw.get("rules", [])
        rules = []
        for r in rules_data:
            try:
                rules.append(FaultRule(**r))
            except Exception as e:
                logger.warning("Skipping invalid rule '%s': %s", r.get("name", "?"), e)
        logger.info("Loaded %d fault rules", len(rules))
        return sorted(rules, key=lambda r: r.priority)

    def get_threshold_for(self, param_name: str) -> Optional[dict]:
        return self.thresholds.get("parameters", {}).get(param_name)

    def reload(self):
        """Clear caches and reload all YAML files."""
        self._thresholds = None
        self._rules = None
        self._recommendations = None
        logger.info("Rule configuration reloaded")
