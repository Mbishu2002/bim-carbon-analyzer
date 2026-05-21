"""VS Code-inspired dark theme: palette, Qt stylesheet, and matplotlib
rcParams. Keep colour values in one place so charts and widgets stay in sync.
"""

# -------------------------------------------------
# COLOR PALETTE (VS Code Dark+ inspired)
# -------------------------------------------------
BG = "#1e1e1e"           # editor / main background
BG_PANEL = "#252526"     # side panels, kpi cards
BG_ELEV = "#2d2d30"      # elevated panels, table header
BG_ACTIVE = "#37373d"    # active selection bg
BG_HOVER = "#2a2d2e"     # hover bg
ACTIVITYBAR = "#333333"  # left sidebar bg
BORDER = "#3c3c3c"       # subtle separators
BORDER_STRONG = "#464647"

TEXT = "#cccccc"         # primary text
TEXT_MUTED = "#9d9d9d"   # secondary text
TEXT_DIM = "#7a7a7a"     # tertiary

ACCENT = "#0098ff"       # VS Code accent blue
ACCENT_HOVER = "#1ba1ff"
ACCENT_SUBTLE = "#094771"

OK = "#4ec9b0"           # mint - good values
WARN = "#dcdcaa"         # soft yellow
ERR = "#f48771"          # warm red
INFO = "#9cdcfe"

# Categorical palette for charts (mostly within VS Code's syntax-highlight range)
CHART_CYCLE = [
    "#0098ff", "#4ec9b0", "#dcdcaa", "#c586c0",
    "#9cdcfe", "#f48771", "#ce9178", "#b5cea8",
    "#569cd6", "#d7ba7d",
]


# -------------------------------------------------
# GLOBAL QT STYLESHEET
# -------------------------------------------------
STYLESHEET = f"""
* {{
    color: {TEXT};
    font-family: "Segoe UI", "SF Pro Text", system-ui, sans-serif;
    font-size: 13px;
}}

QMainWindow, QWidget {{
    background-color: {BG};
}}

/* ---- Activity bar (vertical sidebar) ---- */
QFrame#ActivityBar {{
    background-color: {ACTIVITYBAR};
    border-right: 1px solid {BORDER};
}}
QPushButton#ActivityButton {{
    background: transparent;
    border: none;
    border-left: 3px solid transparent;
    color: {TEXT_MUTED};
    padding: 14px 0;
    text-align: center;
    font-size: 11px;
    font-weight: 500;
}}
QPushButton#ActivityButton:hover {{
    color: {TEXT};
    background: {BG_HOVER};
}}
QPushButton#ActivityButton:checked {{
    color: {TEXT};
    border-left-color: {ACCENT};
    background: {BG_PANEL};
}}

/* ---- Header bar at top of content ---- */
QFrame#HeaderBar {{
    background-color: {BG_PANEL};
    border-bottom: 1px solid {BORDER};
}}
QLabel#HeaderTitle {{
    font-size: 15px;
    font-weight: 600;
    color: {TEXT};
}}
QLabel#HeaderSubtitle {{
    color: {TEXT_MUTED};
    font-size: 12px;
}}

/* ---- KPI cards ---- */
QFrame#KpiCard {{
    background-color: {BG_PANEL};
    border: 1px solid {BORDER};
    border-radius: 6px;
}}
QLabel#KpiLabel {{
    color: {TEXT_MUTED};
    font-size: 11px;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}}
QLabel#KpiValue {{
    color: {TEXT};
    font-size: 24px;
    font-weight: 600;
}}
QLabel#KpiValueAccent {{
    color: {ACCENT};
    font-size: 24px;
    font-weight: 600;
}}

/* ---- Buttons ---- */
QPushButton {{
    background-color: {BG_ELEV};
    color: {TEXT};
    border: 1px solid {BORDER_STRONG};
    border-radius: 4px;
    padding: 6px 14px;
    min-height: 22px;
}}
QPushButton:hover {{
    background-color: {BG_ACTIVE};
    border-color: {ACCENT_SUBTLE};
}}
QPushButton:pressed {{
    background-color: {ACCENT_SUBTLE};
}}
QPushButton:disabled {{
    color: {TEXT_DIM};
    background-color: {BG_PANEL};
    border-color: {BORDER};
}}
QPushButton#PrimaryButton {{
    background-color: {ACCENT};
    color: white;
    border: 1px solid {ACCENT};
    font-weight: 600;
    padding: 8px 22px;
}}
QPushButton#PrimaryButton:hover {{
    background-color: {ACCENT_HOVER};
    border-color: {ACCENT_HOVER};
}}
QPushButton#PrimaryButton:disabled {{
    background-color: {ACCENT_SUBTLE};
    border-color: {ACCENT_SUBTLE};
    color: {TEXT_DIM};
}}

/* ---- Combo / dropdown ---- */
QComboBox {{
    background: {BG_ELEV};
    border: 1px solid {BORDER_STRONG};
    border-radius: 3px;
    padding: 4px 8px;
    min-height: 22px;
}}
QComboBox:hover {{ border-color: {ACCENT_SUBTLE}; }}
QComboBox QAbstractItemView {{
    background: {BG_ELEV};
    border: 1px solid {BORDER_STRONG};
    selection-background-color: {ACCENT_SUBTLE};
    selection-color: {TEXT};
}}
QComboBox::drop-down {{
    border: none;
    width: 18px;
}}

/* ---- Tables ---- */
QTableWidget {{
    background-color: {BG};
    alternate-background-color: {BG_PANEL};
    gridline-color: {BORDER};
    border: 1px solid {BORDER};
    border-radius: 4px;
    selection-background-color: {ACCENT_SUBTLE};
    selection-color: {TEXT};
}}
QHeaderView::section {{
    background-color: {BG_ELEV};
    color: {TEXT_MUTED};
    border: none;
    border-right: 1px solid {BORDER};
    border-bottom: 1px solid {BORDER};
    padding: 6px 8px;
    font-weight: 600;
    text-transform: uppercase;
    font-size: 11px;
    letter-spacing: 0.4px;
}}
QTableWidget::item {{
    border: none;
    padding: 4px 6px;
}}

/* ---- Status bar ---- */
QStatusBar {{
    background-color: {ACCENT};
    color: white;
    font-size: 12px;
    min-height: 22px;
}}
QStatusBar QLabel {{
    color: white;
    padding: 0 8px;
}}

/* ---- Progress ---- */
QProgressBar {{
    background-color: rgba(255,255,255,0.15);
    border: none;
    border-radius: 2px;
    height: 4px;
    text-align: center;
    color: transparent;
}}
QProgressBar::chunk {{
    background-color: white;
    border-radius: 2px;
}}

/* ---- Scrollbars ---- */
QScrollBar:vertical, QScrollBar:horizontal {{
    background: {BG};
    border: none;
}}
QScrollBar:vertical {{ width: 12px; }}
QScrollBar:horizontal {{ height: 12px; }}
QScrollBar::handle:vertical, QScrollBar::handle:horizontal {{
    background: {BORDER_STRONG};
    border-radius: 4px;
    margin: 2px;
}}
QScrollBar::handle:hover {{ background: {TEXT_DIM}; }}
QScrollBar::add-line, QScrollBar::sub-line {{ background: none; height: 0; width: 0; }}

/* ---- Misc ---- */
QLabel {{ background: transparent; }}
QToolTip {{
    background-color: {BG_ELEV};
    color: {TEXT};
    border: 1px solid {BORDER_STRONG};
    padding: 4px 6px;
}}

QFrame#PageHeader {{
    background-color: transparent;
}}
QLabel#PageTitle {{
    font-size: 18px;
    font-weight: 600;
    color: {TEXT};
}}
QLabel#PageSubtitle {{
    color: {TEXT_MUTED};
    font-size: 12px;
}}

/* ---- Home page ---- */
QLabel#Eyebrow {{
    color: {ACCENT};
    font-weight: 700;
    font-size: 11px;
    letter-spacing: 3px;
}}
QLabel#Headline {{
    font-size: 38px;
    font-weight: 700;
    color: {TEXT};
}}
QLabel#Tagline {{
    color: {TEXT_MUTED};
    font-size: 15px;
}}
QFrame#DropZone {{
    background-color: rgba(0, 152, 255, 0.04);
    border: 2px dashed {BORDER_STRONG};
    border-radius: 10px;
}}
QFrame#DropZone[active="true"] {{
    background-color: rgba(0, 152, 255, 0.14);
    border: 2px dashed {ACCENT};
}}
QLabel#DropTitle {{
    color: {TEXT};
    font-size: 18px;
    font-weight: 600;
}}
QLabel#DropHint {{
    color: {TEXT_DIM};
    font-size: 12px;
}}
QLabel#SectionLabel {{
    color: {TEXT_DIM};
    font-weight: 700;
    font-size: 11px;
    letter-spacing: 2px;
}}
QFrame#FeatureCard {{
    background-color: {BG_PANEL};
    border: 1px solid {BORDER};
    border-radius: 8px;
}}
QFrame#FeatureCard:hover {{
    border-color: {ACCENT_SUBTLE};
}}
QLabel#FeatureNumber {{
    color: {ACCENT};
    font-size: 12px;
    font-weight: 700;
    letter-spacing: 2px;
}}
QLabel#FeatureTitle {{
    color: {TEXT};
    font-size: 15px;
    font-weight: 600;
}}
QLabel#FeatureBody {{
    color: {TEXT_MUTED};
    font-size: 12px;
}}
QFrame#StatsStrip {{
    background-color: {BG_PANEL};
    border: 1px solid {BORDER};
    border-radius: 8px;
}}
QLabel#StatNumber {{
    color: {ACCENT};
    font-size: 26px;
    font-weight: 700;
}}
QLabel#StatLabel {{
    color: {TEXT_MUTED};
    font-size: 10px;
    letter-spacing: 1.5px;
    font-weight: 600;
}}
QFrame#Divider {{
    background-color: {BORDER};
    max-height: 1px;
    min-height: 1px;
}}
QFrame#StatDivider {{
    background-color: {BORDER};
    max-width: 1px;
    min-width: 1px;
}}
"""


# -------------------------------------------------
# MATPLOTLIB DARK THEME
# -------------------------------------------------
def apply_mpl_theme():
    import matplotlib as mpl
    from cycler import cycler

    mpl.rcParams.update({
        "figure.facecolor": BG,
        "axes.facecolor": BG,
        "savefig.facecolor": BG,
        "axes.edgecolor": BORDER,
        "axes.labelcolor": TEXT_MUTED,
        "axes.titlecolor": TEXT,
        "axes.titlesize": 12,
        "axes.titleweight": "600",
        "axes.titlepad": 12,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "axes.grid": True,
        "grid.color": BORDER,
        "grid.linewidth": 0.5,
        "grid.alpha": 0.6,
        "xtick.color": TEXT_MUTED,
        "ytick.color": TEXT_MUTED,
        "text.color": TEXT,
        "legend.facecolor": BG_PANEL,
        "legend.edgecolor": BORDER,
        "legend.labelcolor": TEXT,
        "legend.fontsize": 9,
        "font.family": ["Segoe UI", "sans-serif"],
        "font.size": 10,
        "axes.prop_cycle": cycler(color=CHART_CYCLE),
    })
