from PySide6.QtWidgets import QHeaderView,  QStyleOptionButton,QStyle
from PySide6.QtCore import QRect


#Checkbox implementation in header section
class ChannHeader(QHeaderView):
    def __init__(self, orientation, parent=None):
        super(ChannHeader, self).__init__(orientation, parent)
        self.isOn = True

    def paintSection(self, painter, rect, logicalIndex):
        painter.save()
        super(ChannHeader, self).paintSection(painter, rect, logicalIndex)
        painter.restore()
        if logicalIndex == 0:
            option = QStyleOptionButton()
            option.rect = QRect(11, 11, 11, 11)
            option.state = QStyle.State_On if self.isOn else QStyle.State_Off
            self.style().drawPrimitive(QStyle.PE_IndicatorCheckBox, option, painter)
            #self.style().drawPrimitive(QStyle.PE_IndicatorItemViewItemCheck, option, painter)

    def mousePressEvent(self, event):
        self.isOn = not self.isOn
        
        self.update
        
        super(ChannHeader, self).mousePressEvent(event)
       
      
    