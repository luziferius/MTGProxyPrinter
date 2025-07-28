#  Copyright © 2020-2025  Thomas Hess <thomas.hess@udo.edu>
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


from unittest.mock import patch, DEFAULT

import pytest
from hamcrest import *

from mtg_proxy_printer.argument_parser import Namespace
import mtg_proxy_printer.__main__


@pytest.fixture
def main_mocks():
    with patch("mtg_proxy_printer.__main__.mtg_proxy_printer.logger.configure_root_logger") as configure_root_logger, \
            patch.multiple(
            "mtg_proxy_printer.__main__",
            _app=DEFAULT, Application=DEFAULT, truststore=DEFAULT,
            parse_args=DEFAULT, QTimer=DEFAULT, logger=DEFAULT) as mocks:
        mocks["configure_root_logger"] = configure_root_logger
        yield mocks
    mocks.clear()


def test_main_calls_inject_into_ssl(main_mocks):
    mtg_proxy_printer.__main__.main()
    main_mocks["truststore"].inject_into_ssl.assert_called_once()


def test_main_parses_command_line_arguments(main_mocks):
    mtg_proxy_printer.__main__.main()
    main_mocks["parse_args"].assert_called_once()


@patch("sys.argv")
def test_main_creates_application_instance_with_parsed_arguments(argv, main_mocks):
    parsed_args = main_mocks["parse_args"]()
    mtg_proxy_printer.__main__.main()
    main_mocks["Application"].assert_called_once_with(parsed_args, argv)


def test_main_puts_application_instance_in_global_scope(main_mocks):
    mtg_proxy_printer.__main__.main()
    app = main_mocks["Application"]()
    assert_that(mtg_proxy_printer.__main__._app, is_(same_instance(app)))


def test_main_configures_logger(main_mocks):
    mtg_proxy_printer.__main__.main()
    main_mocks["configure_root_logger"].assert_called_once()


def test_main_calls_exec_on_application_instance(main_mocks):
    mtg_proxy_printer.__main__.main()
    main_mocks["Application"]().exec.assert_called_once()


def test_enqueues_startup_tasks_on_regular_launch(main_mocks):
    main_mocks["parse_args"].return_value = Namespace(test_exit_on_launch=False)
    mtg_proxy_printer.__main__.main()
    app = main_mocks["Application"]()
    app.enqueue_startup_tasks.assert_called_once()
    main_mocks["QTimer"].singleShot.assert_not_called()


def test_skips_enqueuing_startup_tasks_on_launch_requesting_immediate_exit(main_mocks):
    main_mocks["parse_args"].return_value = Namespace(test_exit_on_launch=True)
    mtg_proxy_printer.__main__.main()
    app = main_mocks["Application"]()
    app.enqueue_startup_tasks.assert_not_called()
    main_mocks["QTimer"].singleShot.assert_called_with(0, app.main_window.on_action_quit_triggered)
