from PySide6.QtCore import (Qt,QRect, Slot, Signal,QSettings)
from PySide6.QtGui import (QFont,QBrush,QColor)
import pyqtgraph as pg


class Cursor(pg.InfiniteLine):
    def __init__(self, *args, **kwargs):

        super().__init__(
            *args, label="{value:.4f}s", labelOpts={"position": 0.04}, **kwargs
        )

        self.addMarker("^", 0)
        self.addMarker("v", 1)

        self._settings = QSettings()
        if self._settings.value("plot_background") == "White":
            self.label.setColor(QColor(0, 59, 126))
        else:
            self.label.setColor(QColor("#ffffff"))

        self.label.show()

    def set_value(self, value):
        self.setPos(value)
