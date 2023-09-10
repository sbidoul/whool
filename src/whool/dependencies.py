import logging
from pathlib import Path
from typing import List

from manifestoo_core.exceptions import ManifestooException
from manifestoo_core.metadata import POST_VERSION_STRATEGY_NONE, metadata_from_addon_dir

from .utils import load_pyproject_toml

_logger = logging.getLogger(__name__)


def dependencies_for_addon_dir(addon_dir: Path) -> List[str]:
    try:
        options = load_pyproject_toml(addon_dir).get("tool", {}).get("whool", {})
        options["post_version_strategy_override"] = POST_VERSION_STRATEGY_NONE
        metadata = metadata_from_addon_dir(addon_dir, options=options)
    except ManifestooException as e:
        _logger.debug("Could not load metadata for %s: %s", addon_dir, e)
        return []
    else:
        return metadata.get_all("Requires-Dist") or []
