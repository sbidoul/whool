import logging
from pathlib import Path
from typing import List

from manifestoo_core.exceptions import ManifestooException
from manifestoo_core.metadata import POST_VERSION_STRATEGY_NONE, metadata_from_addon_dir

_logger = logging.getLogger(__name__)


def dependencies_for_addon_dir(addon_dir: Path) -> List[str]:
    try:
        # TODO load options from pyproject.toml
        metadata = metadata_from_addon_dir(
            addon_dir,
            options={"post_version_strategy_override": POST_VERSION_STRATEGY_NONE},
        )
    except ManifestooException as e:
        _logger.debug("Could not load metadata for %s: %s", addon_dir, e)
        return []
    else:
        return metadata.get_all("Requires-Dist")
