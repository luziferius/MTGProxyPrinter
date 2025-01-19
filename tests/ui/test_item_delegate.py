#  Copyright © 2020-2025.  Thomas Hess <thomas.hess@udo.edu>
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program. If not, see <http://www.gnu.org/licenses/>.


from collections import Counter
import itertools
from unittest.mock import NonCallableMagicMock

from PyQt5.QtWidgets import QComboBox
import pytest
from hamcrest import *

from mtg_proxy_printer.document_controller.card_actions import ActionAddCard
from mtg_proxy_printer.model.carddb import CardDatabase, Card, MTGSet
from mtg_proxy_printer.model.card_list import CardListModel
from mtg_proxy_printer.model.document import Document
from mtg_proxy_printer.model.imagedb import ImageDatabase
from mtg_proxy_printer.natsort import NaturallySortedSortFilterProxyModel
from mtg_proxy_printer.units_and_sizes import CardSizes

from mtg_proxy_printer.ui.item_delegates import ComboBoxItemDelegate


@pytest.fixture(params=itertools.product(range(3), ["", "language"]))
def card_list_empty_carddb(card_db: CardDatabase, request):
    proxy_level, language = request.param  # type: int, str
    card = Card("", MTGSet("", ""), "", language, "", True, "", "", True, CardSizes.REGULAR, 1, False, None)
    source_model = CardListModel(card_db)
    source_model.add_cards(Counter({card: 1}))
    # Having this list keeps the references alive. Without keeping them here, access in test code raises
    #   RuntimeError: wrapped C/C++ object of type NaturallySortedSortFilterProxyModel has been deleted
    models = [source_model]
    for _ in range(proxy_level):
        proxy = NaturallySortedSortFilterProxyModel()
        proxy.setSourceModel(models[-1])
        models.append(proxy)
    yield models[-1]


@pytest.fixture(params=["", "language"])
def document_empty_carddb(card_db: CardDatabase, request):
    card = Card("", MTGSet("", ""), "", request.param, "", True, "", "", True, CardSizes.REGULAR, 1, False, None)
    source_model = Document(card_db, NonCallableMagicMock(spec=ImageDatabase))
    ActionAddCard(card).apply(source_model)
    yield source_model


@pytest.mark.parametrize("column", CardListModel.EDITABLE_COLUMNS)
def test_setEditorData_on_card_list_empty_model(qtbot, card_db: CardDatabase, card_list_empty_carddb, column):
    editor_widget = QComboBox()
    delegate = ComboBoxItemDelegate()
    index = card_list_empty_carddb.index(0, column)
    delegate.setEditorData(editor_widget, index)
    assert_that(editor_widget.model().rowCount(), is_(1))  # Data from the source card must round-trip


@pytest.mark.parametrize("column", CardListModel.EDITABLE_COLUMNS)
def test_setEditorData_on_document_empty_model(qtbot, card_db: CardDatabase, document_empty_carddb, column):
    editor_widget = QComboBox()
    delegate = ComboBoxItemDelegate()
    page_index = document_empty_carddb.index(0, 0)
    index = document_empty_carddb.index(0, column, page_index)
    delegate.setEditorData(editor_widget, index)
    assert_that(editor_widget.model().rowCount(), is_(1))  # Data from the source card must round-trip
