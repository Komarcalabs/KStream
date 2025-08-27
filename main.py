import sys
import subprocess
from pathlib import Path
import re
import platform
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton, QLabel, QFileDialog, QListWidget, QMessageBox
)

# Función para generar slug legible
def slugify(value):
    value = re.sub(r"[^\w\s-]", "", value)
    value = re.sub(r"\s+", "_", value)
    return value.lower()

# Detectar ffmpeg según plataforma
def get_ffmpeg_bin():
    if getattr(sys, 'frozen', False):
        base_dir = Path(sys._MEIPASS)  # PyInstaller
    else:
        base_dir = Path(__file__).parent

    if platform.system() == "Windows":
        ffmpeg_path = base_dir / "ffmpeg.exe"
        if ffmpeg_path.exists():
            return str(ffmpeg_path)
    # Otros sistemas usan PATH
    return "ffmpeg"

def get_ffprobe_bin():
    if getattr(sys, 'frozen', False):
        base_dir = Path(sys._MEIPASS)
    else:
        base_dir = Path(__file__).parent

    if platform.system() == "Windows":
        ffprobe_path = base_dir / "ffprobe.exe"
        if ffprobe_path.exists():
            return str(ffprobe_path)
    return "ffprobe"

FFMPEG_BIN = get_ffmpeg_bin()
FFPROBE_BIN = get_ffprobe_bin()

# Función para verificar si un video está optimizado para streaming
def is_streamable(video_path):
    try:
        result = subprocess.run(
            [FFPROBE_BIN, "-v", "trace", "-i", str(video_path)],
            capture_output=True, text=True, check=True
        )
        output = result.stdout + result.stderr
        moov_line = [line for line in output.splitlines() if "moov" in line.lower()]
        if not moov_line:
            return False
        # Heurística: si el primer 'moov' aparece temprano
        return True
    except Exception:
        return False

class VideoOptimizer(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("🎬 Optimizador de Videos para Streaming")
        self.resize(650, 500)

        layout = QVBoxLayout()

        self.label_input = QLabel("Carpeta de origen: No seleccionada")
        self.label_output = QLabel("Carpeta de salida: No seleccionada")
        layout.addWidget(self.label_input)
        layout.addWidget(self.label_output)

        btn_select_input = QPushButton("Seleccionar carpeta de origen")
        btn_select_input.clicked.connect(self.select_input_folder)
        layout.addWidget(btn_select_input)

        btn_select_output = QPushButton("Seleccionar carpeta de salida (opcional)")
        btn_select_output.clicked.connect(self.select_output_folder)
        layout.addWidget(btn_select_output)

        self.list_files = QListWidget()
        layout.addWidget(self.list_files)

        btn_optimize = QPushButton("Iniciar Optimización")
        btn_optimize.clicked.connect(self.start_optimization)
        layout.addWidget(btn_optimize)

        btn_verify = QPushButton("Verificar videos optimizados")
        btn_verify.clicked.connect(self.verify_optimized)
        layout.addWidget(btn_verify)

        self.setLayout(layout)
        self.input_folder = None
        self.output_folder = None

    def select_input_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Seleccionar carpeta de origen")
        if folder:
            self.input_folder = Path(folder)
            self.label_input.setText(f"Carpeta de origen: {folder}")

            if not self.output_folder:
                self.output_folder = self.input_folder / "_optimized"
                self.output_folder.mkdir(exist_ok=True)
                self.label_output.setText(f"Carpeta de salida: {self.output_folder}")

            self.update_file_list()

    def select_output_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Seleccionar carpeta de salida")
        if folder:
            self.output_folder = Path(folder)
            self.label_output.setText(f"Carpeta de salida: {self.output_folder}")

    def update_file_list(self):
        self.list_files.clear()
        if self.input_folder:
            for file in self.input_folder.iterdir():
                if file.is_file() and file.suffix.lower() in [".mp4", ".mov", ".mkv", ".avi"] and "_opt" not in file.stem:
                    self.list_files.addItem(file.name)

    def start_optimization(self):
        if not self.input_folder or not self.output_folder:
            QMessageBox.warning(self, "Error", "Debes seleccionar la carpeta de origen primero.")
            return

        total_files = 0
        skipped_files = 0
        processed_files = 0
        errors_files = 0

        for file in self.input_folder.iterdir():
            if file.is_file() and file.suffix.lower() in [".mp4", ".mov", ".mkv", ".avi"]:
                if "_opt" in file.stem:
                    print(f"⚠ Ignorado: {file.name} (ya optimizado)")
                    skipped_files += 1
                    continue

                slug_name = slugify(file.stem) + "_opt" + file.suffix
                output_file = self.output_folder / slug_name

                try:
                    subprocess.run([
                        FFMPEG_BIN, "-y", "-i", str(file),
                        "-c", "copy", "-movflags", "+faststart",
                        str(output_file)
                    ], check=True)
                    print(f"✅ Procesado: {file.name} -> {output_file.name}")
                    processed_files += 1
                except subprocess.CalledProcessError as e:
                    print(f"❌ Error procesando {file.name}: {e}")
                    errors_files += 1

                total_files += 1

        QMessageBox.information(
            self, "Completado",
            f"Optimización finalizada!\n\n"
            f"Total archivos encontrados: {total_files}\n"
            f"Procesados: {processed_files}\n"
            f"Ignorados: {skipped_files}\n"
            f"Errores: {errors_files}"
        )

    def verify_optimized(self):
        if not self.output_folder or not self.output_folder.exists():
            QMessageBox.warning(self, "Error", "No se ha encontrado la carpeta de videos optimizados.")
            return

        results = []
        for file in self.output_folder.iterdir():
            if file.is_file() and file.suffix.lower() in [".mp4", ".mov", ".mkv", ".avi"]:
                streamable = is_streamable(file)
                status = "✅ Optimizado" if streamable else "❌ No optimizado"
                results.append(f"{file.name}: {status}")

        if results:
            QMessageBox.information(self, "Verificación de videos", "\n".join(results))
        else:
            QMessageBox.information(self, "Verificación de videos", "No se encontraron videos optimizados en la carpeta.")

# --- Ejecutar la app ---
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = VideoOptimizer()
    window.show()
    sys.exit(app.exec())
