import os
import sys
import subprocess

from dotenv import load_dotenv
from PySide6.QtWidgets import (QApplication, QWidget, QGridLayout, QHBoxLayout, QLineEdit, 
                               QPushButton, QFileDialog, QLabel, QSpinBox, QDoubleSpinBox,
                               QTextEdit, QVBoxLayout, QMessageBox)
from PySide6.QtCore import Qt, Slot, QThread, Signal
from PySide6.QtGui import QFont, QIcon


# Cargar variables de entorno desde el archivo .env
load_dotenv()
PYTHON=os.getenv("PYTHON_ENV", "python")

class ACOSCPThread(QThread):
    update_log = Signal(str)

    def __init__(self, params):
        super().__init__()
        self.params = params

    def run(self):
        try:
            self.process = subprocess.Popen(
                [PYTHON, './acoscp/acoscp_wrapper.py'] + self.params,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                universal_newlines=True
            )

            for line in iter(self.process.stdout.readline, ''):
                decoded_line = line.encode('utf-8').decode('utf-8')
                self.update_log.emit(decoded_line.strip())

            self.process.wait()

            if self.process.returncode != 0:
                self.update_log.emit(f"Error: El proceso terminó con código de salida {self.process.returncode}")

        except Exception as e:
            self.update_log.emit(f"Error al ejecutar el programa: {str(e)}")

    def cancel_thread(self):
        if self.process:
            self.process.terminate()
            self.update_log.emit("Ejecución Terminada.")


class clsGui(QWidget):

    def __init__(self):

        self.acoscp_thread = None

        super().__init__()
        self.setWindowTitle('Configuración de Algoritmo ACOSCP')
        self.setMinimumSize(500, 600)
        self.setWindowIcon(QIcon('./gui/app_icon.png'))
        self.setup_ui()

    def setup_ui(self):
        main_layout = QVBoxLayout()
        self.setLayout(main_layout)

        form_layout = QGridLayout()

        title_font = QFont()
        title_font.setBold(True)
        title_font.setPointSize(14)

        title = QLabel("Configuración de Parámetros ACOSCP")
        title.setFont(title_font)
        title.setAlignment(Qt.AlignCenter)
        form_layout.addWidget(title, 0, 0, 1, 2)

        self.create_labeled_input(form_layout, 1, "Alpha:", QDoubleSpinBox, (0.0, 10.0, 0.1, 1.0))
        self.create_labeled_input(form_layout, 2, "Beta:", QDoubleSpinBox, (0.0, 10.0, 0.1, 2.0))
        self.create_labeled_input(form_layout, 3, "Rho:", QDoubleSpinBox, (0.0, 1.0, 0.01, 0.1))
        self.create_labeled_input(form_layout, 4, "Q0:", QDoubleSpinBox, (0.0, 1.0, 0.01, 0.7))
        self.create_labeled_input(form_layout, 5, "Tao:", QDoubleSpinBox, (0.000, 1.000, 0.001, 0.001))
        self.create_labeled_input(form_layout, 6, "Iteraciones:", QSpinBox, (1, 1000, 1, 20))
        self.create_labeled_input(form_layout, 7, "Cantidad_de_hormigas:", QSpinBox, (1, 1000, 1, 10))

        self.create_file_input(form_layout, 8, "Archivo_de_entrada:", "Seleccionar Archivo")
        self.create_file_input(form_layout, 9, "Directorio_de_resultados:", "Seleccionar Directorio", True)

        button_layout = QHBoxLayout()
        
        self.submit_button = QPushButton("Ejecutar Algoritmo")
        self.submit_button.clicked.connect(self.submit_form)
        self.submit_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        button_layout.addWidget(self.submit_button)

        self.cancel_button = QPushButton("Cancelar Ejecución")
        self.cancel_button.clicked.connect(self.cancel_execution)
        self.cancel_button.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                color: white;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #d32f2f;
            }
        """)
        self.cancel_button.setEnabled(False)
        button_layout.addWidget(self.cancel_button)

        form_layout.addLayout(button_layout, 11, 0, 1, 2)

        main_layout.addLayout(form_layout)

        # Console-like log area
        self.log_area = QTextEdit()
        self.log_area.setReadOnly(True)
        self.log_area.setStyleSheet("""
            QTextEdit {
                background-color: #000000;
                color: #FFFFFF;
                font-family: Consolas, Monaco, monospace;
            }
        """)
        main_layout.addWidget(self.log_area)

    def create_labeled_input(self, layout, row, label, widget_type, properties=None):
        label_widget = QLabel(label.replace('_', ' ').replace(':', ''))
        layout.addWidget(label_widget, row, 0)

        input_widget = widget_type()

        if properties:
            if isinstance(input_widget, (QSpinBox, QDoubleSpinBox)):
                input_widget.setRange(properties[0], properties[1])
                input_widget.setSingleStep(properties[2])

            if isinstance(input_widget, (QDoubleSpinBox)):
                input_widget.setDecimals(3)

            input_widget.setValue(properties[3])

        layout.addWidget(input_widget, row, 1)
        setattr(self, label.lower().replace(':', ''), input_widget)

    def create_file_input(self, layout, row, label, button_text, is_directory=False):
        label_widget = QLabel(label.replace('_', ' ').replace(':', ''))
        layout.addWidget(label_widget, row, 0)

        file_input = QLineEdit()
        file_input.setReadOnly(True)
        layout.addWidget(file_input, row, 1)

        file_button = QPushButton(button_text)
        file_button.clicked.connect(lambda: self.select_file(file_input, is_directory))
        layout.addWidget(file_button, row, 2)

        setattr(self, label.lower().replace(':', ''), file_input)

    @Slot()
    def select_file(self, input_field, is_directory):
        if is_directory:
            path = QFileDialog.getExistingDirectory(self, "Seleccionar Directorio")
        else:
            path, _ = QFileDialog.getOpenFileName(self, "Seleccionar Archivo")
        if path:
            input_field.setText(path)

    def validate_form(self):
        empty_fields = []
        
        for attr, value in self.__dict__.items():
            if isinstance(value, (QLineEdit, QSpinBox, QDoubleSpinBox)):
                if isinstance(value, QLineEdit) and not value.text():
                    empty_fields.append(attr)
                elif isinstance(value, (QSpinBox, QDoubleSpinBox)) and value.value() == 0:
                    empty_fields.append(attr)
        
        if empty_fields:
            QMessageBox.warning(self, "Campos Obligatorios", 
                                "Complete todos los campos obligatorios:\n" + 
                                "\n".join(field.replace('_', ' ').capitalize() for field in empty_fields))
            return False

        return True

    @Slot()
    def submit_form(self):

        if not self.validate_form():
            return

        if self.acoscp_thread and self.acoscp_thread.isRunning():
            QMessageBox.warning(self, "Ejecución en curso", "Ya se está ejecutando ACOSCP.")
            return

        self.log_area.clear()
        self.log_area.append("Iniciando ejecución del algoritmo ACOSCP...")
        
        params = [
            self.archivo_de_entrada.text(),
            self.directorio_de_resultados.text(),
            str(self.alpha.value()),
            str(self.beta.value()),
            str(self.rho.value()),
            str(self.q0.value()),
            str(self.iteraciones.value()),
            str(self.cantidad_de_hormigas.value()),
            str(self.tao.value())
        ]

        self.acoscp_thread = ACOSCPThread(params)
        self.acoscp_thread.update_log.connect(self.update_log)
        self.acoscp_thread.finished.connect(self.on_execution_finished)
        self.acoscp_thread.start()
        
        self.submit_button.setEnabled(False)
        self.cancel_button.setEnabled(True)

    @Slot(str)
    def update_log(self, message):
        self.log_area.append(message)

    @Slot()
    def cancel_execution(self):
        if self.acoscp_thread and self.acoscp_thread.isRunning():
            self.log_area.append("Cancelando ejecución...")
            self.acoscp_thread.cancel_thread()
        else:
            QMessageBox.information(self, "Información", "No hay ninguna ejecución en curso para cancelar.")

    @Slot()
    def on_execution_finished(self):
        self.submit_button.setEnabled(True)
        self.cancel_button.setEnabled(False)
        self.log_area.append("Ejecución finalizada.")

    def closeEvent(self, event):
        if self.acoscp_thread and self.acoscp_thread.isRunning():
            self.acoscp_thread.cancel_thread()
        super().closeEvent(event)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    form = clsGui()
    form.show()
    sys.exit(app.exec())