import sys
from pathlib import Path

import pytest

BACKEND = Path(__file__).resolve().parents[1]
if str(BACKEND) not in sys.path:
    sys.path.insert(0, str(BACKEND))

from src.geometry import kernel as kernel_module  # noqa: E402


def _has_cadquery() -> bool:
    try:
        import cadquery  # noqa: F401
        return True
    except ImportError:
        return False


HAS_CADQUERY = _has_cadquery()


@pytest.fixture(autouse=True)
def preview_kernel():
    """Fast unit tests run on the preview kernel; e2e tests switch kernels explicitly."""
    kernel_module.set_kernel('preview')
    yield
    kernel_module.set_kernel('preview')


@pytest.fixture(params=['preview', 'cadquery'])
def any_kernel(request):
    if request.param == 'cadquery' and not HAS_CADQUERY:
        pytest.skip('cadquery is not installed (conda install -c conda-forge cadquery)')
    kernel_module.set_kernel(request.param)
    return request.param
