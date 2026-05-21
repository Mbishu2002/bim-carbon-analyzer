from pathlib import Path

import pandas as pd
from PySide6.QtCore import QSize, Qt, QSettings, QThread, Signal
from PySide6.QtWidgets import (
    QAbstractItemView,
    QButtonGroup,
    QComboBox,
    QFileDialog,
    QFrame,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QMainWindow,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QSizePolicy,
    QSpacerItem,
    QStackedWidget,
    QStatusBar,
    QTableWidget,
    QTableWidgetItem,
    QToolButton,
    QVBoxLayout,
    QWidget,
)

try:
    import qtawesome as qta  # MDI / Font Awesome icon library
    _HAS_QTA = True
except ImportError:
    qta = None
    _HAS_QTA = False

from src.core import BIMMasterExtractor, CarbonCalculator, IFCImporter
from src.core.paths import app_data_dir, resource_path
from src.ui import theme
from src.ui.chart_widgets import ChartPanel


OUTPUT_DIR = app_data_dir() / "output"
SAMPLES_DIR = resource_path("data/samples")

PAGE_HOME, PAGE_MAPPING, PAGE_CHARTS, PAGE_TABLE, PAGE_EXPORT = range(5)


# -------------------------------------------------
# WORKER
# -------------------------------------------------
class PipelineWorker(QThread):
    progress = Signal(int, str)
    finished_ok = Signal(object)
    failed = Signal(str)

    def __init__(self, ifc_path: str):
        super().__init__()
        self.ifc_path = ifc_path

    def run(self):
        try:
            self.progress.emit(5, "Loading IFC...")
            model = IFCImporter(self.ifc_path).run()
            self.progress.emit(15, "Extracting building elements...")
            extractor = BIMMasterExtractor(model)
            extractor.extract.__doc__  # touch attr to satisfy lint
            df = extractor.extract(
                progress_cb=lambda p: self.progress.emit(
                    15 + int(p * 0.83), "Extracting geometry..."
                )
            )
            self.progress.emit(100, "Extraction complete")
            self.finished_ok.emit(df)
        except Exception as e:
            self.failed.emit(str(e))


# -------------------------------------------------
# REUSABLE WIDGETS
# -------------------------------------------------
class KpiCard(QFrame):
    def __init__(self, label: str, accent: bool = False, parent=None):
        super().__init__(parent)
        self.setObjectName("KpiCard")
        lay = QVBoxLayout(self)
        lay.setContentsMargins(16, 12, 16, 12)
        lay.setSpacing(2)
        self.lbl = QLabel(label.upper())
        self.lbl.setObjectName("KpiLabel")
        self.val = QLabel("-")
        self.val.setObjectName("KpiValueAccent" if accent else "KpiValue")
        lay.addWidget(self.lbl)
        lay.addWidget(self.val)

    def set_value(self, text: str):
        self.val.setText(text)


class ActivityButton(QToolButton):
    """Sidebar nav item: icon stacked above its label, VS Code style."""

    def __init__(self, label: str, icon_name: str | None = None, parent=None):
        super().__init__(parent)
        self.setObjectName("ActivityButton")
        self.setText(label)
        self.setCheckable(True)
        self.setAutoExclusive(False)
        self.setCursor(Qt.PointingHandCursor)
        self.setFixedHeight(68)
        self.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
        self.setIconSize(QSize(22, 22))
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self._icon_name = icon_name
        self._apply_icon(active=False)

    def _apply_icon(self, active: bool):
        if not _HAS_QTA or not self._icon_name:
            return
        color = theme.TEXT if active else theme.TEXT_MUTED
        try:
            self.setIcon(qta.icon(self._icon_name, color=color))
        except Exception:
            # Unknown icon name - silently fall back to text only.
            pass

    def setChecked(self, on: bool):
        super().setChecked(on)
        self._apply_icon(active=on)


class DropZone(QFrame):
    """Dashed-border drop target that emits the path of a dropped .ifc file."""

    file_dropped = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("DropZone")
        self.setAcceptDrops(True)
        self.setMinimumHeight(170)

    @staticmethod
    def _ifc_paths(md) -> list[str]:
        if not md.hasUrls():
            return []
        return [
            u.toLocalFile() for u in md.urls()
            if u.toLocalFile().lower().endswith(".ifc")
        ]

    def _set_active(self, on: bool):
        self.setProperty("active", "true" if on else "false")
        self.style().unpolish(self)
        self.style().polish(self)

    def dragEnterEvent(self, e):
        if self._ifc_paths(e.mimeData()):
            e.acceptProposedAction()
            self._set_active(True)

    def dragLeaveEvent(self, e):
        self._set_active(False)

    def dropEvent(self, e):
        self._set_active(False)
        paths = self._ifc_paths(e.mimeData())
        if paths:
            self.file_dropped.emit(paths[0])
            e.acceptProposedAction()


# -------------------------------------------------
# MAIN WINDOW
# -------------------------------------------------
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("BIM Embodied Carbon Analyzer  -  Cameroon")
        self.resize(1360, 860)
        self.setStyleSheet(theme.STYLESHEET)
        theme.apply_mpl_theme()

        # State
        self.df_raw: pd.DataFrame = pd.DataFrame()
        self.df: pd.DataFrame = pd.DataFrame()
        self.current_path: str | None = None
        self.worker: PipelineWorker | None = None
        self.settings = QSettings("BIMCarbon", "Analyzer")
        self.calculator = CarbonCalculator()
        self.lca_choices = self.calculator.available_materials()

        self._build_ui()
        self._build_status()
        self._update_chrome()

    # =============================================
    # LAYOUT
    # =============================================
    def _build_ui(self):
        root = QWidget()
        root_l = QHBoxLayout(root)
        root_l.setContentsMargins(0, 0, 0, 0)
        root_l.setSpacing(0)

        # Activity bar (left)
        self.activity_bar = self._build_activity_bar()
        root_l.addWidget(self.activity_bar)

        # Content area (right)
        content = QWidget()
        cl = QVBoxLayout(content)
        cl.setContentsMargins(0, 0, 0, 0)
        cl.setSpacing(0)

        # Top header
        self.header_bar = self._build_header()
        cl.addWidget(self.header_bar)

        # KPI row (visible only after calc)
        self.kpi_strip = self._build_kpi_strip()
        cl.addWidget(self.kpi_strip)

        # Filter row (visible only after calc)
        self.filter_strip = self._build_filter_strip()
        cl.addWidget(self.filter_strip)

        # Stacked pages
        self.pages = QStackedWidget()
        self.pages.addWidget(self._page_home())
        self.pages.addWidget(self._page_mapping())
        self.pages.addWidget(self._page_charts())
        self.pages.addWidget(self._page_table())
        self.pages.addWidget(self._page_export())
        cl.addWidget(self.pages, 1)

        root_l.addWidget(content, 1)
        self.setCentralWidget(root)

    def _build_activity_bar(self) -> QFrame:
        bar = QFrame()
        bar.setObjectName("ActivityBar")
        bar.setFixedWidth(82)
        lay = QVBoxLayout(bar)
        lay.setContentsMargins(0, 8, 0, 8)
        lay.setSpacing(2)

        self.act_buttons = QButtonGroup(self)
        self.act_buttons.setExclusive(True)

        entries = [
            ("Home",    "mdi6.home-outline"),
            ("Mapping", "mdi6.swap-horizontal-bold"),
            ("Charts",  "mdi6.chart-donut"),
            ("Table",   "mdi6.table-large"),
            ("Export",  "mdi6.download-outline"),
        ]
        for idx, (label, icon_name) in enumerate(entries):
            btn = ActivityButton(label, icon_name)
            btn.clicked.connect(lambda _=False, i=idx: self.switch_page(i))
            self.act_buttons.addButton(btn, idx)
            lay.addWidget(btn)

        self.act_buttons.button(PAGE_HOME).setChecked(True)
        lay.addStretch(1)
        return bar

    def _build_header(self) -> QFrame:
        h = QFrame()
        h.setObjectName("HeaderBar")
        h.setFixedHeight(58)
        lay = QHBoxLayout(h)
        lay.setContentsMargins(24, 8, 24, 8)

        col = QVBoxLayout()
        col.setSpacing(0)
        self.header_title = QLabel("Home")
        self.header_title.setObjectName("HeaderTitle")
        self.header_subtitle = QLabel("No model loaded")
        self.header_subtitle.setObjectName("HeaderSubtitle")
        col.addWidget(self.header_title)
        col.addWidget(self.header_subtitle)
        lay.addLayout(col)
        lay.addStretch(1)

        self.header_open_btn = QPushButton("Open IFC...")
        self.header_open_btn.setObjectName("PrimaryButton")
        self.header_open_btn.clicked.connect(self.on_open)
        lay.addWidget(self.header_open_btn)
        return h

    def _build_kpi_strip(self) -> QWidget:
        w = QWidget()
        lay = QHBoxLayout(w)
        lay.setContentsMargins(24, 16, 24, 0)
        lay.setSpacing(12)

        self.kpi_elements = KpiCard("Elements")
        self.kpi_volume = KpiCard("Volume (m3)")
        self.kpi_mass = KpiCard("Mass (t)")
        self.kpi_carbon = KpiCard("Embodied Carbon (tCO2e)", accent=True)
        for c in (self.kpi_elements, self.kpi_volume, self.kpi_mass, self.kpi_carbon):
            lay.addWidget(c, 1)
        return w

    def _build_filter_strip(self) -> QWidget:
        w = QWidget()
        lay = QHBoxLayout(w)
        lay.setContentsMargins(24, 12, 24, 0)
        lay.setSpacing(8)

        for label, attr in (("Category", "cb_category"),
                            ("Storey", "cb_storey"),
                            ("Material", "cb_material")):
            l = QLabel(label)
            l.setStyleSheet(f"color: {theme.TEXT_MUTED};")
            lay.addWidget(l)
            cb = QComboBox()
            cb.setMinimumWidth(160)
            cb.currentTextChanged.connect(self.refresh_view)
            setattr(self, attr, cb)
            lay.addWidget(cb)

        self.btn_reset_filters = QPushButton("Reset filters")
        self.btn_reset_filters.clicked.connect(self.reset_filters)
        lay.addWidget(self.btn_reset_filters)
        lay.addStretch(1)
        return w

    # =============================================
    # PAGES
    # =============================================
    def _page_home(self) -> QWidget:
        page = QWidget()
        outer = QVBoxLayout(page)
        outer.setContentsMargins(0, 0, 0, 0)

        # Constrain content width so it looks intentional on wide windows.
        wrap = QWidget()
        wrap.setMaximumWidth(1100)
        lay = QVBoxLayout(wrap)
        lay.setContentsMargins(56, 36, 56, 28)
        lay.setSpacing(16)

        # Eyebrow + headline
        eyebrow = QLabel("CAMEROON EDITION")
        eyebrow.setObjectName("Eyebrow")
        lay.addWidget(eyebrow)

        headline = QLabel()
        headline.setObjectName("Headline")
        headline.setTextFormat(Qt.RichText)
        headline.setText(
            f"<span style='color:{theme.TEXT};'>BIM </span>"
            f"<span style='color:{theme.ACCENT};'>Embodied Carbon</span>"
            f"<span style='color:{theme.TEXT};'> Analyzer</span>"
        )
        lay.addWidget(headline)

        tagline = QLabel(
            "Quantify the carbon footprint of any IFC model with locally-sourced "
            "Cameroon material emission factors - hollow concrete block, CEB, "
            "tropical hardwood, in-situ concrete and more."
        )
        tagline.setObjectName("Tagline")
        tagline.setWordWrap(True)
        lay.addWidget(tagline)

        lay.addItem(QSpacerItem(0, 12, QSizePolicy.Minimum, QSizePolicy.Fixed))

        # Drop zone
        self.drop_zone = DropZone()
        self.drop_zone.file_dropped.connect(self.start_pipeline)
        dz_lay = QVBoxLayout(self.drop_zone)
        dz_lay.setContentsMargins(28, 28, 28, 28)
        dz_lay.setSpacing(10)

        drop_title = QLabel("Drop an IFC model here")
        drop_title.setObjectName("DropTitle")
        drop_title.setAlignment(Qt.AlignCenter)

        drop_hint = QLabel("or use the buttons below to browse")
        drop_hint.setObjectName("DropHint")
        drop_hint.setAlignment(Qt.AlignCenter)

        btn_row = QHBoxLayout()
        btn_row.setSpacing(10)
        btn_row.addStretch(1)
        browse = QPushButton("Browse for file...")
        browse.setObjectName("PrimaryButton")
        browse.setMinimumHeight(40)
        browse.setMinimumWidth(170)
        browse.clicked.connect(self.on_open)
        btn_row.addWidget(browse)

        sample = QPushButton("Try a bundled sample")
        sample.setMinimumHeight(40)
        sample.setMinimumWidth(170)
        sample.clicked.connect(self.on_load_sample)
        btn_row.addWidget(sample)
        btn_row.addStretch(1)

        dz_lay.addWidget(drop_title)
        dz_lay.addWidget(drop_hint)
        dz_lay.addLayout(btn_row)
        lay.addWidget(self.drop_zone)

        lay.addItem(QSpacerItem(0, 16, QSizePolicy.Minimum, QSizePolicy.Fixed))

        # Section label
        sect = QLabel("WHAT YOU GET")
        sect.setObjectName("SectionLabel")
        lay.addWidget(sect)

        # Feature cards
        cards_row = QHBoxLayout()
        cards_row.setSpacing(12)
        cards_row.addWidget(self._feature_card(
            "01",
            "Extract everything",
            "Walls, slabs, beams, columns, footings, roofs, stairs, doors and "
            "windows - every IfcBuildingElement with geometry, material and "
            "storey context.",
        ), 1)
        cards_row.addWidget(self._feature_card(
            "02",
            "Map to Cameroon LCA",
            "Confirm or override the auto-suggested local material per IFC "
            "entry: hollow concrete block, CEB, in-situ concrete, tropical "
            "hardwood, imported steel and more.",
        ), 1)
        cards_row.addWidget(self._feature_card(
            "03",
            "Visualise & export",
            "Interactive donut, bar and table views with storey, category and "
            "material filters. Export the per-element dataset to Excel or CSV.",
        ), 1)
        lay.addLayout(cards_row)
        lay.addStretch(1)

        # Centre the wrap both horizontally and vertically
        h_centre = QHBoxLayout()
        h_centre.setContentsMargins(0, 0, 0, 0)
        h_centre.addStretch(1)
        h_centre.addWidget(wrap)
        h_centre.addStretch(1)

        outer.addStretch(1)
        outer.addLayout(h_centre)
        outer.addStretch(1)
        return page

    def _feature_card(self, number: str, title: str, body: str) -> QFrame:
        card = QFrame()
        card.setObjectName("FeatureCard")
        l = QVBoxLayout(card)
        l.setContentsMargins(22, 20, 22, 20)
        l.setSpacing(8)

        num = QLabel(number)
        num.setObjectName("FeatureNumber")
        t = QLabel(title)
        t.setObjectName("FeatureTitle")
        b = QLabel(body)
        b.setObjectName("FeatureBody")
        b.setWordWrap(True)

        l.addWidget(num)
        l.addWidget(t)
        l.addWidget(b)
        l.addStretch(1)
        return card

    def _page_mapping(self) -> QWidget:
        page = QWidget()
        lay = QVBoxLayout(page)
        lay.setContentsMargins(24, 16, 24, 16)
        lay.setSpacing(12)

        intro = QLabel(
            "Each row is a unique material extracted from the IFC. The "
            "auto-suggested column shows the best Cameroon LCA match; use the "
            "Override dropdown to change it (for example: pick "
            "<b>Compressed Earth Block</b> where the model says generic "
            "masonry). Press <b>Calculate carbon</b> when ready."
        )
        intro.setWordWrap(True)
        intro.setStyleSheet(f"color: {theme.TEXT_MUTED};")
        lay.addWidget(intro)

        self.mapping_table = QTableWidget()
        self.mapping_table.setColumnCount(5)
        self.mapping_table.setHorizontalHeaderLabels(
            ["IFC Material", "Elements", "Volume (m3)", "Auto-suggested", "Override (used)"]
        )
        self.mapping_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.mapping_table.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)
        self.mapping_table.verticalHeader().setVisible(False)
        self.mapping_table.setAlternatingRowColors(True)
        lay.addWidget(self.mapping_table, 1)

        btn_row = QHBoxLayout()
        self.btn_calc = QPushButton("Calculate carbon")
        self.btn_calc.setObjectName("PrimaryButton")
        self.btn_calc.setMinimumHeight(40)
        self.btn_calc.clicked.connect(self.on_calculate)
        self.btn_calc.setEnabled(False)

        self.btn_auto = QPushButton("Reset to auto-suggested")
        self.btn_auto.clicked.connect(self.reset_mapping)
        self.btn_auto.setEnabled(False)

        btn_row.addWidget(self.btn_calc)
        btn_row.addWidget(self.btn_auto)
        btn_row.addStretch(1)
        lay.addLayout(btn_row)
        return page

    def _page_charts(self) -> QWidget:
        page = QWidget()
        lay = QVBoxLayout(page)
        lay.setContentsMargins(24, 16, 24, 16)
        lay.setSpacing(12)

        row1 = QHBoxLayout()
        self.chart_category = ChartPanel(default_type="Bar")
        self.chart_storey = ChartPanel(default_type="Bar")
        row1.addWidget(self.chart_category)
        row1.addWidget(self.chart_storey)
        lay.addLayout(row1, 1)

        row2 = QHBoxLayout()
        self.chart_material = ChartPanel(default_type="Horizontal bar")
        self.chart_pie = ChartPanel(default_type="Donut")
        row2.addWidget(self.chart_material)
        row2.addWidget(self.chart_pie)
        lay.addLayout(row2, 1)
        return page

    def _page_table(self) -> QWidget:
        page = QWidget()
        lay = QVBoxLayout(page)
        lay.setContentsMargins(24, 16, 24, 16)

        self.table = QTableWidget()
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setAlternatingRowColors(True)
        self.table.verticalHeader().setVisible(False)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)
        lay.addWidget(self.table)
        return page

    def _page_export(self) -> QWidget:
        page = QWidget()
        lay = QVBoxLayout(page)
        lay.setContentsMargins(48, 36, 48, 36)
        lay.setSpacing(16)

        title = QLabel("Export")
        title.setObjectName("PageTitle")
        sub = QLabel(
            "Save the calculated dataset. You choose the destination in the "
            "Save dialog; the folder is remembered for next time."
        )
        sub.setObjectName("PageSubtitle")
        sub.setWordWrap(True)
        lay.addWidget(title)
        lay.addWidget(sub)

        cards = QHBoxLayout()
        cards.setSpacing(12)

        cards.addWidget(self._export_card(
            "Excel workbook",
            "Two sheets: MASTER_TABLE (every element) and CARBON_SUMMARY "
            "(grouped by Category x Material).",
            "Save Excel as...",
            lambda: self.on_export("xlsx"),
        ), 1)

        cards.addWidget(self._export_card(
            "CSV file",
            "Single flat file with one row per element including the embodied "
            "carbon column.",
            "Save CSV as...",
            lambda: self.on_export("csv"),
        ), 1)
        lay.addLayout(cards)

        # Default folder card
        folder_card = QFrame()
        folder_card.setObjectName("KpiCard")
        fl = QVBoxLayout(folder_card)
        fl.setContentsMargins(20, 16, 20, 16)
        ft = QLabel("Default save folder")
        ft.setStyleSheet(f"color:{theme.TEXT}; font-weight:600;")
        self.lbl_default_folder = QLabel(str(self._default_save_dir()))
        self.lbl_default_folder.setStyleSheet(f"color:{theme.TEXT_MUTED};")
        self.lbl_default_folder.setWordWrap(True)
        change_btn = QPushButton("Change folder...")
        change_btn.clicked.connect(self.on_set_default_folder)
        fl.addWidget(ft)
        fl.addWidget(self.lbl_default_folder)
        fl.addSpacing(6)
        fl.addWidget(change_btn, 0, Qt.AlignLeft)
        lay.addWidget(folder_card)

        lay.addStretch(1)
        return page

    def _export_card(self, title, body, btn_text, on_click) -> QFrame:
        card = QFrame()
        card.setObjectName("KpiCard")
        l = QVBoxLayout(card)
        l.setContentsMargins(20, 18, 20, 18)
        l.setSpacing(6)

        t = QLabel(title)
        t.setStyleSheet(f"color:{theme.TEXT}; font-weight:600; font-size:14px;")
        b = QLabel(body)
        b.setStyleSheet(f"color:{theme.TEXT_MUTED};")
        b.setWordWrap(True)
        btn = QPushButton(btn_text)
        btn.setObjectName("PrimaryButton")
        btn.clicked.connect(on_click)

        l.addWidget(t)
        l.addWidget(b)
        l.addStretch(1)
        l.addWidget(btn, 0, Qt.AlignLeft)
        return card

    def _build_status(self):
        sb = QStatusBar()
        self.setStatusBar(sb)
        self.progress = QProgressBar()
        self.progress.setMaximumWidth(220)
        self.progress.setTextVisible(False)
        self.progress.setVisible(False)
        sb.addPermanentWidget(self.progress)
        self.status_msg = QLabel("Ready")
        sb.addWidget(self.status_msg, 1)

    # =============================================
    # NAVIGATION
    # =============================================
    def switch_page(self, idx: int):
        self.pages.setCurrentIndex(idx)
        if not self.act_buttons.button(idx).isChecked():
            self.act_buttons.button(idx).setChecked(True)
        self._update_chrome()

    def _update_chrome(self):
        idx = self.pages.currentIndex()
        titles = {
            PAGE_HOME: "Home",
            PAGE_MAPPING: "Material mapping",
            PAGE_CHARTS: "Charts",
            PAGE_TABLE: "Element table",
            PAGE_EXPORT: "Export",
        }
        self.header_title.setText(titles.get(idx, ""))

        file_part = (
            f"{Path(self.current_path).name}  ·  {len(self.df_raw):,} elements"
            if self.current_path else "No model loaded"
        )
        self.header_subtitle.setText(file_part)

        # Strip chrome on the welcome screen when there's no data yet so the
        # hero is the entire focus.
        on_blank_home = (idx == PAGE_HOME) and self.df_raw.empty
        self.activity_bar.setVisible(not on_blank_home)
        self.header_bar.setVisible(not on_blank_home)

        has_calc = not self.df.empty
        self.kpi_strip.setVisible(has_calc and idx in (PAGE_CHARTS, PAGE_TABLE))
        self.filter_strip.setVisible(has_calc and idx in (PAGE_CHARTS, PAGE_TABLE))
        self.header_open_btn.setVisible(idx != PAGE_HOME)

    # =============================================
    # ACTIONS
    # =============================================
    def on_open(self):
        start_dir = str(SAMPLES_DIR) if SAMPLES_DIR.exists() else str(PROJECT_ROOT)
        path, _ = QFileDialog.getOpenFileName(
            self, "Open IFC model", start_dir, "IFC files (*.ifc);;All files (*.*)"
        )
        if path:
            self.start_pipeline(path)

    def on_load_sample(self):
        if not SAMPLES_DIR.exists():
            QMessageBox.information(self, "No samples", "No bundled samples found.")
            return
        candidates = list(SAMPLES_DIR.glob("*.ifc"))
        if not candidates:
            QMessageBox.information(self, "No samples", "No IFC samples found.")
            return
        self.start_pipeline(str(candidates[0]))

    def start_pipeline(self, path: str):
        self.current_path = path
        self.progress.setVisible(True)
        self.progress.setRange(0, 100)
        self.progress.setValue(0)
        self.status_msg.setText(f"Loading {Path(path).name}...")
        self._update_chrome()

        self.worker = PipelineWorker(path)
        self.worker.progress.connect(self.on_progress)
        self.worker.finished_ok.connect(self.on_pipeline_done)
        self.worker.failed.connect(self.on_pipeline_failed)
        self.worker.start()

    def on_progress(self, pct: int, msg: str):
        self.progress.setValue(pct)
        self.status_msg.setText(msg)

    def on_pipeline_failed(self, msg: str):
        self.progress.setVisible(False)
        self.status_msg.setText("Failed")
        QMessageBox.critical(self, "Pipeline error", msg)

    def on_pipeline_done(self, df: pd.DataFrame):
        self.progress.setVisible(False)
        self.df_raw = df
        self.df = pd.DataFrame()
        self.populate_mapping_table()
        self.populate_filters()
        self.refresh_view()
        self.btn_calc.setEnabled(not df.empty)
        self.btn_auto.setEnabled(not df.empty)
        self.switch_page(PAGE_MAPPING)
        self.status_msg.setText(
            f"Extracted {len(df)} elements - review the mapping, then "
            f"click 'Calculate carbon'."
        )

    # ---------- filters ----------
    def populate_filters(self):
        for cb, col in (
            (self.cb_category, "Category"),
            (self.cb_storey, "Storey"),
            (self.cb_material, "Material"),
        ):
            cb.blockSignals(True)
            cb.clear()
            cb.addItem("(All)")
            if not self.df.empty:
                values = sorted(
                    str(v) for v in self.df[col].dropna().unique().tolist()
                )
                cb.addItems(values)
            cb.blockSignals(False)

    def reset_filters(self):
        for cb in (self.cb_category, self.cb_storey, self.cb_material):
            cb.blockSignals(True)
            cb.setCurrentIndex(0)
            cb.blockSignals(False)
        self.refresh_view()

    def filtered_df(self) -> pd.DataFrame:
        if self.df.empty:
            return self.df
        d = self.df
        for cb, col in (
            (self.cb_category, "Category"),
            (self.cb_storey, "Storey"),
            (self.cb_material, "Material"),
        ):
            val = cb.currentText()
            if val and val != "(All)":
                d = d[d[col].astype(str) == val]
        return d

    # ---------- rendering ----------
    def refresh_view(self):
        d = self.filtered_df()
        self._refresh_kpis(d)
        self._refresh_charts(d)
        self._refresh_table(d)

    def _refresh_kpis(self, d: pd.DataFrame):
        if d.empty:
            for c in (self.kpi_elements, self.kpi_volume, self.kpi_mass, self.kpi_carbon):
                c.set_value("-")
            return
        vol = pd.to_numeric(d["Volume_m3"], errors="coerce").sum(skipna=True)
        mass = pd.to_numeric(d.get("Mass_kg", 0), errors="coerce").sum(skipna=True)
        carb = pd.to_numeric(d.get("EmbodiedCarbon_kgCO2e", 0), errors="coerce").sum(skipna=True)
        self.kpi_elements.set_value(f"{len(d):,}")
        self.kpi_volume.set_value(f"{vol:,.1f}")
        self.kpi_mass.set_value(f"{mass/1000:,.2f}")
        self.kpi_carbon.set_value(f"{carb/1000:,.2f}")

    def _refresh_charts(self, d: pd.DataFrame):
        by_cat = CarbonCalculator.totals_by(d, ["Category"])
        self.chart_category.set_data(
            by_cat, "Category", "EmbodiedCarbon_kgCO2e",
            "Embodied carbon by category",
        )

        by_st = CarbonCalculator.totals_by(d, ["Storey"])
        self.chart_storey.set_data(
            by_st, "Storey", "EmbodiedCarbon_kgCO2e",
            "Embodied carbon by storey",
        )

        mcol = "Mapped_Material" if not d.empty and "Mapped_Material" in d.columns else "Material"
        by_mat = CarbonCalculator.totals_by(d, [mcol])
        self.chart_material.set_data(
            by_mat, mcol, "EmbodiedCarbon_kgCO2e",
            "Top materials (kgCO2e)",
        )
        self.chart_pie.set_data(
            by_mat, mcol, "EmbodiedCarbon_kgCO2e",
            "Material share of total carbon",
        )

    def _refresh_table(self, d: pd.DataFrame):
        cols = [
            "GUID", "Name", "Element_Type", "Category", "Storey", "Material",
            "Mapped_Material", "Quantity", "Unit", "Volume_m3", "Area_m2",
            "EC_factor_kgCO2e_per_m3", "Mass_kg", "EmbodiedCarbon_kgCO2e",
        ]
        cols = [c for c in cols if c in d.columns]
        self.table.clear()
        self.table.setColumnCount(len(cols))
        self.table.setHorizontalHeaderLabels(cols)
        self.table.setRowCount(len(d))

        for r, (_, row) in enumerate(d.iterrows()):
            for c, col in enumerate(cols):
                v = row[col]
                if isinstance(v, float):
                    text = f"{v:,.3f}" if not pd.isna(v) else ""
                else:
                    text = "" if pd.isna(v) else str(v)
                item = QTableWidgetItem(text)
                if isinstance(v, (int, float)) and not pd.isna(v):
                    item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                self.table.setItem(r, c, item)
        self.table.resizeColumnsToContents()

    # ---------- mapping ----------
    def populate_mapping_table(self):
        df = self.df_raw
        self.mapping_table.setRowCount(0)
        if df.empty:
            return

        summary = (
            df.assign(_v=pd.to_numeric(df["Volume_m3"], errors="coerce"))
            .groupby("Material", dropna=False)
            .agg(elements=("GUID", "count"), volume=("_v", "sum"))
            .reset_index()
            .sort_values("volume", ascending=False)
        )

        self.mapping_table.setRowCount(len(summary))
        for r, row in enumerate(summary.itertuples(index=False)):
            ifc_mat = "(unspecified)" if pd.isna(row.Material) else str(row.Material)
            suggested = self.calculator.suggest(ifc_mat)

            item_mat = QTableWidgetItem(ifc_mat)
            item_mat.setToolTip(ifc_mat)
            self.mapping_table.setItem(r, 0, item_mat)

            item_cnt = QTableWidgetItem(f"{int(row.elements):,}")
            item_cnt.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.mapping_table.setItem(r, 1, item_cnt)

            vol = 0.0 if pd.isna(row.volume) else float(row.volume)
            item_vol = QTableWidgetItem(f"{vol:,.2f}")
            item_vol.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.mapping_table.setItem(r, 2, item_vol)

            item_sug = QTableWidgetItem(suggested)
            item_sug.setForeground(Qt.gray)
            self.mapping_table.setItem(r, 3, item_sug)

            combo = QComboBox()
            combo.addItems(self.lca_choices)
            combo.setCurrentText(suggested)
            combo.setToolTip(
                "Pick the Cameroon LCA material this IFC material represents"
            )
            self.mapping_table.setCellWidget(r, 4, combo)
        self.mapping_table.resizeColumnsToContents()

    def reset_mapping(self):
        for r in range(self.mapping_table.rowCount()):
            suggested_item = self.mapping_table.item(r, 3)
            combo = self.mapping_table.cellWidget(r, 4)
            if suggested_item and isinstance(combo, QComboBox):
                combo.setCurrentText(suggested_item.text())

    def current_material_map(self) -> dict[str, str]:
        m: dict[str, str] = {}
        for r in range(self.mapping_table.rowCount()):
            ifc_item = self.mapping_table.item(r, 0)
            combo = self.mapping_table.cellWidget(r, 4)
            if ifc_item is None or not isinstance(combo, QComboBox):
                continue
            ifc_mat = ifc_item.text()
            if ifc_mat == "(unspecified)":
                continue
            m[ifc_mat] = combo.currentText()
        return m

    def on_calculate(self):
        if self.df_raw.empty:
            return
        mapping = self.current_material_map()
        self.df = self.calculator.calculate(self.df_raw, material_map=mapping)
        self.populate_filters()
        self.refresh_view()
        self.switch_page(PAGE_CHARTS)
        carb = pd.to_numeric(self.df["EmbodiedCarbon_kgCO2e"], errors="coerce").sum(skipna=True)
        self.status_msg.setText(
            f"Calculated: {len(self.df)} elements - "
            f"{carb/1000:,.2f} tCO2e using {len(mapping)} mapped materials."
        )

    # ---------- export ----------
    def _default_save_dir(self) -> Path:
        saved = self.settings.value("export/default_dir", "", type=str)
        if saved and Path(saved).exists():
            return Path(saved)
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        return OUTPUT_DIR

    def on_set_default_folder(self):
        start = str(self._default_save_dir())
        chosen = QFileDialog.getExistingDirectory(self, "Choose default export folder", start)
        if chosen:
            self.settings.setValue("export/default_dir", chosen)
            if hasattr(self, "lbl_default_folder"):
                self.lbl_default_folder.setText(chosen)
            self.status_msg.setText(f"Default export folder: {chosen}")

    def on_export(self, kind: str):
        d = self.filtered_df()
        if d.empty:
            QMessageBox.information(
                self, "Nothing to export",
                "Load a model and click 'Calculate carbon' first.",
            )
            return

        stem = Path(self.current_path).stem if self.current_path else "carbon"
        start_dir = self._default_save_dir()

        if kind == "csv":
            default = start_dir / f"{stem}_carbon.csv"
            path, _ = QFileDialog.getSaveFileName(
                self, "Save CSV as...", str(default), "CSV files (*.csv)"
            )
            if not path:
                return
            d.to_csv(path, index=False)
        else:
            default = start_dir / f"{stem}_carbon.xlsx"
            path, _ = QFileDialog.getSaveFileName(
                self, "Save Excel workbook as...", str(default),
                "Excel workbook (*.xlsx)",
            )
            if not path:
                return
            with pd.ExcelWriter(path, engine="openpyxl") as writer:
                d.to_excel(writer, sheet_name="MASTER_TABLE", index=False)
                (
                    d.groupby(["Category", "Material", "Unit"], dropna=False)
                    .agg(
                        Quantity=("Quantity", "sum"),
                        Volume_m3=("Volume_m3", "sum"),
                        EmbodiedCarbon_kgCO2e=("EmbodiedCarbon_kgCO2e", "sum"),
                    )
                    .reset_index()
                    .to_excel(writer, sheet_name="CARBON_SUMMARY", index=False)
                )

        self.settings.setValue("export/default_dir", str(Path(path).parent))
        if hasattr(self, "lbl_default_folder"):
            self.lbl_default_folder.setText(str(Path(path).parent))
        self.status_msg.setText(f"Saved to {path}")
        QMessageBox.information(self, "Saved", f"File saved to:\n{path}")
