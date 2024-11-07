from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QSpinBox, QHBoxLayout, QPushButton, QCheckBox, QTableWidget, QTableWidgetItem, QFileDialog
from PyQt5.QtGui import QColor, QFont
from PyQt5.QtCore import pyqtSignal, QObject, QThread
import sys

class ImageDownloadThread(QThread):
    finished = pyqtSignal(object)
    progress = pyqtSignal(str, str)

    def __init__(self, downloader, update_table_callback):
        super().__init__()
        self.downloader = downloader
        self.update_table_callback = update_table_callback

    def run(self):
        self.downloader.download_images(self.update_table_callback)
        self.finished.emit([1, 2, 3])

    def update_table(self, title, status):
        self.progress.emit(title, status)

class ImageDownloaderUI(QWidget):
    start_download_signal = pyqtSignal(str, str, int, bool, bool, bool)
    select_folder_signal = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Image Hunter")
        self.setGeometry(100, 100, 1200, 700)
        self.layout = QVBoxLayout()

        self.label = QLabel("Nhập username Instagram và chọn số lượng ảnh để tải.")
        self.label.setFixedSize(600, 50)
        self.label.setStyleSheet("font-size: 18px; font-weight: bold;")
        
        font = QFont()
        font.setPointSize(18)
        font.setBold(True)
        self.label.setFont(font)
        
        self.layout.addWidget(self.label)
        
        

        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Nhập tên người muốn tải")
        self.layout.addWidget(self.username_input)

        self.num_images_input = QSpinBox()
        self.num_images_input.setRange(1, 100)
        self.num_images_input.setValue(10)
        self.layout.addWidget(self.num_images_input)

        self.folder_layout = QHBoxLayout()
        self.folder_path_input = QLineEdit()
        self.folder_path_input.setPlaceholderText("Chọn thư mục lưu ảnh")
        self.folder_layout.addWidget(self.folder_path_input)

        self.select_folder_button = QPushButton("Chọn thư mục")
        self.select_folder_button.clicked.connect(self.select_folder)
        self.folder_layout.addWidget(self.select_folder_button)

        self.layout.addLayout(self.folder_layout)

        self.checkbox_layout = QHBoxLayout()
        self.square_checkbox = QCheckBox("Hình vuông")
        self.checkbox_layout.addWidget(self.square_checkbox)
        self.rectangle_checkbox = QCheckBox("Hình chữ nhật")
        self.checkbox_layout.addWidget(self.rectangle_checkbox)
        self.all_images_checkbox = QCheckBox("Tất cả ảnh")
        self.checkbox_layout.addWidget(self.all_images_checkbox)
        self.layout.addLayout(self.checkbox_layout)

        self.download_button = QPushButton("Tải ảnh")
        self.download_button.clicked.connect(self.start_download)
        self.layout.addWidget(self.download_button)

        self.table_widget = QTableWidget()
        self.table_widget.setColumnCount(2)
        self.table_widget.setHorizontalHeaderLabels(["Tên ảnh", "Trạng thái"])
        self.layout.addWidget(self.table_widget)

        self.setLayout(self.layout)

    def select_folder(self):
        folder_path = QFileDialog.getExistingDirectory(self, "Chọn thư mục lưu ảnh")
        if folder_path:
            self.folder_path_input.setText(folder_path)

    def start_download(self):
        username = self.username_input.text()
        folder_path = self.folder_path_input.text()
        num_images = self.num_images_input.value()
        download_square = self.square_checkbox.isChecked()
        download_rectangle = self.rectangle_checkbox.isChecked()
        download_all = self.all_images_checkbox.isChecked()
        self.start_download_signal.emit(username, folder_path, num_images, download_square, download_rectangle, download_all)

    def update_table(self, title, status):
        row_position = self.table_widget.rowCount()
        self.table_widget.insertRow(row_position)

        # Tạo QTableWidgetItem cho tên ảnh và trạng thái
        title_item = QTableWidgetItem(title)
        status_item = QTableWidgetItem(status)

        # Đặt màu theo trạng thái
        if status == "Thành công":
            status_item.setForeground(QColor("green"))
        elif status in ["Lỗi khi tải", "Lỗi khi lưu"]:
            status_item.setForeground(QColor("red"))
        else:
            status_item.setForeground(QColor("orange"))

        # Thêm các item vào bảng
        self.table_widget.setItem(row_position, 0, title_item)
        self.table_widget.setItem(row_position, 1, status_item)

        # Cập nhật kích thước cột
        self.table_widget.resizeColumnsToContents()

