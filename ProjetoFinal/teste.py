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
    QFrame,
    QDialog,
    QComboBox,
    QFormLayout,
    QHeaderView
)

from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure


DB_NAME = "vintelligence.db"


def get_data():
    conn = sqlite3.connect(DB_NAME)
    try:
        df = pd.read_sql_query("SELECT * FROM listings ORDER BY score DESC", conn)
    except:
        df = pd.DataFrame()
    conn.close()
    return df


class ProfitGraph(FigureCanvasQTAgg):

    def __init__(self):
        self.figure = Figure(figsize=(5, 3))
        self.ax = self.figure.add_subplot(111)
        super().__init__(self.figure)

        self.ax.set_facecolor("#121722")
        self.figure.patch.set_facecolor("#0f1115")
        self.ax.grid(True, color="#1f2633", linestyle="--", linewidth=0.5)

    def update_graph(self, df):
        self.ax.clear()

        self.ax.set_facecolor("#121722")
        self.figure.patch.set_facecolor("#0f1115")
        self.ax.grid(True, color="#1f2633", linestyle="--", linewidth=0.5)

        if not df.empty and "profit" in df.columns:
            self.ax.plot(df.index, df["profit"], color="#5b8cff", linewidth=2)
            self.ax.set_title("Profit Evolution", color="#e6e6e6")
            self.ax.set_ylabel("Profit", color="#e6e6e6")

        self.draw()


class SettingsDialog(QDialog):

    def __init__(self, parent):
        super().__init__(parent)

        self.parent = parent
        self.setWindowTitle("Settings")
        self.resize(300, 150)

        layout = QFormLayout()

        self.theme = QComboBox()
        self.theme.addItems(["Dark", "Light"])
        self.theme.setCurrentText(parent.theme)

        self.currency = QComboBox()
        self.currency.addItems(["EUR", "USD", "GBP", "JPY", "BRL"])
        self.currency.setCurrentText(parent.currency)

        btn = QPushButton("Save")
        btn.clicked.connect(self.save)

        layout.addRow("Theme", self.theme)
        layout.addRow("Currency", self.currency)
        layout.addRow(btn)

        self.setLayout(layout)

    def save(self):
        self.parent.theme = self.theme.currentText()
        self.parent.currency = self.currency.currentText()
        self.parent.apply_theme()
        self.parent.refresh_data()
        self.accept()


class Vintelligence(QWidget):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("VINTELLIGENCE")
        self.resize(1400, 800)

        self.theme = "Dark"
        self.currency = "EUR"

        self.symbols = {"EUR":"€","USD":"$","GBP":"£","JPY":"¥","BRL":"R$"}
        self.rates = {"EUR":1,"USD":1.08,"GBP":0.86,"JPY":170,"BRL":6.2}

        self.build_ui()
        self.apply_theme()
        self.refresh_data()

    def build_ui(self):

        root = QHBoxLayout(self)

        left = QVBoxLayout()

        self.search = QLineEdit()
        self.search.setPlaceholderText("Search...")
        self.search.textChanged.connect(self.refresh_data)

        refresh = QPushButton("Refresh")
        refresh.clicked.connect(self.refresh_data)

        settings = QPushButton("Settings")
        settings.clicked.connect(self.open_settings)

        left.addWidget(QLabel("FILTERS"))
        left.addWidget(self.search)
        left.addWidget(refresh)
        left.addWidget(settings)
        left.addStretch()

        center = QVBoxLayout()

        self.profit_label = QLabel()
        self.roi_label = QLabel()
        self.count_label = QLabel()

        stats = QHBoxLayout()
        stats.addWidget(self.profit_label)
        stats.addWidget(self.roi_label)
        stats.addWidget(self.count_label)

        self.table = QTableWidget()

        center.addLayout(stats)
        center.addWidget(self.table)

        right = QVBoxLayout()

        self.graph = ProfitGraph()

        self.weight = QLineEdit()
        self.weight.setPlaceholderText("Weight kg")

        self.distance = QLineEdit()
        self.distance.setPlaceholderText("Distance km")

        ship = QPushButton("Calc Shipping")
        ship.clicked.connect(self.calc_shipping)

        self.ship_result = QLabel("Shipping: €0")

        right.addWidget(QLabel("GRAPH"))
        right.addWidget(self.graph)
        right.addWidget(QLabel("SHIPPING"))
        right.addWidget(self.weight)
        right.addWidget(self.distance)
        right.addWidget(ship)
        right.addWidget(self.ship_result)

        root.addLayout(left,1)
        root.addLayout(center,4)
        root.addLayout(right,2)

    def open_settings(self):
        SettingsDialog(self).exec_()

    def convert(self, v):
        return round(v * self.rates.get(self.currency,1),2)

    def sym(self):
        return self.symbols.get(self.currency,"€")

    def apply_theme(self):

        if self.theme == "Dark":
            self.setStyleSheet("""
            QWidget{background:#0f1115;color:#e6e6e6;}
            QLineEdit,QTableWidget{background:#161a22;color:white;}
            QPushButton{background:#1a1f2b;}
            """)
        else:
            self.setStyleSheet("""
            QWidget{background:white;color:black;}
            QLineEdit,QTableWidget{background:#f2f2f2;}
            """)

    def calc_shipping(self):
        try:
            w = float(self.weight.text())
            d = float(self.distance.text())
            cost = 3 + w*0.8 + d*0.01
            cost = self.convert(cost)
            self.ship_result.setText(f"Shipping: {self.sym()}{cost:.2f}")
        except:
            self.ship_result.setText("Invalid")

    def refresh_data(self):

        df = get_data()

        if self.search.text():
            df = df[df["title"].str.lower().str.contains(self.search.text().lower(), na=False)]

        self.update_stats(df)
        self.update_table(df)
        self.graph.update_graph(df)

    def update_stats(self, df):

        if df.empty:
            self.profit_label.setText("0")
            self.roi_label.setText("0%")
            self.count_label.setText("0")
            return

        profit = self.convert(df["profit"].sum())

        self.profit_label.setText(f"Profit {self.sym()}{profit}")
        self.roi_label.setText(f"ROI {df['roi'].mean():.2f}%")
        self.count_label.setText(f"{len(df)} listings")

    def update_table(self, df):

        self.table.clear()

        cols = ["title","brand","price","estimated_value","profit","roi","score"]
        cols = [c for c in cols if c in df.columns]

        self.table.setRowCount(len(df))
        self.table.setColumnCount(len(cols))
        self.table.setHorizontalHeaderLabels(cols)

        for r in range(len(df)):
            for c,i in enumerate(cols):
                v = df.iloc[r][i]
                if i in ["price","profit","estimated_value"]:
                    try:
                        v = f"{self.sym()}{self.convert(float(v))}"
                    except:
                        pass
                self.table.setItem(r,c,QTableWidgetItem(str(v)))

        self.table.resizeColumnsToContents()


app = QApplication(sys.argv)
w = Vintelligence()
w.show()
sys.exit(app.exec_())
