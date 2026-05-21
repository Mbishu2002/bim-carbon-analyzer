import pandas as pd
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QComboBox, QHBoxLayout, QLabel, QVBoxLayout, QWidget

from src.ui import theme


class MplCanvas(FigureCanvasQTAgg):
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi, tight_layout=True)
        self.fig.patch.set_facecolor(theme.BG)
        self.ax = self.fig.add_subplot(111)
        super().__init__(self.fig)
        self.setParent(parent)


class ChartPanel(QWidget):
    """Self-contained chart card: title in a header, a chart-type dropdown
    so the user can switch between Bar / Horizontal Bar / Donut, and the
    matplotlib canvas below."""

    CHART_TYPES = ["Bar", "Horizontal bar", "Donut"]

    def __init__(self, default_type: str = "Bar", parent=None):
        super().__init__(parent)
        self.canvas = MplCanvas(self)

        # Header
        header = QWidget()
        hl = QHBoxLayout(header)
        hl.setContentsMargins(2, 2, 2, 0)
        hl.setSpacing(8)
        self._title_lbl = QLabel("")
        self._title_lbl.setStyleSheet(
            f"color:{theme.TEXT}; font-weight:600; font-size:13px;"
        )
        hl.addWidget(self._title_lbl)
        hl.addStretch(1)

        chart_lbl = QLabel("Type:")
        chart_lbl.setStyleSheet(f"color:{theme.TEXT_MUTED}; font-size:11px;")
        hl.addWidget(chart_lbl)

        self.type_combo = QComboBox()
        self.type_combo.addItems(self.CHART_TYPES)
        if default_type in self.CHART_TYPES:
            self.type_combo.setCurrentText(default_type)
        self.type_combo.setFixedWidth(140)
        self.type_combo.currentTextChanged.connect(self._redraw)
        hl.addWidget(self.type_combo)

        # Layout
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(4)
        outer.addWidget(header)
        outer.addWidget(self.canvas, 1)
        self.setStyleSheet(f"background-color: {theme.BG};")

        # Stored dataset (set_data + chart-type combo drive redraws)
        self._df: pd.DataFrame | None = None
        self._label_col: str = ""
        self._value_col: str = ""
        self._title: str = ""
        self._units: str = "kgCO2e"

    # =============================================
    # PUBLIC API
    # =============================================
    def set_data(self, df, label_col: str, value_col: str,
                 title: str, units: str = "kgCO2e",
                 default_type: str | None = None):
        self._df = df
        self._label_col = label_col
        self._value_col = value_col
        self._title = title
        self._units = units
        self._title_lbl.setText(title)
        if default_type and default_type in self.CHART_TYPES:
            self.type_combo.blockSignals(True)
            self.type_combo.setCurrentText(default_type)
            self.type_combo.blockSignals(False)
        self._redraw()

    # =============================================
    # INTERNAL DRAW DISPATCH
    # =============================================
    def _redraw(self):
        if self._df is None:
            return
        kind = self.type_combo.currentText()
        if kind == "Bar":
            self._draw_bar()
        elif kind == "Horizontal bar":
            self._draw_hbar()
        elif kind == "Donut":
            self._draw_donut()

    def _reset_axes(self):
        self.canvas.fig.clear()
        self.canvas.ax = self.canvas.fig.add_subplot(111)

    def _empty(self):
        self.canvas.ax.text(
            0.5, 0.5, "No data",
            ha="center", va="center",
            color=theme.TEXT_DIM,
            transform=self.canvas.ax.transAxes,
            fontsize=11,
        )
        self.canvas.ax.set_xticks([])
        self.canvas.ax.set_yticks([])
        for s in self.canvas.ax.spines.values():
            s.set_visible(False)
        self.canvas.draw_idle()

    # ---------- BAR ----------
    def _draw_bar(self):
        self._reset_axes()
        df = self._df
        if df.empty:
            self._empty()
            return

        labels = df[self._label_col].astype(str).tolist()
        values = df[self._value_col].fillna(0).tolist()
        colors = [theme.CHART_CYCLE[i % len(theme.CHART_CYCLE)] for i in range(len(values))]

        bars = self.canvas.ax.bar(labels, values, color=colors, edgecolor="none")
        self.canvas.ax.set_ylabel(self._units, color=theme.TEXT_MUTED)
        self.canvas.ax.tick_params(axis="x", rotation=30, colors=theme.TEXT_MUTED)
        self.canvas.ax.tick_params(axis="y", colors=theme.TEXT_MUTED)

        ymax = max(values) if values else 0
        offset = ymax * 0.02 if ymax else 0
        for b, v in zip(bars, values):
            self.canvas.ax.text(
                b.get_x() + b.get_width() / 2,
                b.get_height() + offset,
                self._fmt(v),
                ha="center", va="bottom",
                fontsize=8, color=theme.TEXT,
            )
        for tick in self.canvas.ax.get_xticklabels():
            tick.set_ha("right")
        self.canvas.fig.tight_layout()
        self.canvas.draw_idle()

    # ---------- HORIZONTAL BAR ----------
    def _draw_hbar(self, top_n: int = 12):
        self._reset_axes()
        df = self._df
        if df.empty:
            self._empty()
            return

        d = (
            df[df[self._value_col] > 0]
            .sort_values(self._value_col, ascending=False)
            .head(top_n)
            .iloc[::-1]
        )
        if d.empty:
            self._empty()
            return

        labels = [self._truncate(str(x), 40) for x in d[self._label_col].tolist()]
        values = d[self._value_col].fillna(0).tolist()
        colors = [theme.CHART_CYCLE[i % len(theme.CHART_CYCLE)] for i in range(len(values))]

        bars = self.canvas.ax.barh(labels, values, color=colors, edgecolor="none")
        self.canvas.ax.set_xlabel(self._units, color=theme.TEXT_MUTED)
        self.canvas.ax.tick_params(axis="x", colors=theme.TEXT_MUTED)
        self.canvas.ax.tick_params(axis="y", colors=theme.TEXT_MUTED)

        xmax = max(values) if values else 0
        for b, v in zip(bars, values):
            self.canvas.ax.text(
                b.get_width() + xmax * 0.01,
                b.get_y() + b.get_height() / 2,
                self._fmt(v),
                va="center", ha="left",
                fontsize=8, color=theme.TEXT,
            )
        self.canvas.fig.tight_layout()
        self.canvas.draw_idle()

    # ---------- DONUT ----------
    def _draw_donut(self, top_n: int = 6):
        self._reset_axes()
        df = self._df
        if df.empty:
            self._empty()
            return

        d = df[df[self._value_col] > 0].sort_values(self._value_col, ascending=False).copy()
        if d.empty:
            self._empty()
            return

        if len(d) > top_n:
            head = d.head(top_n)
            other_val = d.iloc[top_n:][self._value_col].sum()
            if other_val > 0:
                d = pd.concat(
                    [head, pd.DataFrame([{self._label_col: "Other", self._value_col: other_val}])],
                    ignore_index=True,
                )
            else:
                d = head

        labels = d[self._label_col].astype(str).tolist()
        values = d[self._value_col].astype(float).tolist()
        total = sum(values) or 1.0
        colors = [theme.CHART_CYCLE[i % len(theme.CHART_CYCLE)] for i in range(len(values))]

        wedges, _ = self.canvas.ax.pie(
            values,
            startangle=90,
            counterclock=False,
            colors=colors,
            wedgeprops=dict(width=0.42, edgecolor=theme.BG, linewidth=2),
        )
        self.canvas.ax.set_aspect("equal")

        self.canvas.ax.text(
            0, 0.06, self._fmt(total),
            ha="center", va="center",
            color=theme.TEXT, fontsize=15, fontweight="700",
        )
        self.canvas.ax.text(
            0, -0.12, self._units,
            ha="center", va="center",
            color=theme.TEXT_MUTED, fontsize=9,
        )

        legend_labels = [
            f"{self._truncate(lab, 26)}  {(v/total)*100:.1f}%"
            for lab, v in zip(labels, values)
        ]
        legend = self.canvas.ax.legend(
            wedges,
            legend_labels,
            loc="center left",
            bbox_to_anchor=(1.0, 0.5),
            frameon=False,
            fontsize=9,
            labelspacing=0.7,
            handlelength=1.0,
            borderpad=0,
        )
        for txt in legend.get_texts():
            txt.set_color(theme.TEXT)

        self.canvas.fig.subplots_adjust(left=0.02, right=0.62, top=0.92, bottom=0.05)
        self.canvas.draw_idle()

    # =============================================
    # HELPERS
    # =============================================
    @staticmethod
    def _fmt(v):
        if v is None or v != v:
            return ""
        if abs(v) >= 1e6:
            return f"{v/1e6:.1f}M"
        if abs(v) >= 1e3:
            return f"{v/1e3:.1f}k"
        return f"{v:.0f}"

    @staticmethod
    def _truncate(s: str, n: int) -> str:
        return s if len(s) <= n else s[: n - 1] + "..."
