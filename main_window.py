# main_window.py
import sys
from PyQt5.QtWidgets import QApplication, QMessageBox
from image_downloader import ImageDownloader
from gui import ImageDownloaderUI, ImageDownloadThread
from PyQt5.QtCore import QThread

def on_download_finished():
    ui.label.setText("Tải ảnh hoàn tất!")
    QMessageBox.information(ui, "Hoàn tất", "Tải ảnh hoàn tất!")

def start_download(username, folder_path, num_images, download_square, download_rectangle, download_all):
    if not username:
        QMessageBox.warning(ui, "Cảnh báo", "Vui lòng nhập tên người dùng!")
        return
    if not folder_path:
        QMessageBox.warning(ui, "Cảnh báo", "Vui lòng chọn thư mục lưu ảnh!")
        return

    ui.label.setText("Đang tải ảnh...")

    # Tạo downloader
    downloader = ImageDownloader(username, folder_path, num_images, download_square, download_rectangle, download_all)

    # Tạo QThread và ImageDownloadThread
    thread = QThread()
    download_thread = ImageDownloadThread(downloader, ui.update_table)

    # Kết nối tín hiệu và di chuyển download_thread vào QThread
    download_thread.moveToThread(thread)
    download_thread.finished.connect(on_download_finished)
    download_thread.finished.connect(thread.quit)  # Dừng QThread khi xong việc
    thread.started.connect(download_thread.run)  # Bắt đầu download khi QThread chạy

    # Giữ tham chiếu để không bị thu hồi
    ui.download_thread = download_thread
    ui.thread = thread

    # Khởi động QThread
    thread.start()

app = QApplication(sys.argv)
ui = ImageDownloaderUI()
ui.start_download_signal.connect(start_download)
ui.show()
sys.exit(app.exec_())
