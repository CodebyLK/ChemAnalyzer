import sys
from PyQt6.QtWidgets import (
    QMainWindow, QLabel, QVBoxLayout, QHBoxLayout,
    QWidget, QLineEdit, QPushButton, QTabWidget,
    QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox, QComboBox,
    QApplication
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon
from app.controller import ChemController
from app.models.visualizer import MoleculeVisualizer

class ChemAnalyzerWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.controller = ChemController()
        self.setWindowTitle("Chemical Compound & Reaction Analyzer")
        self.resize(650, 550)

        self.setWindowIcon(QIcon("assets/icon.png"))

        self.setStyleSheet("""
            QMainWindow { background-color: #1B2845; }
            QLabel { color: #65AFFF; font-size: 16px; font-weight: bold; }
            QLineEdit, QComboBox { background-color: #274060; color: white; border: 2px solid #335C81; padding: 10px; font-size: 14px; border-radius: 4px; }
            QComboBox::drop-down { border-left: 2px solid #335C81; }
            QComboBox QAbstractItemView { background-color: #274060; color: white; selection-background-color: #4C86C0; }
            QPushButton { background-color: #4C86C0; color: white; font-weight: bold; padding: 12px; border-radius: 5px; font-size: 14px; }
            QPushButton:hover { background-color: #5899E2; }
            QPushButton:disabled { background-color: #335C81; color: #888888; }
            QPushButton#deleteBtn { background-color: #A3333D; }
            QPushButton#deleteBtn:hover { background-color: #C43B47; }
            
            QTabBar::tab { background-color: #274060; color: white; padding: 10px 25px; margin-right: 2px; border-top-left-radius: 4px; border-top-right-radius: 4px; }
            QTabBar::tab:selected { background-color: #4C86C0; font-weight: bold; }
            QTabWidget::pane { border: 2px solid #4C86C0; border-radius: 4px; }
            QTableWidget { background-color: #274060; color: white; gridline-color: #335C81; font-size: 14px; }
            QHeaderView::section { background-color: #1B2845; color: #65AFFF; padding: 4px; border: 1px solid #335C81; font-weight: bold; }
            QHeaderView { background-color: #274060; border: none; }
            
            #resultBox { background-color: #0D1626; border-radius: 5px; padding: 15px; color: #00FFC2; font-family: 'Courier New'; font-size: 15px; }
            
            QTableWidget QTableCornerButton::section {
                background-color: #1B2845;
                border: 1px solid #335C81;
            }
        """)

        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)

        self.tab_analyzer = QWidget()
        self.tab_balancer = QWidget()
        self.tab_history = QWidget()

        self.tabs.addTab(self.tab_analyzer, "Compound Analyzer")
        self.tabs.addTab(self.tab_balancer, "Equation Balancer")
        self.tabs.addTab(self.tab_history, "History")

        self.setup_analyzer_tab()
        self.setup_balancer_tab()
        self.setup_history_tab()

    def setup_analyzer_tab(self):
        layout = QVBoxLayout(self.tab_analyzer)
        layout.setSpacing(15)

        layout.addWidget(QLabel("1. Enter Empirical/Molecular Formula:"))

        search_layout = QHBoxLayout()
        self.formula_input = QLineEdit()
        self.formula_input.setPlaceholderText("e.g. C2H6O")
        self.find_isomers_btn = QPushButton("Search PubChem")
        search_layout.addWidget(self.formula_input)
        search_layout.addWidget(self.find_isomers_btn)
        layout.addLayout(search_layout)

        layout.addWidget(QLabel("2. Select Specific Isomer for 3D Analysis:"))
        self.isomer_dropdown = QComboBox()
        self.isomer_dropdown.setPlaceholderText("Awaiting search...")
        self.isomer_dropdown.setEnabled(False)
        layout.addWidget(self.isomer_dropdown)

        self.analyze_button = QPushButton("Analyze Molar Mass & Prepare 3D")
        self.analyze_button.setEnabled(False)

        self.comp_result_label = QLabel("Result will appear here...")
        self.comp_result_label.setObjectName("resultBox")
        self.comp_result_label.setWordWrap(True)

        layout.addWidget(self.analyze_button)
        layout.addWidget(self.comp_result_label)
        layout.addStretch()

        self.find_isomers_btn.clicked.connect(self.on_find_isomers_clicked)
        self.analyze_button.clicked.connect(self.on_analyze_clicked)

        self.current_isomers = {}

    def on_find_isomers_clicked(self):
        formula = self.formula_input.text().strip()
        if not formula:
            return

        self.find_isomers_btn.setText("Searching...")
        QApplication.processEvents()

        self.current_isomers = self.controller.get_isomers(formula)

        self.isomer_dropdown.clear()

        if self.current_isomers:
            isomer_names = list(self.current_isomers.keys())
            self.isomer_dropdown.addItems(isomer_names)
            self.isomer_dropdown.setCurrentIndex(0)

            self.isomer_dropdown.setEnabled(True)
            self.analyze_button.setEnabled(True)
            self.comp_result_label.setText("Isomers found! Select one and click Analyze.")
        else:
            self.isomer_dropdown.setEnabled(False)
            self.analyze_button.setEnabled(False)
            self.comp_result_label.setText(f"No 3D structures found for {formula}.")

        self.find_isomers_btn.setText("Search PubChem")

    def on_analyze_clicked(self):
        formula = self.formula_input.text().strip()
        selected_name = self.isomer_dropdown.currentText()

        cid = self.current_isomers.get(selected_name)

        math_res = self.controller.process_compound(formula)

        self.comp_result_label.setText(f"{math_res}\n\nFetching 3D coordinates for {selected_name} (CID: {cid})...")
        QApplication.processEvents()

        sdf_data = self.controller.get_3d_data(cid)

        # Refresh history and force UI update BEFORE launching the 3D window
        self.load_history()
        QApplication.processEvents()

        if sdf_data:
            self.comp_result_label.setText(f"{math_res}\n\n[SUCCESS] 3D coordinates downloaded for {selected_name}! Launching visualizer...")

            # App pauses main thread here to handle the 3D interaction
            MoleculeVisualizer.show_3d(sdf_data, selected_name)

        else:
            self.comp_result_label.setText(f"{math_res}\n\n[ERROR] Could not fetch 3D coordinates.")

    def setup_balancer_tab(self):
        layout = QVBoxLayout(self.tab_balancer)
        layout.setSpacing(15)
        layout.addWidget(QLabel("Balance Chemical Equation"))
        layout.addWidget(QLabel("Format: Reactants = Products (use '+' between molecules)"))
        self.eq_input = QLineEdit()
        self.eq_input.setPlaceholderText("e.g. H2 + O2 = H2O")
        self.balance_button = QPushButton("Balance Equation")
        self.eq_result_label = QLabel("Balanced equation will appear here...")
        self.eq_result_label.setObjectName("resultBox")
        layout.addWidget(self.eq_input)
        layout.addWidget(self.balance_button)
        layout.addWidget(self.eq_result_label)
        layout.addStretch()
        self.balance_button.clicked.connect(self.on_balance_clicked)

    def setup_history_tab(self):
        layout = QVBoxLayout(self.tab_history)
        self.history_table = QTableWidget()
        self.history_table.setColumnCount(4)
        self.history_table.setHorizontalHeaderLabels(["ID", "Formula", "Molar Mass", "Date"])
        self.history_table.setColumnHidden(0, True)
        self.history_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        button_layout = QHBoxLayout()
        self.refresh_button = QPushButton("Refresh")
        self.delete_button = QPushButton("Delete Selected")
        self.delete_button.setObjectName("deleteBtn")
        button_layout.addWidget(self.refresh_button)
        button_layout.addWidget(self.delete_button)
        layout.addWidget(self.history_table)
        layout.addLayout(button_layout)
        self.refresh_button.clicked.connect(self.load_history)
        self.delete_button.clicked.connect(self.on_delete_clicked)
        self.load_history()

    def on_balance_clicked(self):
        eq = self.eq_input.text().strip()
        res = self.controller.balance_equation(eq)
        self.eq_result_label.setText(res)

    def load_history(self):
        self.history_table.setRowCount(0)
        for i, rec in enumerate(self.controller.get_history()):
            self.history_table.insertRow(i)
            self.history_table.setItem(i, 0, QTableWidgetItem(str(rec[0])))
            self.history_table.setItem(i, 1, QTableWidgetItem(str(rec[1])))
            self.history_table.setItem(i, 2, QTableWidgetItem(f"{rec[2]} g/mol"))
            self.history_table.setItem(i, 3, QTableWidgetItem(rec[3].strftime("%Y-%m-%d %H:%M") if rec[3] else ""))

    def on_delete_clicked(self):
        row = self.history_table.currentRow()
        if row >= 0:
            cid = self.history_table.item(row, 0).text()
            self.controller.delete_record(int(cid))
            self.load_history()
            QMessageBox.information(self, "Success", "Record deleted.")