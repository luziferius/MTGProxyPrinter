#  Copyright © 2020-2026  Thomas Hess <thomas.hess@udo.edu>
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

from hamcrest import *

from mtg_proxy_printer.async_tasks.printing_filter_updater import PrintingPreferenceUpdater
from mtg_proxy_printer.model.carddb import CardDatabase
from tests.helpers import fill_card_database_with_json_cards


def test_update_only_updates_relevant_printing_preferences(card_db: CardDatabase):
    fill_card_database_with_json_cards(None, card_db, [
        "universes_beyond_card",
        "spanish_basic_Forest",
        "english_basic_Forest",
        "textless_card",
        "universes_beyond_textless_card",
    ])
    db = card_db.db
    weights = {
        ("hide-universes-beyond-cards", 5), ("hide-low-resolution-cards", -5), ("hide-textless-cards", -7),
        ("hide-full-art-cards", 1)
    }
    printing_preference_updater = PrintingPreferenceUpdater(card_db, weights, db)
    printing_preference_updater.run()
    db.row_factory = None
    assert_that(
        db.execute("SELECT scryfall_id, preference_score FROM AllPrintings ORDER BY scryfall_id ASC"),
        contains_exactly(
            ("1381ec47-55fd-47d9-aded-d21776bc06b9", -1),  # universes_beyond_textless_card
            ("7ef83f4c-d3ff-4905-a16d-f2bae673a5b2", 1),  # english_basic_Forest (is full-art)
            ("815261f8-daaa-4d76-86d9-d2801eb3f1f7", 5),  # universes_beyond_card
            ("9ad231e2-f401-4670-b9ec-0d0aa7ea9bae", -6),  # textless_card
            ("ffa13d4c-6c5e-44bd-859e-38e79d47a916", -4),  # spanish_basic_Forest (is low resolution)
        )
    )


