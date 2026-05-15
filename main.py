import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QIcon  # <-- Import QIcon here
from app.views.main_window import ChemAnalyzerWindow

def main():
    # Initialize the PyQt6 application
    app = QApplication(sys.argv)

    # --- THE FIX: Set the icon globally for the entire application ---
    app.setWindowIcon(QIcon("assets/icon.png"))

    # Instantiate and display the main window
    window = ChemAnalyzerWindow()
    window.show()

    # Execute the application loop
    sys.exit(app.exec())

if __name__ == "__main__":
    main()