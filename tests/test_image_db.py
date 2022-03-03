# Copyright (C) 2022 Thomas Hess <thomas.hess@udo.edu>

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

from pathlib import Path
from tempfile import TemporaryDirectory

from hamcrest import *
import pytest

from mtg_proxy_printer.model.imagedb import ImageDatabase


@pytest.fixture()
def image_db():
    with TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        image_db = ImageDatabase(temp_path)
        yield image_db


def test_quit_background_thread(image_db: ImageDatabase):
    image_db.quit_background_thread()
    assert_that(image_db.download_thread.isRunning(), is_(False))
