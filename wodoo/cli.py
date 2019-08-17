from .buildapi import _make_dist_info, _prepare_package_metadata


def _get_purelib():
    import sysconfig

    return sysconfig.get_paths()["purelib"]


def develop():
    metadata = _prepare_package_metadata(".")
    _make_dist_info(_get_purelib(), metadata)


def main():
    pass
