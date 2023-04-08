# Copyright (C) 2020-2023 Thomas Hess <thomas.hess@udo.edu>


# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

import abc
import configparser
import functools
import typing

from PyQt5.QtCore import QUrl
from PyQt5.QtGui import QDesktopServices
from PyQt5.QtWidgets import QGroupBox, QWidget, QCheckBox, QPushButton

try:
    from mtg_proxy_printer.ui.generated.settings_window.format_printing_filter import Ui_card_download_format_settings as Ui_FormatPrintingFilter
    from mtg_proxy_printer.ui.generated.settings_window.general_printing_filter import Ui_Form as Ui_GeneralPrintingFilter
except ModuleNotFoundError:
    from mtg_proxy_printer.ui.common import load_ui_from_file
    Ui_FormatPrintingFilter = load_ui_from_file("settings_window/format_printing_filter")
    Ui_GeneralPrintingFilter = load_ui_from_file("settings_window/general_printing_filter")

UiTypes = typing.Union[typing.Type[Ui_FormatPrintingFilter], typing.Type[Ui_GeneralPrintingFilter]]


class AbstractPrintingFilterWidget(QGroupBox):

    def __init__(self, ui_class: UiTypes, parent: QWidget = None):
        super(AbstractPrintingFilterWidget, self).__init__(parent)
        self.ui = ui_class()
        self.ui.setupUi(self)

    def load_settings(self, settings: configparser.SectionProxy):
        for widget, key in self._get_widgets_with_keys():
            widget.setChecked(settings.getboolean(key))

    def save_settings(self, settings: configparser.SectionProxy):
        for widget, key in self._get_widgets_with_keys():
            settings[key] = str(widget.isChecked())

    @staticmethod
    def view_query_on_scryfall(query: str):
        query_url = QUrl("https://scryfall.com/search", QUrl.StrictMode)
        query_url.setQuery(f"q={query}", QUrl.StrictMode)
        QDesktopServices.openUrl(query_url)

    @abc.abstractmethod
    def _get_widgets_with_keys(self) -> typing.List[typing.Tuple[QCheckBox, str]]:
        pass


class GeneralPrintingFilterWidget(AbstractPrintingFilterWidget):
    def __init__(self, parent: QWidget = None):
        super().__init__(Ui_GeneralPrintingFilter, parent)
        ui = self.ui
        ui.view_cards_depicting_racism.clicked.connect(
            lambda: self.view_query_on_scryfall("function:banned-due-to-racist-imagery"))
        ui.view_oversized_cards.clicked.connect(lambda: self.view_query_on_scryfall("is:oversized"))
        ui.view_white_bordered_cards.clicked.connect(lambda: self.view_query_on_scryfall("border:white"))
        ui.view_gold_bordered_cards.clicked.connect(lambda: self.view_query_on_scryfall("border:gold"))
        ui.view_funny_cards.clicked.connect(lambda: self.view_query_on_scryfall("is:funny"))
        ui.view_token.clicked.connect(lambda: self.view_query_on_scryfall("is:token"))
        ui.view_digital_cards.clicked.connect(lambda: self.view_query_on_scryfall("is:digital"))

    def _get_widgets_with_keys(self) -> typing.List[typing.Tuple[QCheckBox, str]]:
        ui = self.ui
        widgets_with_settings: typing.List[typing.Tuple[QCheckBox, str]] = [
            (ui.hide_cards_depicting_racism, "hide-cards-depicting-racism"),
            (ui.hide_cards_without_images, "hide-cards-without-images"),
            (ui.hide_oversized_cards, "hide-oversized-cards"),
            (ui.hide_white_bordered_cards, "hide-white-bordered"),
            (ui.hide_gold_bordered_cards, "hide-gold-bordered"),
            (ui.hide_funny_cards, "hide-funny-cards"),
            (ui.hide_token, "hide-token"),
            (ui.hide_digital_cards, "hide-digital-cards"),
        ]
        return widgets_with_settings


class FormatPrintingFilterWidget(AbstractPrintingFilterWidget):

    def __init__(self, parent: QWidget = None):
        super().__init__(Ui_FormatPrintingFilter, parent)
        ui = self.ui
        for _, key in self._get_widgets_with_keys():
            format_name = key.split("-")[-1]
            button: QPushButton = getattr(ui, f"view_banned_in_{format_name}")
            button.clicked.connect(
                functools.partial(self.view_query_on_scryfall, f"banned:{format_name}")
            )

    def _get_widgets_with_keys(self) -> typing.List[typing.Tuple[QCheckBox, str]]:
        ui = self.ui
        widgets_with_settings: typing.List[typing.Tuple[QCheckBox, str]] = [
            (ui.hide_banned_in_brawl, "hide-banned-in-brawl"),
            (ui.hide_banned_in_commander, "hide-banned-in-commander"),
            (ui.hide_banned_in_historic, "hide-banned-in-historic"),
            (ui.hide_banned_in_legacy, "hide-banned-in-legacy"),
            (ui.hide_banned_in_modern, "hide-banned-in-modern"),
            (ui.hide_banned_in_pauper, "hide-banned-in-pauper"),
            (ui.hide_banned_in_penny, "hide-banned-in-penny"),
            (ui.hide_banned_in_pioneer, "hide-banned-in-pioneer"),
            (ui.hide_banned_in_standard, "hide-banned-in-standard"),
            (ui.hide_banned_in_vintage, "hide-banned-in-vintage"),
        ]
        return widgets_with_settings
