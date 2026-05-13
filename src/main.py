import sys
import os

# Asegurar que el directorio padre esté en el path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.ui.app import PyAnalyzerApp


def main():
    """Punto de entrada principal."""
    app = PyAnalyzerApp()
    app.mainloop()


if __name__ == "__main__":
    main()
