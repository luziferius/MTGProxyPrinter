"""Read-only, offline view of the canonical Siser workflow guide."""

from pathlib import Path

from PySide6.QtCore import QUrl
from PySide6.QtGui import QImage
from PySide6.QtWidgets import QDialog, QDialogButtonBox, QTextBrowser, QVBoxLayout, QWidget

from mtg_proxy_printer.ui import common


GUIDE_PATH = 'help/siser-print-cut.md'
PREVIEW_PATH = 'help/images/a4-portrait-feed.png'


class SiserGuideDialog(QDialog):
    def __init__(self, parent: QWidget | None = None):
        # Attach only after resources load, so a failed construction leaves no
        # empty, parent-owned guide behind on repeated help requests.
        super().__init__()
        self.setWindowTitle(self.tr('Siser Print & Cut Guide'))
        self.setModal(False)
        self.resize(800, 700)
        self.browser = QTextBrowser(self)
        self.browser.setReadOnly(True)
        self.browser.setOpenLinks(False)
        self.close_buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Close, self)
        self.close_buttons.rejected.connect(self.reject)
        layout = QVBoxLayout(self)
        layout.addWidget(self.browser)
        layout.addWidget(self.close_buttons)

        markdown = common.load_file(GUIDE_PATH)
        if not markdown:
            raise RuntimeError(self.tr('Siser guide unavailable: cannot read {path}.').format(path=GUIDE_PATH))
        try:
            text = markdown.decode('utf-8')
        except UnicodeDecodeError as error:
            raise RuntimeError(self.tr('Siser guide unavailable: invalid UTF-8 text.')) from error
        image = QImage()
        if not image.loadFromData(common.load_file(PREVIEW_PATH)):
            raise RuntimeError(self.tr('Siser guide unavailable: cannot read preview {path}.').format(path=PREVIEW_PATH))

        if common.HAS_COMPILED_RESOURCES:
            base_url = QUrl('qrc:/help/')
        else:
            base_url = QUrl.fromLocalFile(str(Path(common.RESOURCE_PATH_PREFIX) / 'help') + '/')
        self.browser.document().setBaseUrl(base_url)
        self.browser.setMarkdown(text)
        self.setParent(parent, self.windowFlags())
