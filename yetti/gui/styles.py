"""
Стили для GUI в стиле глассморфизма
"""

MAIN_STYLE = """
QMainWindow {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                              stop:0 #1a1b26, stop:1 #24283b);
}

QWidget {
    color: #c0caf5;
    font-family: 'Segoe UI', Arial;
}

QPushButton {
    background-color: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                                    stop:0 rgba(86, 95, 137, 0.5),
                                    stop:1 rgba(100, 110, 160, 0.5));
    border: 1px solid rgba(86, 95, 137, 0.8);
    border-radius: 10px;
    padding: 10px 20px;
    color: #c0caf5;
    font-size: 14px;
    font-weight: 500;
}

QPushButton:hover {
    background-color: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                                    stop:0 rgba(86, 95, 137, 0.7),
                                    stop:1 rgba(100, 110, 160, 0.7));
    border: 1px solid rgba(122, 162, 247, 0.8);
}

QPushButton:pressed {
    background-color: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                                    stop:0 rgba(86, 95, 137, 0.9),
                                    stop:1 rgba(100, 110, 160, 0.9));
    padding: 11px 19px 9px 21px;
}

QTableWidget {
    background-color: rgba(26, 27, 38, 0.7);
    border: 1px solid rgba(86, 95, 137, 0.3);
    border-radius: 15px;
    gridline-color: rgba(86, 95, 137, 0.2);
    padding: 5px;
}

QTableWidget::item {
    padding: 10px;
    border-radius: 8px;
    margin: 2px;
}

QTableWidget::item:selected {
    background-color: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                                    stop:0 rgba(86, 95, 137, 0.5),
                                    stop:1 rgba(100, 110, 160, 0.5));
    border: 1px solid rgba(122, 162, 247, 0.5);
}

QHeaderView::section {
    background-color: rgba(36, 40, 59, 0.8);
    padding: 12px 8px;
    border: none;
    color: #7aa2f7;
    font-weight: bold;
    font-size: 13px;
    border-radius: 8px;
    margin: 2px;
}

QProgressBar {
    border: none;
    border-radius: 8px;
    background-color: rgba(26, 27, 38, 0.7);
    text-align: center;
    color: #c0caf5;
    font-size: 12px;
    font-weight: bold;
    height: 20px;
}

QProgressBar::chunk {
    background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                    stop:0 #7aa2f7,
                                    stop:1 #89b4ff);
    border-radius: 8px;
}

QLabel {
    color: #c0caf5;
    font-size: 14px;
}

QLineEdit {
    background-color: rgba(26, 27, 38, 0.7);
    border: 1px solid rgba(86, 95, 137, 0.3);
    border-radius: 10px;
    padding: 8px 12px;
    color: #c0caf5;
    font-size: 14px;
    selection-background-color: rgba(122, 162, 247, 0.3);
}

QLineEdit:focus {
    border: 1px solid #7aa2f7;
    background-color: rgba(26, 27, 38, 0.8);
}

QLineEdit:hover {
    border: 1px solid rgba(122, 162, 247, 0.5);
}

QComboBox {
    background-color: rgba(26, 27, 38, 0.7);
    border: 1px solid rgba(86, 95, 137, 0.3);
    border-radius: 10px;
    padding: 8px 12px;
    color: #c0caf5;
    font-size: 14px;
    min-width: 100px;
}

QComboBox:hover {
    border: 1px solid rgba(122, 162, 247, 0.5);
}

QComboBox:focus {
    border: 1px solid #7aa2f7;
}

QComboBox::drop-down {
    border: none;
    width: 30px;
}

QComboBox::down-arrow {
    image: url(down_arrow.png);
    width: 16px;
    height: 16px;
}

QSpinBox {
    background-color: rgba(26, 27, 38, 0.7);
    border: 1px solid rgba(86, 95, 137, 0.3);
    border-radius: 10px;
    padding: 8px 12px;
    color: #c0caf5;
    font-size: 14px;
    min-width: 80px;
}

QSpinBox:hover {
    border: 1px solid rgba(122, 162, 247, 0.5);
}

QSpinBox:focus {
    border: 1px solid #7aa2f7;
}

QMenu {
    background-color: rgba(26, 27, 38, 0.95);
    border: 1px solid rgba(86, 95, 137, 0.3);
    border-radius: 12px;
    padding: 8px;
}

QMenu::item {
    padding: 12px 30px;
    border-radius: 8px;
}

QMenu::item:selected {
    background-color: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                                    stop:0 rgba(86, 95, 137, 0.5),
                                    stop:1 rgba(100, 110, 160, 0.5));
}

QScrollBar:vertical {
    border: none;
    background-color: rgba(26, 27, 38, 0.7);
    width: 12px;
    margin: 0px;
    border-radius: 6px;
}

QScrollBar::handle:vertical {
    background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                    stop:0 rgba(86, 95, 137, 0.5),
                                    stop:1 rgba(100, 110, 160, 0.5));
    border-radius: 6px;
    min-height: 30px;
}

QScrollBar::handle:vertical:hover {
    background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                    stop:0 rgba(86, 95, 137, 0.7),
                                    stop:1 rgba(100, 110, 160, 0.7));
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}

QScrollBar:horizontal {
    border: none;
    background-color: rgba(26, 27, 38, 0.7);
    height: 12px;
    margin: 0px;
    border-radius: 6px;
}

QScrollBar::handle:horizontal {
    background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                    stop:0 rgba(86, 95, 137, 0.5),
                                    stop:1 rgba(100, 110, 160, 0.5));
    border-radius: 6px;
    min-width: 30px;
}

QScrollBar::handle:horizontal:hover {
    background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                    stop:0 rgba(86, 95, 137, 0.7),
                                    stop:1 rgba(100, 110, 160, 0.7));
}

QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
    width: 0px;
}

QWidget[objectName="dialogWindow"] {
    background-color: rgba(26, 27, 38, 0.95);
    border: 1px solid rgba(86, 95, 137, 0.3);
    border-radius: 15px;
}

QWidget[objectName="dialogWindow"] QPushButton {
    min-width: 100px;
}
"""

CARD_STYLE = """
QWidget[objectName="card"] {
    background-color: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                                    stop:0 rgba(36, 40, 59, 0.7),
                                    stop:1 rgba(46, 50, 69, 0.7));
    border: 1px solid rgba(86, 95, 137, 0.3);
    border-radius: 20px;
    padding: 20px;
}

QWidget[objectName="card"]:hover {
    background-color: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                                    stop:0 rgba(36, 40, 59, 0.8),
                                    stop:1 rgba(46, 50, 69, 0.8));
    border: 1px solid rgba(122, 162, 247, 0.3);
}

QWidget[objectName="card"] QLabel {
    background: transparent;
}
""" 