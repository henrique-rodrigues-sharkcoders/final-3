import sys
import sqlite3
import pandas as pd

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
    QFrame
)

from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure

from vinted_scraper import scrape_vinted


DB_NAME = "vintelligence.db"


# ==========================================
# DB LOAD
# ==========================================

def get_data():
    conn = sqlite3.connect(DB_NAME)

    try:
        df = pd.read_sql_query("SELECT * FROM listings ORDER BY score DESC", conn)
    except:
        df = pd.DataFrame()

    conn.close()
    return df


# ==========================================
# GRAPH
# ==========================================

class ProfitGraph(FigureCanvasQTAgg):

    def __init__(self):
        self.figure = Figure(figsize=(5, 3))
        self.ax = self.figure.add_subplot(111)
        super().__init__(self.figure)

        self.ax.set_facecolor("#121722")
        self.figure.patch.set_facecolor("#0f1115")

    def update_graph(self, df):

        self.ax.clear()

        self.ax.set_facecolor("#121722")
        self.figure.patch.set_facecolor("#0f1115")

        if not df.empty and "profit" in df.columns:
            self.ax.plot(df.index, df["profit"], color="#5b8cff", linewidth=2)
            self.ax.set_title("Profit Evolution")

        self.draw()


# ==========================================
# UI
# ==========================================

class Vintelligence(QWidget):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("VINTELLIGENCE")
        self.resize(1400, 800)

        self.build_ui()
        self.refresh_data()

    def build_ui(self):

        root = QHBoxLayout(self)

        # LEFT
        left = QVBoxLayout()

        title = QLabel("FILTERS")
        self.search = QLineEdit()
        self.search.setPlaceholderText("Search...")

        btn = QPushButton("Refresh")
        btn.clicked.connect(self.refresh_data)

        left.addWidget(title)
        left.addWidget(self.search)
        left.addWidget(btn)
        left.addStretch()

        # CENTER
        center = QVBoxLayout()

        self.profit = QLabel("Profit")
        self.roi = QLabel("ROI")
        self.count = QLabel("Count")

        stats = QHBoxLayout()

        for w in [self.profit, self.roi, self.count]:

            f = QFrame()
            lay = QVBoxLayout(f)
            lay.addWidget(w)
            stats.addWidget(f)

        self.table = QTableWidget()

        center.addLayout(stats)
        center.addWidget(self.table)

        # RIGHT
        right = QVBoxLayout()

        self.graph = ProfitGraph()

        right.addWidget(QLabel("GRAPH"))
        right.addWidget(self.graph)

        # ROOT
        root.addLayout(left, 1)
        root.addLayout(center, 4)
        root.addLayout(right, 2)

    def refresh_data(self):

        scrape_vinted()  # 🔥 atualiza DB

        df = get_data()

        search = self.search.text().lower()

        if search and not df.empty:
            df = df[df["title"].str.lower().str.contains(search, na=False)]

        self.update_stats(df)
        self.update_table(df)
        self.graph.update_graph(df)

    def update_stats(self, df):

        if df.empty:
            self.profit.setText("Profit: 0")
            self.roi.setText("ROI: 0")
            self.count.setText("0 listings")
            return

        self.profit.setText(f"Profit: €{df['profit'].sum():.2f}")
        self.roi.setText(f"ROI: {df['roi'].mean():.2f}%")
        self.count.setText(f"{len(df)} listings")

    def update_table(self, df):

        if df.empty:
            self.table.clear()
            return

        cols = ["title", "brand", "price", "profit", "roi", "score"]

        self.table.setRowCount(len(df))
        self.table.setColumnCount(len(cols))
        self.table.setHorizontalHeaderLabels(cols)

        for i in range(len(df)):
            for j, c in enumerate(cols):
                self.table.setItem(i, j, QTableWidgetItem(str(df.iloc[i][c])))

        self.table.resizeColumnsToContents()


# ==========================================
# RUN
# ==========================================

app = QApplication(sys.argv)

app.setStyleSheet("""
QWidget {
    background-color: #0f1115;
    color: white;
}
QPushButton {
    background-color: #1a1f2b;
    padding: 8px;
}
QTableWidget {
    background-color: #121722;
}
""")

window = Vintelligence()
window.show()

sys.exit(app.exec())