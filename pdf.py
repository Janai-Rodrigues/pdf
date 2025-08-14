# -*- coding: utf-8 -*-
# #############################################################################
#
#   QuantumPDF v8.9 - Centralização Perfeita do Preview de Impressão
#   Autor: Gemini
#   Data: 14/08/2025
#
#   Recursos Principais (v8.9):
#   - Preview de Impressão Sempre Centralizado: A miniatura na janela de
#     impressão agora permanece perfeitamente centralizada em todas as
#     situações, seja ao abrir a janela ou ao alternar entre as orientações.
#
# #############################################################################

import sys
import os
import logging
import traceback
from typing import Dict, Optional, List

# Importações do PyQt6
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QToolBar, QStatusBar, QFileDialog, QDialog, QListWidget,
    QListWidgetItem, QSizePolicy, QTabWidget, QSpinBox,
    QCheckBox, QComboBox, QMessageBox, QGridLayout, QGroupBox, QDialogButtonBox,
    QLineEdit, QRadioButton, QGraphicsView, QGraphicsScene,
    QGraphicsPixmapItem, QGraphicsRectItem, QFrame, QStackedWidget
)
from PyQt6.QtGui import (
    QIcon, QPixmap, QImage, QPainter, QPen, QColor,
    QCursor, QBrush, QAction, QIntValidator, QPageLayout, QTransform, QActionGroup,
    QFont, QShortcut, QKeySequence
)
from PyQt6.QtCore import (
    Qt, QSize, QRectF, QPoint, QTimer, QThread, pyqtSignal, QByteArray,
    QSettings, QPropertyAnimation, QEasingCurve, QEvent, QPointF
)
from PyQt6.QtSvg import QSvgRenderer
from PyQt6.QtPrintSupport import QPrinter, QPrintDialog, QPrinterInfo
from PyQt6.QtNetwork import QLocalServer, QLocalSocket

# Importação da biblioteca para manipulação de PDF
import fitz  # PyMuPDF

# #############################################################################
# SEÇÃO 0: CONFIGURAÇÃO DE LOG
# #############################################################################
logging.basicConfig(
    level=logging.INFO, # Mude para DEBUG para ver mais detalhes
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s (%(filename)s:%(lineno)d)",
    stream=sys.stdout,
)
logger = logging.getLogger("QuantumPDF")

def handle_exception(exc_type, exc_value, exc_traceback):
    """Loga exceções não tratadas antes de o programa fechar."""
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return
    logger.critical("Exceção não tratada encontrada:", exc_info=(exc_type, exc_value, exc_traceback))
    QMessageBox.critical(
        None,
        "Erro Crítico",
        f"Ocorreu um erro inesperado e o QuantumPDF precisa ser fechado.\n\n"
        f"Detalhes do Erro:\n{exc_value}\n\n"
        f"Por favor, verifique o log no terminal para mais informações."
    )

sys.excepthook = handle_exception


# #############################################################################
# SEÇÃO 1: GERENCIADOR DE ÍCONES E CONFIGURAÇÕES
# #############################################################################

class IconManager:
    """Gerencia a criação de ícones SVG com cores dinâmicas."""
    _instance = None
    _icon_cache: Dict[str, QIcon] = {}
    _svg_data = {
        "open": """<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14.5 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7.5L14.5 2z"></path><polyline points="14 2 14 8 20 8"></polyline></svg>""",
        "print": """<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="6 9 6 2 18 2 18 9"></polyline><path d="M6 18H4a2 2 0 0 1-2-2v-5a2 2 0 0 1 2-2h16a2 2 0 0 1 2 2v5a2 2 0 0 1-2 2h-2"></path><rect x="6" y="14" width="12" height="8"></rect></svg>""",
        "zoom-in": """<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="8"></circle><line x1="21" y1="21" x2="16.65" y2="16.65"></line><line x1="11" y1="8" x2="11" y2="14"></line><line x1="8" y1="11" x2="14" y2="11"></line></svg>""",
        "zoom-out": """<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="8"></circle><line x1="21" y1="21" x2="16.65" y2="16.65"></line><line x1="8" y1="11" x2="14" y2="11"></line></svg>""",
        "fit-width": """<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="15 3 21 3 21 9"></polyline><polyline points="9 21 3 21 3 15"></polyline><line x1="21" y1="3" x2="14" y2="10"></line><line x1="3" y1="21" x2="10" y2="14"></line></svg>""",
        "fit-page": """<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="9 3 3 3 3 9"></polyline><polyline points="15 21 21 21 21 15"></polyline><line x1="3" y1="3" x2="10" y2="10"></line><line x1="21" y1="21" x2="14" y2="14"></line></svg>""",
        "search": """<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="8"></circle><line x1="21" y1="21" x2="16.65" y2="16.65"></line></svg>""",
        "arrow-up": """<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="12" y1="19" x2="12" y2="5"></line><polyline points="5 12 12 5 19 12"></polyline></svg>""",
        "arrow-down": """<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="12" y1="5" x2="12" y2="19"></line><polyline points="19 12 12 19 5 12"></polyline></svg>""",
        "rotate-right": """<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="23 4 23 10 17 10"></polyline><path d="M20.49 15a9 9 0 1 1-2.12-9.36L23 10"></path></svg>""",
        "rotate-left": """<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="1 4 1 10 7 10"></polyline><path d="M3.51 15a9 9 0 1 0 2.13-9.36L1 10"></path></svg>""",
        "select": """<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 3l7 18 2.5-7.5L19 12l-16-9z"></path></svg>""",
        "hand": """<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M18 11V6a2 2 0 0 0-2-2v0a2 2 0 0 0-2 2v0"></path><path d="M14 10V4a2 2 0 0 0-2-2v0a2 2 0 0 0-2 2v2"></path><path d="M10 10.5V6a2 2 0 0 0-2-2v0a2 2 0 0 0-2 2v8"></path><path d="M18 8a2 2 0 1 1 4 0v6a8 8 0 0 1-8 8h-2c-2.8 0-4.5-1.8-4-4l1.4-1.4"></path></svg>""",
        "close": """<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="6" x2="6" y2="18"></line><line x1="6" y1="6" x2="18" y2="18"></line></svg>""",
        "minimize": """<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="5" y1="12" x2="19" y2="12"></line></svg>""",
        "maximize": """<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M8 3H5a2 2 0 0 0-2 2v3m18 0V5a2 2 0 0 0-2-2h-3m0 18h3a2 2 0 0 0 2-2v-3M3 16v3a2 2 0 0 0 2 2h3"></path></svg>""",
        "restore": """<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="4 14 10 14 10 20"></polyline><polyline points="20 10 14 10 14 4"></polyline><line x1="14" y1="10" x2="21" y2="3"></line><line x1="3" y1="21" x2="10" y2="14"></line></svg>""",
        "welcome_file": """<svg xmlns="http://www.w3.org/2000/svg" width="96" height="96" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1" stroke-linecap="round" stroke-linejoin="round"><path d="M14.5 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7.5L14.5 2z"></path><polyline points="14 2 14 8 20 8"></polyline><line x1="12" y1="18" x2="12" y2="12"></line><line x1="9" y1="15" x2="15" y2="15"></line></svg>"""
    }

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(IconManager, cls).__new__(cls)
        return cls._instance

    def get_icon(self, name: str, color: str = "#000000") -> QIcon:
        cache_key = f"{name}_{color}"
        if cache_key in self._icon_cache:
            return self._icon_cache[cache_key]
        svg_string = self._svg_data.get(name)
        if not svg_string:
            logger.warning(f"Ícone '{name}' não encontrado no IconManager.")
            return QIcon()
        colored_svg = svg_string.replace('stroke="currentColor"', f'stroke="{color}"')
        svg_bytes = QByteArray(colored_svg.encode('utf-8'))
        renderer = QSvgRenderer(svg_bytes)
        pixmap = QPixmap(renderer.defaultSize())
        pixmap.fill(Qt.GlobalColor.transparent)
        painter = QPainter(pixmap)
        renderer.render(painter)
        painter.end()
        icon = QIcon(pixmap)
        self._icon_cache[cache_key] = icon
        return icon

# #############################################################################
# SEÇÃO 2: WIDGETS PERSONALIZADOS E THREADS
# #############################################################################

class WelcomeScreen(QWidget):
    """Tela de boas-vindas exibida quando nenhum arquivo está aberto."""
    clicked = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("welcomeScreen")
        self.setCursor(Qt.CursorShape.PointingHandCursor)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(20)

        icon_manager = IconManager()
        icon_label = QLabel()
        icon_pixmap = icon_manager.get_icon("welcome_file", "#B0BEC5").pixmap(QSize(96, 96))
        icon_label.setPixmap(icon_pixmap)
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        title_label = QLabel("QuantumPDF")
        title_label.setObjectName("welcomeTitle")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        subtitle_label = QLabel("Nenhum arquivo aberto")
        subtitle_label.setObjectName("welcomeSubtitle")
        subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        instruction_label = QLabel("Clique em qualquer lugar para abrir um arquivo ou arraste um PDF aqui.")
        instruction_label.setObjectName("welcomeInstruction")
        instruction_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout.addWidget(icon_label)
        layout.addWidget(title_label)
        layout.addWidget(subtitle_label)
        layout.addWidget(instruction_label)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit()
        super().mousePressEvent(event)

class PDFGraphicsView(QGraphicsView):
    """View que exibe a cena do PDF."""
    zoom_requested_by_wheel = pyqtSignal(float)
    text_selected = pyqtSignal(QRectF)
    page_scroll_requested = pyqtSignal(int)  # +1 para próxima página, -1 para anterior

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("PDFGraphicsView")
        self._scene = QGraphicsScene(self)
        self.setScene(self._scene)
        self.setRenderHints(QPainter.RenderHint.Antialiasing | QPainter.RenderHint.SmoothPixmapTransform)
        self.setTransformationAnchor(QGraphicsView.ViewportAnchor.NoAnchor)
        self.setResizeAnchor(QGraphicsView.ViewportAnchor.NoAnchor)

        self._pixmap_item: Optional[QGraphicsPixmapItem] = None
        self._selection_rect_item: Optional[QGraphicsRectItem] = None
        self._selection_start_pos: Optional[QPointF] = None

        self.set_interaction_mode('select')

    def set_page_pixmap(self, pixmap: QPixmap):
        self.setTransform(QTransform())
        self._scene.clear()
        if pixmap and not pixmap.isNull():
            self._pixmap_item = self._scene.addPixmap(pixmap)
            self.setSceneRect(QRectF(pixmap.rect()))
        else:
            self._pixmap_item = None

    def set_interaction_mode(self, mode: str):
        if mode == 'select':
            self.setDragMode(QGraphicsView.DragMode.NoDrag)
            self.setCursor(Qt.CursorShape.IBeamCursor)
        else:
            self.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
            self.setCursor(Qt.CursorShape.OpenHandCursor)

    def wheelEvent(self, event):
        if event.modifiers() == Qt.KeyboardModifier.ControlModifier:
            angle = event.angleDelta().y()
            factor = 1.15 if angle > 0 else 1 / 1.15
            self.zoom_requested_by_wheel.emit(factor)
            event.accept()
            return

        v_bar = self.verticalScrollBar()
        is_at_top = v_bar.value() == v_bar.minimum()
        is_at_bottom = v_bar.value() == v_bar.maximum()

        scroll_delta = event.angleDelta().y()

        if scroll_delta > 0 and is_at_top:
            self.page_scroll_requested.emit(-1)
            event.accept()
        elif scroll_delta < 0 and is_at_bottom:
            self.page_scroll_requested.emit(1)
            event.accept()
        else:
            super().wheelEvent(event)


    def mousePressEvent(self, event):
        if self.dragMode() == QGraphicsView.DragMode.NoDrag and event.button() == Qt.MouseButton.LeftButton:
            self._selection_start_pos = self.mapToScene(event.pos())
            if self._selection_rect_item:
                self._scene.removeItem(self._selection_rect_item)
            pen = QPen(QColor(0, 120, 215, 150), 1, Qt.PenStyle.SolidLine)
            brush = QBrush(QColor(0, 120, 215, 40))
            self._selection_rect_item = self._scene.addRect(QRectF(), pen, brush)
            self._selection_rect_item.setZValue(10)
        elif self.dragMode() == QGraphicsView.DragMode.ScrollHandDrag:
             self.setCursor(Qt.CursorShape.ClosedHandCursor)
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self.dragMode() == QGraphicsView.DragMode.NoDrag and self._selection_start_pos:
            end_pos = self.mapToScene(event.pos())
            rect = QRectF(self._selection_start_pos, end_pos).normalized()
            self._selection_rect_item.setRect(rect)
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if self.dragMode() == QGraphicsView.DragMode.NoDrag and self._selection_start_pos and self._selection_rect_item:
            scene_rect = self._selection_rect_item.rect()
            self._scene.removeItem(self._selection_rect_item)
            self._selection_rect_item = None
            self._selection_start_pos = None
            if scene_rect.width() > 2 and scene_rect.height() > 2:
                 self.text_selected.emit(scene_rect)
        elif self.dragMode() == QGraphicsView.DragMode.ScrollHandDrag:
            self.setCursor(Qt.CursorShape.OpenHandCursor)
        super().mouseReleaseEvent(event)

class PageRenderThread(QThread):
    """Renderiza uma página de PDF com uma escala específica em segundo plano."""
    page_ready = pyqtSignal(QPixmap, float)

    def __init__(self, page, rotation, scale, parent=None):
        super().__init__(parent)
        self.page = page
        self.rotation = rotation
        self.scale = scale

    def run(self):
        try:
            mat = fitz.Matrix(self.scale, self.scale).prerotate(self.rotation)
            pix = self.page.get_pixmap(matrix=mat, alpha=False, colorspace=fitz.csRGB)
            image = QImage(pix.samples, pix.width, pix.height, pix.stride, QImage.Format.Format_RGB888)
            pixmap = QPixmap.fromImage(image)
            if not self.isInterruptionRequested():
                self.page_ready.emit(pixmap, self.scale)
        except Exception:
            logger.exception(f"Erro ao renderizar página {self.page.number if self.page else 'desconhecida'}")

class ThumbnailListWidget(QListWidget):
    """Widget para exibir miniaturas das páginas do PDF."""
    page_selected = pyqtSignal(int)
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("ThumbnailListWidget")
        self.setViewMode(QListWidget.ViewMode.ListMode)
        self.setFlow(QListWidget.Flow.TopToBottom)
        self.setWrapping(False)
        self.setResizeMode(QListWidget.ResizeMode.Adjust)
        self.setMovement(QListWidget.Movement.Static)
        self.setSpacing(10)
        self.itemClicked.connect(self._on_item_clicked)
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.setUniformItemSizes(False)
        self.setIconSize(QSize(140, 220))

    def _on_item_clicked(self, item: QListWidgetItem):
        page_num = self.row(item)
        self.page_selected.emit(page_num)

class ThumbnailLoaderThread(QThread):
    """Carrega as miniaturas em segundo plano."""
    thumbnail_ready = pyqtSignal(int, QPixmap, bool)
    def __init__(self, doc, rotation, parent=None):
        super().__init__(parent)
        self.doc = doc
        self.rotation = rotation

    def run(self):
        logger.debug(f"Iniciando ThumbnailLoaderThread para {len(self.doc)} páginas com rotação {self.rotation} graus.")
        for i in range(len(self.doc)):
            if self.isInterruptionRequested():
                logger.debug("ThumbnailLoaderThread interrompida.")
                return
            try:
                page = self.doc.load_page(i)
                mat = fitz.Matrix(0.5, 0.5).prerotate(self.rotation)
                pix = page.get_pixmap(matrix=mat, alpha=False)
                is_landscape = pix.width > pix.height
                image = QImage(pix.samples, pix.width, pix.height, pix.stride, QImage.Format.Format_RGB888)
                self.thumbnail_ready.emit(i, QPixmap.fromImage(image), is_landscape)
            except Exception:
                logger.exception(f"Erro ao carregar miniatura da página {i}")
        logger.debug("ThumbnailLoaderThread finalizada com sucesso.")

# #############################################################################
# SEÇÃO 3: O WIDGET PRINCIPAL DO VISUALIZADOR DE PDF
# #############################################################################

class PDFViewer(QWidget):
    """Widget que contém apenas a view do PDF. Controles são externos."""
    page_changed = pyqtSignal()
    zoom_changed = pyqtSignal(float)
    copied_to_clipboard = pyqtSignal(str)
    search_results_updated = pyqtSignal(int, int)
    rotation_changed = pyqtSignal()

    def __init__(self, file_path: str, parent=None):
        super().__init__(parent)
        self.file_path = file_path
        self.doc: Optional[fitz.Document] = None
        self.current_page_index = 0
        self.rotation = 0
        self.base_scale = 1.0
        self.current_zoom_factor = 1.0
        self.current_render_scale = 1.0
        self.page_render_thread: Optional[PageRenderThread] = None
        self.thumbnail_loader: Optional[ThumbnailLoaderThread] = None
        self.search_results = []
        self.current_search_index = -1
        self.scroll_to_bottom_on_load = False

        try:
            logger.info(f"Tentando abrir o arquivo: {file_path}")
            self.doc = fitz.open(file_path)
            self.raw_thumbnail_pixmaps: List[Optional[QPixmap]] = [None] * self.page_count()
            self.thumbnail_orientations: List[bool] = [False] * self.page_count()
            logger.info(f"Arquivo '{os.path.basename(file_path)}' aberto com sucesso. Páginas: {len(self.doc)}")
        except Exception:
            logger.critical(f"Falha CRÍTICA ao abrir o arquivo PDF: {file_path}", exc_info=True)
            QMessageBox.critical(self, "Erro ao Abrir Arquivo", f"Não foi possível abrir o arquivo:\n{file_path}\n\nPode estar corrompido ou não ser um PDF válido.")
            return

        self._init_ui()

    def _init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0,0,0,0)

        self.view = PDFGraphicsView()
        self.view.zoom_requested_by_wheel.connect(self._handle_wheel_zoom)
        self.view.text_selected.connect(self._on_text_selected)
        self.view.page_scroll_requested.connect(self._handle_page_scroll)

        main_layout.addWidget(self.view)

        self._render_timer = QTimer(self)
        self._render_timer.setSingleShot(True)
        self._render_timer.setInterval(150)
        self._render_timer.timeout.connect(self._render_page)

        self.set_interaction_mode('select')

    def display_page(self, page_num: int):
        if not self.doc or not (0 <= page_num < self.page_count()): return

        if self.current_page_index != page_num:
            logger.debug(f"Exibindo página {page_num} do arquivo '{os.path.basename(self.file_path)}'")
            self.current_page_index = page_num
            self._request_render(immediate=True)
            self.page_changed.emit()
        else:
            self.fit_to_page()

    def _request_render(self, immediate=False):
        if immediate:
            self._render_timer.stop()
            self._render_page()
        else:
            self._render_timer.start()

    def _render_page(self):
        if not self.doc or not self.view.viewport(): return

        if self.page_render_thread and self.page_render_thread.isRunning():
            self.page_render_thread.requestInterruption()
            self.page_render_thread.wait()

        page = self.doc.load_page(self.current_page_index)

        final_scale = self.base_scale * self.current_zoom_factor
        logger.debug(f"Iniciando renderização da página {self.current_page_index} com escala final {final_scale:.2f}")

        self.page_render_thread = PageRenderThread(page, self.rotation, final_scale)
        self.page_render_thread.page_ready.connect(self._on_page_ready)
        self.page_render_thread.start()

    def _on_page_ready(self, pixmap: QPixmap, scale: float):
        logger.debug(f"Renderização da página {self.current_page_index} concluída com escala {scale:.2f}.")
        self.current_render_scale = scale
        self.view.set_page_pixmap(pixmap)

        if self.scroll_to_bottom_on_load:
            QTimer.singleShot(0, lambda: self.view.verticalScrollBar().setValue(self.view.verticalScrollBar().maximum()))
            self.scroll_to_bottom_on_load = False
        else:
            QTimer.singleShot(0, lambda: self.view.verticalScrollBar().setValue(0))

        self._update_highlights()

    def set_zoom_factor(self, factor: float):
        new_factor = max(0.1, min(factor, 15.0))
        if abs(new_factor - self.current_zoom_factor) > 0.01:
            self.current_zoom_factor = new_factor
            logger.debug(f"Fator de zoom alterado para {self.current_zoom_factor:.2f}")
            self.zoom_changed.emit(self.current_zoom_factor)
            self._request_render()

    def rotate(self, angle: int):
        self.rotation = (self.rotation + angle) % 360
        logger.info(f"Rotação global do documento alterada para {self.rotation} graus.")
        self._recalculate_base_scale_and_render()
        self.rotation_changed.emit()

    def _on_text_selected(self, scene_rect: QRectF):
        if not self.doc: return

        try:
            pdf_rect = fitz.Rect(
                scene_rect.x() / self.current_render_scale,
                scene_rect.y() / self.current_render_scale,
                scene_rect.right() / self.current_render_scale,
                scene_rect.bottom() / self.current_render_scale
            )
        except ZeroDivisionError:
            logger.warning("Tentativa de seleção de texto com escala de renderização zero.")
            return

        page = self.doc.load_page(self.current_page_index)
        if self.rotation != 0:
            pdf_rect = pdf_rect.transform(fitz.Matrix(1, 1).prerotate(-self.rotation))

        selected_text = page.get_text("text", clip=pdf_rect, sort=True)
        if selected_text:
            logger.info(f"Texto selecionado e copiado: '{selected_text[:30].strip()}...'")
            QApplication.clipboard().setText(selected_text.strip())
            self.copied_to_clipboard.emit("✓ Texto copiado para a área de transferência")
        else:
            logger.debug("Seleção de área sem texto extraível.")

    def _handle_page_scroll(self, direction: int):
        """Muda de página quando o usuário rola o mouse até o limite."""
        if direction > 0 and self.current_page_index < self.page_count() - 1:
            self.display_page(self.current_page_index + 1)
        elif direction < 0 and self.current_page_index > 0:
            self.scroll_to_bottom_on_load = True
            self.display_page(self.current_page_index - 1)


    def page_count(self) -> int:
        return len(self.doc) if self.doc else 0

    def _handle_wheel_zoom(self, factor):
        self.set_zoom_factor(self.current_zoom_factor * factor)

    def zoom_in(self):
        self.set_zoom_factor(self.current_zoom_factor * 1.25)

    def zoom_out(self):
        self.set_zoom_factor(self.current_zoom_factor / 1.25)

    def _recalculate_base_scale_and_render(self):
        if not self.doc or not self.view.viewport(): return
        page = self.doc.load_page(self.current_page_index)
        if page.rect.is_empty: return

        page_rect = page.rect.transform(fitz.Matrix(1,1).prerotate(self.rotation))
        view_size = self.view.viewport().size()

        if page_rect.width == 0 or page_rect.height == 0: return

        scale_x = view_size.width() / page_rect.width
        scale_y = view_size.height() / page_rect.height

        self.base_scale = min(scale_x, scale_y)
        self._request_render()

    def fit_to_page(self):
        logger.debug("Ajustando zoom para página inteira.")
        self.current_zoom_factor = 1.0
        self.zoom_changed.emit(self.current_zoom_factor)
        self._recalculate_base_scale_and_render()

    def fit_to_width(self):
        if not self.doc or not self.view.viewport(): return
        page = self.doc.load_page(self.current_page_index)
        if page.rect.is_empty: return

        page_rect = page.rect.transform(fitz.Matrix(1,1).prerotate(self.rotation))
        view_width = self.view.viewport().width()

        if page_rect.width == 0: return

        scale_for_width = view_width / page_rect.width
        new_zoom_factor = scale_for_width / self.base_scale

        logger.debug(f"Ajustando para largura. Novo fator de zoom: {new_zoom_factor:.2f}")
        self.set_zoom_factor(new_zoom_factor)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._recalculate_base_scale_and_render()

    def set_interaction_mode(self, mode: str):
        logger.debug(f"Alterando modo de interação para: {mode}")
        self.view.set_interaction_mode(mode)

    def search_text(self, text: str):
        self.search_results = []
        self.current_search_index = -1
        if not text:
            self._update_highlights()
            self.search_results_updated.emit(0, 0)
            return

        logger.info(f"Buscando por '{text}' no documento.")
        for i in range(self.page_count()):
            page = self.doc.load_page(i)
            rects = page.search_for(text)
            for rect in rects:
                self.search_results.append((i, rect))

        logger.info(f"Busca concluída. {len(self.search_results)} resultados encontrados.")
        if self.search_results:
            self.current_search_index = 0
            self.go_to_result(0)

        self.search_results_updated.emit(self.current_search_index + 1 if self.search_results else 0, len(self.search_results))

    def go_to_result(self, index: int):
        if not (0 <= index < len(self.search_results)): return

        self.current_search_index = index
        page_num, rect = self.search_results[index]
        logger.debug(f"Navegando para resultado {index+1}/{len(self.search_results)} na página {page_num}.")

        if page_num != self.current_page_index:
            self.display_page(page_num)
        else:
            self._update_highlights()

        self.search_results_updated.emit(self.current_search_index + 1, len(self.search_results))

    def _update_highlights(self):
        for item in self.view.scene().items():
            if isinstance(item, QGraphicsRectItem) and item is not self.view._selection_rect_item:
                self.view.scene().removeItem(item)

        if not self.search_results or self.current_search_index < 0: return

        current_page_of_search, _ = self.search_results[self.current_search_index]
        if current_page_of_search != self.current_page_index: return

        for i, (p_num, rect) in enumerate(self.search_results):
            if p_num == self.current_page_index:
                highlight_rect = rect * self.current_render_scale

                item = QGraphicsRectItem(QRectF(highlight_rect.x0, highlight_rect.y0, highlight_rect.width, highlight_rect.height))
                if i == self.current_search_index:
                    item.setBrush(QColor(255, 255, 0, 100))
                    item.setPen(QPen(QColor(255, 165, 0), 1))
                else:
                    item.setBrush(QColor(0, 150, 255, 70))
                    item.setPen(QPen(Qt.PenStyle.NoPen))
                self.view.scene().addItem(item)

    def close(self):
        logger.info(f"Fechando viewer para o arquivo: {os.path.basename(self.file_path)}")
        if self.thumbnail_loader and self.thumbnail_loader.isRunning():
            self.thumbnail_loader.requestInterruption()
            self.thumbnail_loader.wait()
        if self.page_render_thread and self.page_render_thread.isRunning():
            self.page_render_thread.requestInterruption()
            self.page_render_thread.wait()
        if self.doc:
            self.doc.close()
        super().close()

# #############################################################################
# SEÇÃO 4: JANELA PRINCIPAL E LÓGICA DA APLICAÇÃO
# #############################################################################

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("QuantumPDF v8.8")
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.resize(1280, 800)
        self.normal_geometry = None
        self.setAcceptDrops(True)
        self.current_selection_index = -1

        self.icon_manager = IconManager()

        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout(main_widget)
        main_layout.setContentsMargins(0,0,0,0)
        main_layout.setSpacing(0)

        self.title_bar = self._create_custom_title_bar()
        main_layout.addWidget(self.title_bar)

        content_widget = QWidget()
        content_layout = QHBoxLayout(content_widget)
        content_layout.setContentsMargins(0,0,0,0)
        content_layout.setSpacing(0)
        main_layout.addWidget(content_widget)

        self._apply_stylesheet()
        self._create_actions()

        self.thumbnail_sidebar = self._create_thumbnail_sidebar()
        content_layout.addWidget(self.thumbnail_sidebar)

        self.tab_widget = QTabWidget()
        self.tab_widget.setTabsClosable(True)
        self.tab_widget.setMovable(True)
        self.tab_widget.tabBar().setElideMode(Qt.TextElideMode.ElideRight)
        self.tab_widget.tabCloseRequested.connect(self._close_tab)
        self.tab_widget.currentChanged.connect(self._on_tab_changed)

        self.welcome_screen = WelcomeScreen()
        self.welcome_screen.clicked.connect(self._open_file)

        self.view_stack = QStackedWidget()
        self.view_stack.addWidget(self.welcome_screen)
        self.view_stack.addWidget(self.tab_widget)

        content_layout.addWidget(self.view_stack)

        self.tool_sidebar = self._create_tool_sidebar()
        content_layout.addWidget(self.tool_sidebar)

        self._setup_status_bar()

        self._update_ui_for_current_tab()
        self.old_pos = None

        self.search_shortcut = QShortcut(QKeySequence("Ctrl+F"), self)
        self.search_shortcut.activated.connect(self._focus_search_input)

        logger.info("Janela principal criada com sucesso.")

    def _create_custom_title_bar(self):
        title_bar = QWidget()
        title_bar.setObjectName("customTitleBar")
        title_bar_layout = QHBoxLayout(title_bar)
        title_bar_layout.setContentsMargins(10, 5, 5, 5)
        title_bar_layout.setSpacing(10)

        title_label = QLabel("QuantumPDF")
        title_label.setObjectName("titleLabel")
        title_bar_layout.addWidget(title_label)
        title_bar_layout.addStretch()

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Buscar no documento (Ctrl+f)...")
        self.search_input.setFixedWidth(250)
        self.search_input.textChanged.connect(self._on_search_text_changed)
        self.search_timer = QTimer(self)
        self.search_timer.setSingleShot(True)
        self.search_timer.timeout.connect(self._trigger_search)
        title_bar_layout.addWidget(self.search_input)

        self.search_results_label = QLabel("")
        title_bar_layout.addWidget(self.search_results_label)

        self.search_prev_button = QPushButton(self.icon_manager.get_icon("arrow-up", "#555"), "")
        self.search_prev_button.clicked.connect(self._go_to_prev_result)
        self.search_prev_button.setFixedSize(24,24)
        title_bar_layout.addWidget(self.search_prev_button)

        self.search_next_button = QPushButton(self.icon_manager.get_icon("arrow-down", "#555"), "")
        self.search_next_button.clicked.connect(self._go_to_next_result)
        self.search_next_button.setFixedSize(24,24)
        title_bar_layout.addWidget(self.search_next_button)

        line = QFrame()
        line.setFrameShape(QFrame.Shape.VLine)
        line.setFrameShadow(QFrame.Shadow.Sunken)
        title_bar_layout.addWidget(line)

        btn_size = QSize(28, 28)
        minimize_button = QPushButton(self.icon_manager.get_icon("minimize", "#333"), "")
        minimize_button.setFixedSize(btn_size)
        minimize_button.setObjectName("titleBarButton")
        minimize_button.clicked.connect(self.showMinimized)

        self.maximize_button = QPushButton(self.icon_manager.get_icon("maximize", "#333"), "")
        self.maximize_button.setFixedSize(btn_size)
        self.maximize_button.setObjectName("titleBarButton")
        self.maximize_button.clicked.connect(self._toggle_maximize)

        close_button = QPushButton(self.icon_manager.get_icon("close", "#333"), "")
        close_button.setFixedSize(btn_size)
        close_button.setObjectName("closeButton")
        close_button.clicked.connect(self.close)

        title_bar_layout.addWidget(minimize_button)
        title_bar_layout.addWidget(self.maximize_button)
        title_bar_layout.addWidget(close_button)
        return title_bar

    def _setup_status_bar(self):
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)

        status_right_container = QWidget()
        status_right_layout = QHBoxLayout(status_right_container)
        status_right_layout.setContentsMargins(0, 0, 5, 0)
        status_right_layout.setSpacing(2)

        self.status_prev_page_btn = QPushButton(self.icon_manager.get_icon("arrow-up", "#333"), "")
        self.status_prev_page_btn.setFixedSize(22,22)
        self.status_prev_page_btn.clicked.connect(self._go_to_prev_page)

        self.page_input = QLineEdit("0")
        self.page_input.setValidator(QIntValidator(1, 9999))
        self.page_input.returnPressed.connect(self._go_to_page_from_input)
        self.page_input.setFixedWidth(45)
        self.page_input.setAlignment(Qt.AlignmentFlag.AlignRight)

        self.page_count_label = QLabel("/ 0")
        self.page_count_label.setFixedWidth(40)

        self.status_next_page_btn = QPushButton(self.icon_manager.get_icon("arrow-down", "#333"), "")
        self.status_next_page_btn.setFixedSize(22,22)
        self.status_next_page_btn.clicked.connect(self._go_to_next_page)

        self.status_zoom_label = QLabel("100%")
        self.status_zoom_label.setFixedWidth(50)
        self.status_zoom_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        line_sep = QFrame()
        line_sep.setFrameShape(QFrame.Shape.VLine)
        line_sep.setFrameShadow(QFrame.Shadow.Sunken)

        status_right_layout.addWidget(self.status_prev_page_btn)
        status_right_layout.addWidget(self.page_input)
        status_right_layout.addWidget(self.page_count_label)
        status_right_layout.addWidget(self.status_next_page_btn)
        status_right_layout.addWidget(line_sep)
        status_right_layout.addWidget(self.status_zoom_label)

        self.status_bar.addPermanentWidget(status_right_container)


    def _toggle_maximize(self):
        if self.isMaximized():
            logger.debug("Restaurando janela.")
            self.showNormal()
        else:
            logger.debug("Maximizando janela.")
            self.showMaximized()

    def changeEvent(self, event):
        if event.type() == QEvent.Type.WindowStateChange:
            if self.isMaximized():
                self.maximize_button.setIcon(self.icon_manager.get_icon("restore", "#333"))
            else:
                self.maximize_button.setIcon(self.icon_manager.get_icon("maximize", "#333"))
        super().changeEvent(event)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton and self.title_bar.underMouse() and not self.isMaximized():
            self.old_pos = event.globalPosition().toPoint()

    def mouseDoubleClickEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton and self.title_bar.underMouse():
            self._toggle_maximize()

    def mouseMoveEvent(self, event):
        if self.old_pos and not self.isMaximized():
            delta = QPoint(event.globalPosition().toPoint() - self.old_pos)
            self.move(self.x() + delta.x(), self.y() + delta.y())
            self.old_pos = event.globalPosition().toPoint()

    def mouseReleaseEvent(self, event):
        self.old_pos = None

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            urls = event.mimeData().urls()
            if any(url.toLocalFile().lower().endswith('.pdf') for url in urls):
                event.acceptProposedAction()

    def dropEvent(self, event):
        urls = event.mimeData().urls()
        for url in urls:
            path = url.toLocalFile()
            if path.lower().endswith('.pdf'):
                self._add_new_tab(path)

    def _apply_stylesheet(self):
        self.icon_color = "#333333"
        self.setStyleSheet(f"""
            QMainWindow {{ background-color: #ffffff; }}
            #customTitleBar {{
                background-color: #f0f2f5;
                border-bottom: 1px solid #dcdcdc;
                padding: 5px 0;
            }}
            #titleLabel {{ color: #333; font-weight: bold; }}
            QPushButton {{ border: none; border-radius: 4px; outline: none; }}
            #customTitleBar QPushButton:hover {{ background-color: #e0e0e0; }}
            #closeButton:hover {{ background-color: #ff6e6e; }}

            #customTitleBar QLineEdit {{
                border: 1px solid #dcdcdc;
                border-radius: 4px;
                padding: 5px 8px;
                margin: 0;
            }}
            #customTitleBar QLineEdit:focus {{
                border: 1px solid #4d90fe;
                background-color: #ffffff;
            }}

            #thumbnailSidebar {{
                background-color: #f0f2f5;
                border-right: 1px solid #dcdcdc;
            }}
            #thumbnailSidebar QLabel {{ color: #333333; font-weight: bold; }}
            #toolSidebar {{ background-color: #f0f2f5; border-left: 1px solid #dcdcdc; }}

            #toolSidebar QPushButton {{
                border: 1px solid transparent; padding: 4px; margin: 1px 0; border-radius: 4px;
            }}
            #toolSidebar QPushButton:hover {{ background-color: #e0e0e0; border-color: #ccc; }}
            #toolSidebar QPushButton:checked {{
                background-color: #e0e0e0;
                border-color: #cccccc;
            }}
            #toolSidebar QPushButton:disabled {{ background-color: #f0f0f0; border-color: #e0e0e0; }}

            QTabWidget::pane {{ border: none; }}
            QTabBar::tab {{
                background: #f0f2f5; border: 1px solid #dcdcdc; border-bottom: none;
                padding: 8px 12px; margin-right: -1px; min-width: 50px; max-width: 200px;
            }}
            QTabBar::tab:selected {{ background: #ffffff; border-bottom-color: #ffffff; }}
            QTabBar::tab:!selected:hover {{ background: #e8eaf0; }}
            QTabBar::tab:focus {{ outline: none; }}
            QLineEdit {{ border: 1px solid #cccccc; border-radius: 4px; padding: 4px 8px; }}

            QStatusBar {{
                background-color: #f0f2f5;
                border-top: 1px solid #dcdcdc;
                padding: 2px;
            }}
            QStatusBar QLineEdit {{ padding: 1px 4px; }}
            QStatusBar QPushButton {{
                border: none;
                background-color: transparent;
                padding: 2px;
            }}
            QStatusBar QPushButton:hover {{
                background-color: #dcdcdc;
                border-radius: 2px;
            }}
            QStatusBar QLabel {{
                margin: 0 2px;
            }}

            #ThumbnailListWidget {{ background-color: #f0f2f5; border: none; padding: 5px; }}
            #ThumbnailListWidget::item {{
                border: 2px solid transparent;
                border-radius: 4px;
                margin: 2px;
                padding: 0px;
                background-color: transparent;
            }}
            #ThumbnailListWidget::item:selected {{
                border: 2px solid transparent;
                background-color: transparent;
            }}

            QScrollBar:vertical {{
                border: none;
                background: #f0f2f5;
                width: 10px;
                margin: 0px 0px 0px 0px;
            }}
            QScrollBar::handle:vertical {{
                background: #c1c1c1;
                min-height: 20px;
                border-radius: 5px;
            }}
            QScrollBar::handle:vertical:hover {{
                background: #a8a8a8;
            }}

            #PDFGraphicsView {{ background-color: #e9e9e9; border: none; }}
            QWidget#PDFViewerWidget {{ border: none; }}

            #welcomeScreen {{ background-color: #ffffff; }}
            #welcomeTitle {{ font-size: 28px; font-weight: 300; color: #495057; }}
            #welcomeSubtitle {{ font-size: 18px; color: #6c757d; }}
            #welcomeInstruction {{ font-size: 14px; color: #adb5bd; }}

            AdvancedPrintDialog, AdvancedPrintDialog QGroupBox {{ background-color: #f9f9f9; }}

            /* Estilos para botões de Imprimir e Cancelar */
            #printButton, #cancelButton {{
                padding: 8px 16px;
                min-width: 90px;
                font-size: 13px;
                border-radius: 4px;
            }}
            #printButton {{
                background-color: #0078d7;
                color: white;
                border: 1px solid #005a9e;
            }}
            #printButton:hover {{
                background-color: #005a9e;
            }}
            #cancelButton {{
                background-color: #f0f0f0;
                border: 1px solid #cccccc;
                color: #333;
            }}
            #cancelButton:hover {{
                background-color: #e0e0e0;
            }}

            /* Estilos para botões de navegação do preview */
            #previewNavContainer QPushButton {{
                background-color: #f0f0f0;
                border: 1px solid #cccccc;
                border-radius: 4px;
                padding: 5px;
                min-width: 35px;
                max-width: 35px;
            }}
            #previewNavContainer QPushButton:hover {{
                background-color: #e0e0e0;
            }}
        """)

    def _create_actions(self):
        self.action_open = QAction(self.icon_manager.get_icon("open", self.icon_color), "Abrir...", self)
        self.action_open.triggered.connect(self._open_file)

        self.action_print = QAction(self.icon_manager.get_icon("print", self.icon_color), "Imprimir...", self)
        self.action_print.triggered.connect(self._print_pdf)

        self.action_prev_page = QAction(self.icon_manager.get_icon("arrow-up", self.icon_color), "Página Anterior", self)
        self.action_prev_page.triggered.connect(self._go_to_prev_page)
        self.action_next_page = QAction(self.icon_manager.get_icon("arrow-down", self.icon_color), "Próxima Página", self)
        self.action_next_page.triggered.connect(self._go_to_next_page)

        self.action_zoom_in = QAction(self.icon_manager.get_icon("zoom-in", self.icon_color), "Aumentar Zoom", self)
        self.action_zoom_in.triggered.connect(self._zoom_in)
        self.action_zoom_out = QAction(self.icon_manager.get_icon("zoom-out", self.icon_color), "Diminuir Zoom", self)
        self.action_zoom_out.triggered.connect(self._zoom_out)
        self.action_fit_width = QAction(self.icon_manager.get_icon("fit-width", self.icon_color), "Ajustar à Largura", self)
        self.action_fit_width.triggered.connect(self._fit_to_width)
        self.action_fit_page = QAction(self.icon_manager.get_icon("fit-page", self.icon_color), "Ajustar à Página", self)
        self.action_fit_page.triggered.connect(self._fit_to_page)

        self.action_rotate_right = QAction(self.icon_manager.get_icon("rotate-right", self.icon_color), "Girar à Direita (Horário)", self)
        self.action_rotate_right.triggered.connect(lambda: self._rotate_page(90))
        self.action_rotate_left = QAction(self.icon_manager.get_icon("rotate-left", self.icon_color), "Girar à Esquerda (Anti-horário)", self)
        self.action_rotate_left.triggered.connect(lambda: self._rotate_page(-90))

        self.action_select_mode = QAction(self.icon_manager.get_icon("select", self.icon_color), "Selecionar Texto", self)
        self.action_select_mode.setCheckable(True)
        self.action_select_mode.setChecked(True)
        self.action_select_mode.triggered.connect(lambda: self._set_interaction_mode('select'))

        self.action_pan_mode = QAction(self.icon_manager.get_icon("hand", self.icon_color), "Arrastar (Mãozinha)", self)
        self.action_pan_mode.setCheckable(True)
        self.action_pan_mode.triggered.connect(lambda: self._set_interaction_mode('pan'))

        self.tool_mode_group = QActionGroup(self)
        self.tool_mode_group.addAction(self.action_select_mode)
        self.tool_mode_group.addAction(self.action_pan_mode)

    def _create_thumbnail_sidebar(self):
        sidebar = QWidget()
        sidebar.setObjectName("thumbnailSidebar")
        sidebar.setFixedWidth(195)

        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(10, 10, 5, 10)
        layout.setSpacing(10)

        layout.addWidget(QLabel("Miniaturas"))
        self.thumbnail_list = ThumbnailListWidget()
        self.thumbnail_list.page_selected.connect(self._go_to_page_from_thumbnail)
        layout.addWidget(self.thumbnail_list)

        return sidebar

    def _create_tool_sidebar(self):
        sidebar = QWidget()
        sidebar.setObjectName("toolSidebar")
        sidebar.setFixedWidth(65)

        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(5)

        layout.addWidget(self._create_tool_button(self.action_open))
        layout.addWidget(self._create_tool_button(self.action_print))
        layout.addWidget(self._create_separator())
        layout.addWidget(self._create_tool_button(self.action_prev_page))
        layout.addWidget(self._create_tool_button(self.action_next_page))
        layout.addWidget(self._create_separator())
        layout.addWidget(self._create_tool_button(self.action_zoom_in))
        layout.addWidget(self._create_tool_button(self.action_zoom_out))
        layout.addWidget(self._create_tool_button(self.action_fit_width))
        layout.addWidget(self._create_tool_button(self.action_fit_page))
        layout.addWidget(self._create_separator())
        layout.addWidget(self._create_tool_button(self.action_rotate_left))
        layout.addWidget(self._create_tool_button(self.action_rotate_right))
        layout.addWidget(self._create_separator())
        layout.addWidget(self._create_tool_button(self.action_select_mode))
        layout.addWidget(self._create_tool_button(self.action_pan_mode))

        layout.addStretch()
        return sidebar

    def _create_separator(self):
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setFrameShadow(QFrame.Shadow.Sunken)
        return line

    def _create_tool_button(self, action):
        button = QPushButton(action.icon(), "")
        button.setToolTip(action.toolTip())
        button.setCheckable(action.isCheckable())

        if action.isCheckable():
            button.setChecked(action.isChecked())
            action.toggled.connect(button.setChecked)
            if hasattr(self, 'tool_mode_group') and self.tool_mode_group and action in self.tool_mode_group.actions():
                 button.setAutoExclusive(True)

        button.clicked.connect(action.trigger)
        action.changed.connect(lambda: button.setEnabled(action.isEnabled()))
        button.setIconSize(QSize(24, 24))
        button.setFixedSize(32, 32)
        return button

    def _focus_search_input(self):
        if self.search_input.isEnabled():
            self.search_input.setFocus()
            self.search_input.selectAll()

    def _open_file(self):
        paths, _ = QFileDialog.getOpenFileNames(self, "Abrir Arquivo PDF", "", "Arquivos PDF (*.pdf)")
        for path in paths:
            if path:
                self._add_new_tab(path)

    def _add_new_tab(self, file_path):
        logger.info(f"Adicionando nova aba para o arquivo: {file_path}")
        for i in range(self.tab_widget.count()):
            viewer = self.tab_widget.widget(i)
            if viewer and viewer.file_path == file_path:
                logger.warning(f"Arquivo '{file_path}' já está aberto. Trocando para a aba existente.")
                self.tab_widget.setCurrentIndex(i)
                return

        viewer = PDFViewer(file_path, self)
        if not viewer.doc:
            viewer.deleteLater()
            return

        viewer.setObjectName("PDFViewerWidget")
        viewer.page_changed.connect(self._update_page_selection)
        viewer.zoom_changed.connect(lambda z: self.status_zoom_label.setText(f"{int(z*100)}%"))
        viewer.copied_to_clipboard.connect(self.show_notification)
        viewer.search_results_updated.connect(self._update_search_results_label)
        viewer.rotation_changed.connect(self._refresh_thumbnails)

        index = self.tab_widget.addTab(viewer, os.path.basename(file_path))
        self.tab_widget.setCurrentIndex(index)
        self.tab_widget.setTabToolTip(index, file_path)

        self._refresh_thumbnails()

        QTimer.singleShot(50, viewer.fit_to_page)

    def _on_thumbnail_ready(self, viewer: PDFViewer, page_num: int, pixmap: QPixmap, is_landscape: bool):
        """Armazena o pixmap bruto e atualiza o ícone do item na lista."""
        if page_num < len(viewer.raw_thumbnail_pixmaps):
            viewer.raw_thumbnail_pixmaps[page_num] = pixmap
            viewer.thumbnail_orientations[page_num] = is_landscape

            if self._get_current_viewer() is viewer:
                is_selected = (page_num == viewer.current_page_index)
                self._update_thumbnail_icon(page_num, is_selected)

    def _update_thumbnail_icon(self, page_num: int, is_selected: bool):
        """Cria e define o ícone de uma miniatura, aplicando o destaque se necessário."""
        viewer = self._get_current_viewer()
        if not viewer or not (0 <= page_num < viewer.page_count()):
            return

        raw_pixmap = viewer.raw_thumbnail_pixmaps[page_num]
        item = self.thumbnail_list.item(page_num)
        if not raw_pixmap or not item:
            return

        TARGET_WIDTH = 130
        TEXT_AREA_HEIGHT = 20
        HIGHLIGHT_COLOR = QColor("#d4e8fa")

        scaled_pixmap = raw_pixmap.scaledToWidth(TARGET_WIDTH, Qt.TransformationMode.SmoothTransformation)
        final_size = QSize(scaled_pixmap.width(), scaled_pixmap.height() + TEXT_AREA_HEIGHT)
        final_pixmap = QPixmap(final_size)
        final_pixmap.fill(Qt.GlobalColor.transparent)

        painter = QPainter(final_pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        if is_selected:
            highlight_rect = QRectF(0, 0, scaled_pixmap.width(), scaled_pixmap.height())
            painter.fillRect(highlight_rect, HIGHLIGHT_COLOR)

        painter.drawPixmap(0, 0, scaled_pixmap)

        font = self.font()
        font.setPointSize(9)
        painter.setFont(font)
        painter.setPen(QColor("#333333"))
        text_rect = QRectF(0, scaled_pixmap.height(), final_pixmap.width(), TEXT_AREA_HEIGHT)
        painter.drawText(text_rect, Qt.AlignmentFlag.AlignCenter, f"{page_num + 1}")
        painter.end()

        item.setIcon(QIcon(final_pixmap))
        item.setSizeHint(final_pixmap.size())


    def show_notification(self, message):
        logger.info(f"Exibindo notificação: '{message}'")
        self.status_bar.showMessage(message, 3000)

        animation = QPropertyAnimation(self.status_bar, b"styleSheet")
        animation.setDuration(300)
        animation.setStartValue("QStatusBar { color: #4CAF50; }")
        animation.setEndValue("QStatusBar { color: inherit; }")
        animation.start()

    def _close_tab(self, index):
        widget = self.tab_widget.widget(index)
        if widget:
            logger.info(f"Fechando aba {index}: {widget.file_path}")
            widget.close()
            self.tab_widget.removeTab(index)

        if self.tab_widget.count() == 0:
            self.current_selection_index = -1
            self._update_ui_for_current_tab()

    def _get_current_viewer(self) -> Optional[PDFViewer]:
        return self.tab_widget.currentWidget()

    def _on_tab_changed(self, index):
        self.current_selection_index = -1
        self._update_ui_for_current_tab()

    def _update_page_selection(self):
        """Atualiza a seleção visual da miniatura e o scroll."""
        viewer = self._get_current_viewer()
        if not viewer: return

        new_selection_index = viewer.current_page_index

        if self.current_selection_index != -1 and self.current_selection_index < self.thumbnail_list.count():
             self._update_thumbnail_icon(self.current_selection_index, False)

        if new_selection_index < self.thumbnail_list.count():
            self._update_thumbnail_icon(new_selection_index, True)

        self.current_selection_index = new_selection_index

        self.page_input.setText(str(new_selection_index + 1))
        self.thumbnail_list.setCurrentRow(new_selection_index)
        self.thumbnail_list.scrollToItem(
            self.thumbnail_list.item(new_selection_index),
            QListWidget.ScrollHint.PositionAtCenter
        )

    def _refresh_thumbnails(self):
        """Reinicia o carregamento de todas as miniaturas para a aba atual."""
        if viewer := self._get_current_viewer():
            logger.info(f"Atualizando miniaturas para rotação: {viewer.rotation} graus.")
            viewer.raw_thumbnail_pixmaps = [None] * viewer.page_count()
            self._update_ui_for_current_tab()

            if viewer.thumbnail_loader and viewer.thumbnail_loader.isRunning():
                viewer.thumbnail_loader.requestInterruption()
                viewer.thumbnail_loader.wait()

            viewer.thumbnail_loader = ThumbnailLoaderThread(viewer.doc, viewer.rotation)
            viewer.thumbnail_loader.thumbnail_ready.connect(
                lambda page_num, pixmap, is_landscape, v=viewer: self._on_thumbnail_ready(v, page_num, pixmap, is_landscape)
            )
            viewer.thumbnail_loader.start()

    def _update_ui_for_current_tab(self):
        viewer = self._get_current_viewer()
        is_doc_open = viewer is not None

        if is_doc_open:
            self.view_stack.setCurrentWidget(self.tab_widget)
        else:
            self.view_stack.setCurrentWidget(self.welcome_screen)

        doc_dependent_actions = [
            self.action_print, self.action_prev_page, self.action_next_page,
            self.action_zoom_in, self.action_zoom_out, self.action_fit_width,
            self.action_fit_page, self.action_rotate_left, self.action_rotate_right,
            self.action_select_mode, self.action_pan_mode
        ]
        for action in doc_dependent_actions:
            action.setEnabled(is_doc_open)

        self.search_input.setEnabled(is_doc_open)
        self.page_input.setEnabled(is_doc_open)
        self.thumbnail_sidebar.setEnabled(is_doc_open)
        self.status_prev_page_btn.setEnabled(is_doc_open)
        self.status_next_page_btn.setEnabled(is_doc_open)

        has_search_results = is_doc_open and viewer and len(viewer.search_results) > 0
        self.search_prev_button.setEnabled(has_search_results)
        self.search_next_button.setEnabled(has_search_results)

        self.thumbnail_list.setUpdatesEnabled(False)
        self.thumbnail_list.clear()

        if is_doc_open:
            self.status_zoom_label.setText(f"{int(viewer.current_zoom_factor*100)}%")
            self.page_count_label.setText(f"/ {viewer.page_count()}")

            for i in range(viewer.page_count()):
                item = QListWidgetItem()
                self.thumbnail_list.addItem(item)

            self._update_page_selection()
        else:
            self.status_zoom_label.setText("-")
            self.search_input.clear()
            self.search_results_label.setText("")
            self.page_input.setText("0")
            self.page_count_label.setText("/ 0")

        self.thumbnail_list.setUpdatesEnabled(True)

    def _go_to_prev_page(self):
        if viewer := self._get_current_viewer():
            if viewer.current_page_index > 0:
                viewer.scroll_to_bottom_on_load = True
                viewer.display_page(viewer.current_page_index - 1)

    def _go_to_next_page(self):
        if viewer := self._get_current_viewer():
            if viewer.current_page_index < viewer.page_count() - 1:
                viewer.display_page(viewer.current_page_index + 1)

    def _go_to_page_from_input(self):
        if viewer := self._get_current_viewer():
            try:
                page_num = int(self.page_input.text()) - 1
                if 0 <= page_num < viewer.page_count():
                    viewer.display_page(page_num)
                else:
                    self.page_input.setText(str(viewer.current_page_index + 1))
            except ValueError:
                self.page_input.setText(str(viewer.current_page_index + 1))

    def _go_to_page_from_thumbnail(self, page_num):
        if viewer := self._get_current_viewer():
            viewer.display_page(page_num)

    def _zoom_in(self):
        if viewer := self._get_current_viewer():
            viewer.zoom_in()

    def _zoom_out(self):
        if viewer := self._get_current_viewer():
            viewer.zoom_out()

    def _fit_to_width(self):
        if viewer := self._get_current_viewer():
            viewer.fit_to_width()

    def _fit_to_page(self):
        if viewer := self._get_current_viewer():
            viewer.fit_to_page()

    def _rotate_page(self, angle):
        if viewer := self._get_current_viewer():
            viewer.rotate(angle)

    def _set_interaction_mode(self, mode):
        if viewer := self._get_current_viewer():
            viewer.set_interaction_mode(mode)

    def _on_search_text_changed(self):
        self.search_timer.start(300)

    def _trigger_search(self):
        if viewer := self._get_current_viewer():
            viewer.search_text(self.search_input.text())

    def _go_to_next_result(self):
        if viewer := self._get_current_viewer():
            if viewer.search_results:
                new_index = (viewer.current_search_index + 1) % len(viewer.search_results)
                viewer.go_to_result(new_index)

    def _go_to_prev_result(self):
        if viewer := self._get_current_viewer():
            if viewer.search_results:
                new_index = (viewer.current_search_index - 1 + len(viewer.search_results)) % len(viewer.search_results)
                viewer.go_to_result(new_index)

    def _update_search_results_label(self, current, total):
        if total > 0:
            self.search_results_label.setText(f"{current}/{total}")
        else:
            self.search_results_label.setText("")

        has_results = total > 0
        self.search_prev_button.setEnabled(has_results)
        self.search_next_button.setEnabled(has_results)

    def _print_pdf(self):
        if not (viewer := self._get_current_viewer()): return

        dialog = AdvancedPrintDialog(self, viewer=viewer)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            logger.info("Diálogo de impressão aceito. Iniciando processo de impressão.")
            settings = dialog.get_print_settings()

            printer = QPrinter()
            printer.setPrinterName(settings['printer_name'])
            printer.setPageOrientation(settings['orientation'])
            printer.setCopyCount(settings['copies'])
            printer.setColorMode(settings['color_mode'])

            painter = QPainter()
            if not painter.begin(printer):
                logger.error("Falha ao iniciar o QPainter na impressora.")
                self.show_notification("Erro: Não foi possível iniciar a impressão.")
                return

            doc = viewer.doc
            for page_num in settings['page_list']:
                logger.debug(f"Imprimindo página {page_num}...")
                page = doc.load_page(page_num - 1)

                pix = page.get_pixmap(matrix=fitz.Matrix(4, 4), alpha=False)
                img = QImage(pix.samples, pix.width, pix.height, pix.stride, QImage.Format.Format_RGB888)

                rect = painter.viewport()
                size = img.size()
                size.scale(rect.size(), Qt.AspectRatioMode.KeepAspectRatio)

                painter.setViewport(rect.x(), rect.y(), size.width(), size.height())
                painter.setWindow(img.rect())
                painter.drawImage(QPoint(0,0), img)

                if page_num != settings['page_list'][-1]:
                    printer.newPage()

            painter.end()
            self.show_notification("Documento enviado para a impressora.")
        else:
            logger.info("Diálogo de impressão cancelado.")

    def closeEvent(self, event):
        logger.info("Sinal de fechamento recebido. Encerrando a aplicação.")
        super().closeEvent(event)

class AdvancedPrintDialog(QDialog):
    """Diálogo de impressão completo e personalizado."""
    def __init__(self, parent, viewer):
        super().__init__(parent)
        self.viewer = viewer
        self.doc = viewer.doc
        self.preview_page_index = viewer.current_page_index
        self.icon_manager = IconManager()

        self.setWindowTitle("Imprimir")
        self.setMinimumSize(850, 600)
        self.setObjectName("AdvancedPrintDialog")

        main_layout = QHBoxLayout(self)
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(15, 15, 15, 15)

        settings_widget = QWidget()
        settings_layout = QVBoxLayout(settings_widget)
        settings_layout.setContentsMargins(0, 0, 0, 0)
        settings_layout.setSpacing(15)

        printer_group = QGroupBox("Impressora")
        printer_layout = QGridLayout(printer_group)
        self.printer_combo = QComboBox()
        printers = QPrinterInfo.availablePrinterNames()
        self.printer_combo.addItems(printers)
        default_printer = QPrinterInfo.defaultPrinterName()
        if default_printer in printers:
            self.printer_combo.setCurrentText(default_printer)

        self.copies_spinbox = QSpinBox()
        self.copies_spinbox.setMinimum(1)
        self.copies_spinbox.setValue(1)

        self.grayscale_check = QCheckBox("Imprimir em escala de cinza (preto e branco)")

        printer_layout.addWidget(QLabel("Nome:"), 0, 0)
        printer_layout.addWidget(self.printer_combo, 0, 1)
        printer_layout.addWidget(QLabel("Cópias:"), 1, 0)
        printer_layout.addWidget(self.copies_spinbox, 1, 1)
        printer_layout.addWidget(self.grayscale_check, 2, 0, 1, 2)
        settings_layout.addWidget(printer_group)

        pages_group = QGroupBox("Páginas a serem impressas")
        pages_layout = QVBoxLayout(pages_group)
        self.radio_all = QRadioButton(f"Tudo ({self.doc.page_count})")
        self.radio_all.setChecked(True)
        self.radio_current = QRadioButton(f"Página atual ({viewer.current_page_index + 1})")

        range_layout = QHBoxLayout()
        self.radio_range = QRadioButton("Páginas")
        self.range_input = QLineEdit()
        self.range_input.setPlaceholderText("ex: 1-5, 8, 11-13")
        self.range_input.setEnabled(False)
        self.radio_range.toggled.connect(self.range_input.setEnabled)
        range_layout.addWidget(self.radio_range)
        range_layout.addWidget(self.range_input)

        pages_layout.addWidget(self.radio_all)
        pages_layout.addWidget(self.radio_current)
        pages_layout.addLayout(range_layout)
        settings_layout.addWidget(pages_group)

        orientation_group = QGroupBox("Orientação")
        orientation_layout = QHBoxLayout(orientation_group)
        self.orient_auto = QRadioButton("Automático")
        self.orient_auto.setChecked(True)
        self.orient_portrait = QRadioButton("Retrato")
        self.orient_landscape = QRadioButton("Paisagem")
        orientation_layout.addWidget(self.orient_auto)
        orientation_layout.addWidget(self.orient_portrait)
        orientation_layout.addWidget(self.orient_landscape)
        settings_layout.addWidget(orientation_group)

        settings_layout.addStretch()
        main_layout.addWidget(settings_widget, 1)

        preview_widget = QWidget()
        preview_layout = QVBoxLayout(preview_widget)
        preview_layout.setContentsMargins(0, 0, 0, 0)

        self.preview_view = QGraphicsView()
        self.preview_scene = QGraphicsScene(self.preview_view)
        self.preview_view.setScene(self.preview_scene)
        # AJUSTE: Alinhamento centralizado para a view do preview
        self.preview_view.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.preview_view.setStyleSheet("background-color: #e0e0e0; border: 1px solid #c0c0c0; border-radius: 4px;")
        preview_layout.addWidget(self.preview_view)

        preview_nav_container = QWidget()
        preview_nav_container.setObjectName("previewNavContainer")
        preview_nav_layout = QHBoxLayout(preview_nav_container)
        preview_nav_layout.setContentsMargins(0, 5, 0, 5)
        preview_nav_layout.setSpacing(10)

        self.prev_preview_btn = QPushButton(self.icon_manager.get_icon("arrow-up", "#333"), "")
        self.prev_preview_btn.clicked.connect(self.show_prev_preview)
        self.preview_label = QLabel("")
        self.preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.next_preview_btn = QPushButton(self.icon_manager.get_icon("arrow-down", "#333"), "")
        self.next_preview_btn.clicked.connect(self.show_next_preview)

        preview_nav_layout.addStretch()
        preview_nav_layout.addWidget(self.prev_preview_btn)
        preview_nav_layout.addWidget(self.preview_label)
        preview_nav_layout.addWidget(self.next_preview_btn)
        preview_nav_layout.addStretch()
        preview_layout.addWidget(preview_nav_container)

        main_layout.addWidget(preview_widget, 2)

        self.print_button = QPushButton("Imprimir")
        self.print_button.setObjectName("printButton")
        self.print_button.setDefault(True)
        self.cancel_button = QPushButton("Cancelar")
        self.cancel_button.setObjectName("cancelButton")
        self.print_button.clicked.connect(self.accept)
        self.cancel_button.clicked.connect(self.reject)

        button_layout = QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(self.cancel_button)
        button_layout.addWidget(self.print_button)
        settings_layout.addLayout(button_layout)

        self.orient_auto.toggled.connect(self._update_preview)
        self.orient_portrait.toggled.connect(self._update_preview)
        self.orient_landscape.toggled.connect(self._update_preview)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        QTimer.singleShot(0, self._fit_preview_to_view)

    def showEvent(self, event):
        super().showEvent(event)
        self._update_preview()

    def _fit_preview_to_view(self):
        if self.preview_scene.items():
            self.preview_view.fitInView(self.preview_scene.sceneRect(), Qt.AspectRatioMode.KeepAspectRatio)

    def show_prev_preview(self):
        if self.preview_page_index > 0:
            self.preview_page_index -= 1
            self._update_preview()

    def show_next_preview(self):
        if self.preview_page_index < self.doc.page_count - 1:
            self.preview_page_index += 1
            self._update_preview()

    def _update_preview(self):
        self.preview_scene.clear()
        page = self.doc.load_page(self.preview_page_index)

        pix = page.get_pixmap()
        qimg = QImage(pix.samples, pix.width, pix.height, pix.stride, QImage.Format.Format_RGB888)
        pixmap = QPixmap.fromImage(qimg)

        is_landscape_selected = self.orient_landscape.isChecked()
        is_portrait_selected = self.orient_portrait.isChecked()
        page_is_landscape = page.rect.width > page.rect.height

        if is_landscape_selected or (self.orient_auto.isChecked() and page_is_landscape):
            if not page_is_landscape:
                 transform = QTransform().rotate(90)
                 pixmap = pixmap.transformed(transform, Qt.TransformationMode.SmoothTransformation)
        elif is_portrait_selected and page_is_landscape:
            transform = QTransform().rotate(-90)
            pixmap = pixmap.transformed(transform, Qt.TransformationMode.SmoothTransformation)

        self.preview_scene.addPixmap(pixmap)
        self._fit_preview_to_view()

        self.preview_label.setText(f"Página {self.preview_page_index + 1} de {self.doc.page_count}")
        self.prev_preview_btn.setEnabled(self.preview_page_index > 0)
        self.next_preview_btn.setEnabled(self.preview_page_index < self.doc.page_count - 1)

    def _parse_page_ranges(self, text):
        if not text: return []
        pages = set()
        try:
            for part in text.split(','):
                part = part.strip()
                if not part: continue
                if '-' in part:
                    start, end = map(int, part.split('-'))
                    if start > end: start, end = end, start
                    pages.update(range(start, end + 1))
                else:
                    pages.add(int(part))
        except ValueError:
            QMessageBox.warning(self, "Intervalo Inválido", "O formato do intervalo de páginas é inválido. Use números, vírgulas e hifens, como '1-5, 8'.")
            return None

        valid_pages = [p for p in sorted(list(pages)) if 1 <= p <= self.doc.page_count]
        return valid_pages

    def get_print_settings(self) -> Optional[Dict]:
        page_list = []
        if self.radio_all.isChecked():
            page_list = list(range(1, self.doc.page_count + 1))
        elif self.radio_current.isChecked():
            page_list = [self.viewer.current_page_index + 1]
        elif self.radio_range.isChecked():
            page_list = self._parse_page_ranges(self.range_input.text())
            if page_list is None: return None

        if not page_list:
            QMessageBox.warning(self, "Nenhuma Página Selecionada", "Você deve selecionar ao menos uma página para imprimir.")
            return None

        orientation = QPageLayout.Orientation.Portrait
        if self.orient_landscape.isChecked():
            orientation = QPageLayout.Orientation.Landscape
        elif self.orient_auto.isChecked():
            page = self.doc.load_page(page_list[0] - 1)
            if page.rect.width > page.rect.height:
                orientation = QPageLayout.Orientation.Landscape

        return {
            "printer_name": self.printer_combo.currentText(),
            "copies": self.copies_spinbox.value(),
            "color_mode": QPrinter.ColorMode.GrayScale if self.grayscale_check.isChecked() else QPrinter.ColorMode.Color,
            "page_list": page_list,
            "orientation": orientation
        }

    def accept(self):
        if self.get_print_settings() is None:
            return
        super().accept()

def main():
    """Função principal para iniciar a aplicação."""
    logger.info("Iniciando QuantumPDF v8.8...")
    app = QApplication(sys.argv)

    server_name = "QuantumPDF_SingleInstance_Server_v8.8"
    socket = QLocalSocket()
    socket.connectToServer(server_name)

    if socket.waitForConnected(500):
        logger.info("Instância existente do QuantumPDF encontrada.")
        if len(sys.argv) > 1:
            file_path = sys.argv[1]
            logger.info(f"Enviando caminho do arquivo '{file_path}' para a instância existente.")
            file_path_bytes = file_path.encode('utf-8')
            socket.write(file_path_bytes)
            socket.flush()
            socket.waitForBytesWritten()
        socket.disconnectFromServer()
        logger.info("Saindo da nova instância.")
        sys.exit(0)

    else:
        logger.info("Nenhuma instância existente encontrada. Iniciando novo servidor.")
        window = MainWindow()

        server = QLocalServer(window)
        if not server.listen(server_name):
             logger.critical(f"Não foi possível iniciar o servidor local: {server.errorString()}")
             sys.exit(1)

        def handle_new_connection():
            logger.info("Nova conexão recebida pela instância principal.")
            new_socket = server.nextPendingConnection()
            if new_socket:
                if new_socket.waitForReadyRead(1000):
                    file_path = new_socket.readAll().data().decode('utf-8')
                    logger.info(f"Recebido caminho de arquivo da nova instância: {file_path}")
                    if os.path.exists(file_path):
                        window._add_new_tab(file_path)
                    else:
                        logger.error(f"Arquivo '{file_path}' não encontrado.")
                    new_socket.disconnectFromServer()
                else:
                    logger.warning("Timeout ao esperar dados do socket.")

            logger.info("Trazendo a janela principal para primeiro plano.")
            window.setWindowState(window.windowState() & ~Qt.WindowState.WindowMinimized | Qt.WindowState.WindowActive)
            window.show()
            window.activateWindow()
            window.raise_()

        server.newConnection.connect(handle_new_connection)

        if len(sys.argv) > 1:
            file_path = sys.argv[1]
            if os.path.exists(file_path):
                window._add_new_tab(file_path)
            else:
                logger.error(f"Arquivo '{file_path}' passado como argumento não foi encontrado.")

        window.show()
        logger.info("Loop de eventos da aplicação iniciado.")
        sys.exit(app.exec())

if __name__ == "__main__":
    try:
        main()
    except Exception:
        logger.critical("Uma exceção fatal ocorreu na função main:", exc_info=True)
        sys.exit(1)
