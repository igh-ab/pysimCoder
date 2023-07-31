try:
    from PyQt6.QtWidgets import (
        QApplication,
        QCheckBox,
        QComboBox,
        QDialog,
        QDialogButtonBox,
        QFileDialog,
        QGraphicsItem,
        QGraphicsPathItem,
        QGraphicsScene,
        QGraphicsTextItem,
        QGraphicsView,
        QGridLayout,
        QHBoxLayout,
        QLabel,
        QLineEdit,
        QListWidget,
        QMainWindow,
        QMenu,
        QMessageBox,
        QPushButton,
        QSpinBox,
        QTabWidget,
        QTextEdit,
        QVBoxLayout,
        QWidget
    )
    from PyQt6.QtGui import (
        QAction,
        QDrag,
        QFont,
        QIcon,
        QImage,
        QPainter,
        QPainterPath,
        QPen,
        QTransform
    )
    
    from PyQt6.QtCore import (
        QEvent,
        QFileInfo,
        QMimeData,
        QObject,
        QPointF,
        QRectF,
        QSettings,
        QSizeF,
        QT_VERSION_STR,
        QVariant,
        Qt
    )
    
    from PyQt6.QtPrintSupport import (
        QPrinter,
        QPrintDialog
    )
    
except:
    from PyQt5.QtWidgets import (
        QAction,
        QApplication,
        QCheckBox,
        QComboBox,
        QDialog,
        QDialogButtonBox,
        QFileDialog,
        QGraphicsItem,
        QGraphicsPathItem,
        QGraphicsScene,
        QGraphicsTextItem,
        QGraphicsView,
        QGridLayout,
        QHBoxLayout,
        QLabel,
        QLineEdit,
        QListWidget,
        QMainWindow,
        QMenu,
        QMessageBox,
        QPushButton,
        QSpinBox,
        QTabWidget,
        QTextEdit,
        QVBoxLayout,
        QWidget
    )
    from PyQt5.QtGui import (
        QDrag,
        QFont,
        QIcon,
        QImage,
        QPainter,
        QPainterPath,
        QPen,
        QTransform
    )
    
    from PyQt5.QtCore import (
        QEvent,
        QFileInfo,
        QMimeData,
        QObject,
        QPointF,
        QRectF,
        QSettings,
        QSizeF,
        QT_VERSION_STR,
        QVariant,
        Qt
    )
    
    from PyQt5.QtPrintSupport import (
        QPrinter,
        QPrintDialog
    )
    
print(QT_VERSION_STR)
