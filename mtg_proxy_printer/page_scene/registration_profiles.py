"""Stateless registration rendering profiles over ready shared page geometry."""

from collections.abc import Sequence
from typing import Protocol

from PySide6.QtCore import QPointF, Qt
from PySide6.QtGui import QPen, QBrush
from PySide6.QtWidgets import QGraphicsItem, QGraphicsRectItem

from mtg_proxy_printer.model.page_geometry import PageGeometry
from mtg_proxy_printer.registration_profile_ids import RegistrationProfileId
from mtg_proxy_printer.page_scene.items import BullseyeMarkItem, CutMarkSquareItem, CutMarkAngleItem, RenderLayers
from mtg_proxy_printer.siser_registration import resolve_siser_page_marks
from mtg_proxy_printer.units_and_sizes import distance_to_px, unit_registry


class RegistrationProfile(Protocol):
    profile_id: RegistrationProfileId

    def create_items(self) -> list[QGraphicsItem]: ...

    def place_items(self, items: Sequence[QGraphicsItem], geometry: PageGeometry,
                    *, legacy_x_offset_px: int = 0) -> None: ...


def _place_three_corners(items: Sequence[QGraphicsItem], geometry: PageGeometry,
                         legacy_x_offset_px: int) -> None:
    frame = geometry.margin_frame_px
    positions = (
        QPointF(frame.x + legacy_x_offset_px, frame.y),
        QPointF(frame.right + legacy_x_offset_px, frame.y),
        QPointF(frame.x + legacy_x_offset_px, frame.bottom),
    )
    for item, position in zip(items, positions):
        item.setPos(position)


class _DisabledProfile:
    profile_id = RegistrationProfileId.NONE

    def create_items(self) -> list[QGraphicsItem]:
        return []

    def place_items(self, items: Sequence[QGraphicsItem], geometry: PageGeometry,
                    *, legacy_x_offset_px: int = 0) -> None:
        pass


class _BullseyeProfile:
    profile_id = RegistrationProfileId.BULLSEYE

    def create_items(self) -> list[QGraphicsItem]:
        return [BullseyeMarkItem(False, False), BullseyeMarkItem(True, False), BullseyeMarkItem(False, True)]

    def place_items(self, items: Sequence[QGraphicsItem], geometry: PageGeometry,
                    *, legacy_x_offset_px: int = 0) -> None:
        _place_three_corners(items, geometry, legacy_x_offset_px)


class _SilhouetteProfile:
    profile_id = RegistrationProfileId.SILHOUETTE

    def create_items(self) -> list[QGraphicsItem]:
        return [CutMarkSquareItem(), CutMarkAngleItem(False), CutMarkAngleItem(True)]

    def place_items(self, items: Sequence[QGraphicsItem], geometry: PageGeometry,
                    *, legacy_x_offset_px: int = 0) -> None:
        _place_three_corners(items, geometry, legacy_x_offset_px)


class _SiserProfile:
    profile_id = RegistrationProfileId.SISER

    def create_items(self) -> list[QGraphicsItem]:
        items = [QGraphicsRectItem() for _ in range(8)]
        for item in items:
            item.setPen(QPen(Qt.PenStyle.NoPen))
            item.setBrush(QBrush(Qt.GlobalColor.black))
            item.setZValue(RenderLayers.CUT_LINES_BELOW.value)
        return items

    def place_items(self, items: Sequence[QGraphicsItem], geometry: PageGeometry,
                    *, legacy_x_offset_px: int = 0) -> None:
        if legacy_x_offset_px != 0:
            raise ValueError('Siser Page Marks does not support a legacy horizontal offset')
        marks = resolve_siser_page_marks(geometry)
        if len(items) != len(marks.bars):
            raise ValueError('Siser Page Marks requires eight registration roots')
        for item, bar in zip(items, marks.bars):
            r = bar.bounds_mm
            x, y, width, height = (distance_to_px(v * unit_registry.mm)
                                    for v in (r.x, r.y, r.width, r.height))
            item.setRect(0, 0, width, height)
            item.setPos(QPointF(x, y))


_PROFILES: dict[str, RegistrationProfile] = {
    profile.profile_id.value: profile
    for profile in (_DisabledProfile(), _BullseyeProfile(), _SilhouetteProfile(), _SiserProfile())
}


def get_registration_profile(style: str) -> RegistrationProfile:
    return _PROFILES.get(style, _PROFILES[RegistrationProfileId.NONE.value])
