import sys
import sqlite3
import pandas as pd

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QLineEdit,
    QFrame,
    QHeaderView
)

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure


DB_NAME = "vintelligence.db"


# ==========================================
# DATABASE
# ==========================================

def get_data():

    conn = sqlite3.connect(DB_NAME)

    try:
        df = pd.read_sql_query(
            "SELECT * FROM listings ORDER BY score DESC",
            conn
        )
    except:
        df = pd.DataFrame()

    conn.close()

    return df


# ==========================================
# GRAPH
# ==========================================

class ProfitGraph(FigureCanvasQTAgg):

    def __init__(self):

        self.figure = Figure(figsize=(6, 4))
        self.ax = self.figure.add_subplot(111)

        super().__init__(self.figure)

        self.figure.patch.set_facecolor("#111827")
        self.ax.set_facecolor("#111827")

    def update_graph(self, df):

        self.ax.clear()

        self.ax.set_facecolor("#111827")

        if not df.empty and "profit" in df.columns:

            profits = df["profit"].head(50)

            self.ax.plot(
                profits.index,
                profits.values,
                linewidth=2
            )

            self.ax.set_title(
                "Profit Distribution",
                color="white"
            )

            self.ax.tick_params(colors="white")

        self.draw()


# ==========================================
# KPI CARD
# ==========================================

class StatCard(QFrame):

    def __init__(self, title):

        super().__init__()

        self.setObjectName("card")

        layout = QVBoxLayout(self)

        self.title = QLabel(title)
        self.title.setObjectName("cardTitle")

        self.value = QLabel("0")
        self.value.setObjectName("cardValue")

        layout.addWidget(self.title)
        layout.addWidget(self.value)

    def set_value(self, value):
        self.value.setText(str(value))


# ==========================================
# MAIN WINDOW
# ==========================================

class Vintelligence(QWidget):

    def __init__(self):

        super().__init__()

        self.setWindowTitle("VINTELLIGENCE")
        self.resize(1600, 900)

        self.build_ui()
        self.refresh_data()

    # ----------------------------------

    def build_ui(self):

        root = QHBoxLayout(self)

        # ==========================
        # LEFT SIDEBAR
        # ==========================

        sidebar = QVBoxLayout()

        logo = QLabel("VINTELLIGENCE")
        logo.setObjectName("logo")

        self.search = QLineEdit()
        self.search.setPlaceholderText("Search listings...")

        self.search.textChanged.connect(
            self.refresh_data
        )

        refresh_btn = QPushButton("Refresh")
        refresh_btn.clicked.connect(
            self.refresh_data
        )

        sidebar.addWidget(logo)
        sidebar.addWidget(self.search)
        sidebar.addWidget(refresh_btn)
        sidebar.addStretch()

        # ==========================
        # CENTER
        # ==========================

        center = QVBoxLayout()

        cards = QHBoxLayout()

        self.total_card = StatCard("Listings")
        self.profit_card = StatCard("Total Profit")
        self.roi_card = StatCard("Average ROI")

        cards.addWidget(self.total_card)
        cards.addWidget(self.profit_card)
        cards.addWidget(self.roi_card)

        self.table = QTableWidget()

        self.table.setSortingEnabled(True)
        self.table.setAlternatingRowColors(True)

        self.table.horizontalHeader().setSectionResizeMode(
            QHeaderView.Stretch
        )

        center.addLayout(cards)
        center.addWidget(self.table)

        # ==========================
        # RIGHT
        # ==========================

        right = QVBoxLayout()

        graph_title = QLabel("Analytics")
        graph_title.setObjectName("sectionTitle")

        self.graph = ProfitGraph()

        right.addWidget(graph_title)
        right.addWidget(self.graph)

        # ==========================
        # ROOT
        # ==========================

        root.addLayout(sidebar, 1)
        root.addLayout(center, 5)
        root.addLayout(right, 2)

    # ----------------------------------

    def refresh_data(self):

        df = get_data()

        search = self.search.text().lower()

        if search and not df.empty:

            df = df[
                df["title"]
                .str.lower()
                .str.contains(search, na=False)
            ]

        self.update_stats(df)
        self.update_table(df)
        self.graph.update_graph(df)

    # ----------------------------------

    def update_stats(self, df):

        if df.empty:

            self.total_card.set_value("0")
            self.profit_card.set_value("€0")
            self.roi_card.set_value("0%")

            return

        self.total_card.set_value(
            len(df)
        )

        self.profit_card.set_value(
            f"€{df['profit'].sum():.2f}"
        )

        self.roi_card.set_value(
            f"{df['roi'].mean():.2f}%"
        )

    # ----------------------------------

    def update_table(self, df):

        if df.empty:

            self.table.clear()
            return

        columns = [
            "title",
            "price",
            "profit",
            "roi",
            "score",
            "url"
        ]

        available = [
            c for c in columns
            if c in df.columns
        ]

        self.table.setRowCount(len(df))
        self.table.setColumnCount(len(available))
        self.table.setHorizontalHeaderLabels(
            available
        )

        for row in range(len(df)):

            for col, column in enumerate(
                available
            ):

                item = QTableWidgetItem(
                    str(df.iloc[row][column])
                )

                self.table.setItem(
                    row,
                    col,
                    item
                )


# ==========================================
# APP
# ==========================================

app = QApplication(sys.argv)

app.setStyleSheet("""

QWidget {
    background:#0b1220;
    color:white;
    font-family:Segoe UI;
}

#logo{
    font-size:24px;
    font-weight:bold;
    color:#60a5fa;
}

#sectionTitle{
    font-size:18px;
    font-weight:bold;
}

#card{
    background:#111827;
    border-radius:12px;
    border:1px solid #1f2937;
}

#cardTitle{
    color:#9ca3af;
    font-size:12px;
}

#cardValue{
    font-size:24px;
    font-weight:bold;
}

QLineEdit{
    background:#111827;
    border:1px solid #1f2937;
    padding:10px;
    border-radius:8px;
}

QPushButton{
    background:#2563eb;
    border:none;
    border-radius:8px;
    padding:10px;
}

QPushButton:hover{
    background:#3b82f6;
}

QTableWidget{
    background:#111827;
    gridline-color:#1f2937;
    border:1px solid #1f2937;
}

QHeaderView::section{
    background:#1f2937;
    padding:8px;
    border:none;
}

""")

window = Vintelligence()
window.show()

sys.exit(app.exec())