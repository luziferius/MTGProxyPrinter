"""Reference-backed frame resolution and supported ordinary-output validation."""

import math
from PySide6.QtCore import QCoreApplication

from mtg_proxy_printer.model.page_geometry import PageGeometry
from mtg_proxy_printer.registration_profile_ids import RegistrationProfileId
from mtg_proxy_printer.siser_page_marks import SiserPageMarks, build_siser_page_marks

# Observed Leonardo 1.1.31 frames; not a universal paper conversion or correction.
_REFERENCE_FRAMES = (
    ((215.9, 279.4), (215.9, 279.4)),
    ((297.0, 210.0), (296.96832909999995, 209.97333756666666)),
)


def resolve_siser_page_marks(geometry: PageGeometry) -> SiserPageMarks:
    dimensions = (geometry.sheet_width_mm, geometry.sheet_height_mm)
    for nominal, frame in _REFERENCE_FRAMES:
        if all(math.isclose(actual, expected, abs_tol=1e-6, rel_tol=0)
               for actual, expected in zip(dimensions, nominal)):
            return build_siser_page_marks(*frame)
    raise ValueError(f'Siser Page Marks does not support {dimensions[0]:g} × {dimensions[1]:g} mm. '
                     'Supported configurations: Letter portrait (215.9 × 279.4 mm) '
                     'and A4 landscape (297 × 210 mm), including equivalent custom sheets.')


def require_artwork_output_supported(registration_style: str, geometry: PageGeometry) -> None:
    """Validate the explicit frame, without clearance assessment or global state."""
    if registration_style == RegistrationProfileId.SISER.value:
        try:
            resolve_siser_page_marks(geometry)
        except ValueError as error:
            raise RuntimeError(QCoreApplication.translate('SiserRegistration',
                'Artwork output unavailable: {reason}').format(reason=error)) from error
