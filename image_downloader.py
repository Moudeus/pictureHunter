import instaloader
import os
import requests
from PIL import Image
from io import BytesIO
import re
from threading import Semaphore

class ImageDownloader:
    def __init__(self, username, folder_path, max_images, download_square, download_rectangle, download_all, insta_username=None, insta_password=None):
        self.semaphore = Semaphore(5)  # Giới hạn tối đa 5 kết nối đồng thời
        self.username = username
        self.folder_path = folder_path
        self.max_images = max_images
        self.download_square = download_square
        self.download_rectangle = download_rectangle
        self.download_all = download_all
        self.insta_username = insta_username
        self.insta_password = insta_password
        self.loader = instaloader.Instaloader()

    def sanitize_filename(self, filename):
        invalid_chars = r'[<>:"/\\|?*]'
        filename = re.sub(invalid_chars, '_', filename)
        return filename[:100]

    def download_image(self, title, image_url, update_table_callback, suffix=""):
        title = self.sanitize_filename(title) + suffix
        filename = os.path.join(self.folder_path, f"{title}.jpg")

        with self.semaphore:  # Giới hạn số lượng kết nối đồng thời
            response = requests.get(image_url)
            if response.status_code == 200:
                img = Image.open(BytesIO(response.content))
                width, height = img.size
                is_square = abs(width - height) <= 10

                if self.download_all:
                    if (self.download_square and is_square) or (self.download_rectangle and not is_square):
                        try:
                            img.save(filename)
                            update_table_callback(title, "Thành công")
                        except OSError as e:
                            update_table_callback(title, "Lỗi khi lưu")
                    else:
                        try:
                            img.save(filename)
                            update_table_callback(title, "Thành công")
                        except OSError as e:
                            update_table_callback(title, "Lỗi khi lưu")
                else:
                    # Nếu không chọn "Tất cả ảnh", tải ảnh đầu tiên mà không xét kích thước
                    if (not self.download_square and not self.download_rectangle) or \
                    (self.download_square and is_square) or \
                    (self.download_rectangle and not is_square):
                        try:
                            img.save(filename)
                            update_table_callback(title, "Thành công")
                        except OSError as e:
                            update_table_callback(title, "Lỗi khi lưu")
                    else:
                        update_table_callback(title, "Kích thước không phù hợp")
            else:
                update_table_callback(title, "Lỗi khi tải")

    def login(self):
        if self.insta_username and self.insta_password:
            try:
                self.loader.load_session_from_file(self.insta_username)
            except FileNotFoundError:
                self.loader.login(self.insta_username, self.insta_password)
                self.loader.save_session_to_file()

    def download_images(self, update_table_callback):
        self.login()
        os.makedirs(self.folder_path, exist_ok=True)

        try:
            count = 0
            for post in instaloader.Profile.from_username(self.loader.context, self.username).get_posts():
                if count >= self.max_images:
                    break
                caption = post.caption if post.caption else "instagram_post"
                title = " ".join(caption.split()[:10])

                if post.mediacount > 1:
                    if self.download_all:
                        for i, node in enumerate(post.get_sidecar_nodes()):
                            if count >= self.max_images:
                                break
                            image_url = node.display_url
                            suffix = f"_image{i+1}"
                            self.download_image(title, image_url, update_table_callback, suffix)
                            count += 1
                    else:
                        image_url = post.url  # Tải ảnh đầu tiên
                        self.download_image(title, image_url, update_table_callback)
                        count += 1
                else:
                    first_image_url = post.url
                    if count < self.max_images:
                        self.download_image(title, first_image_url, update_table_callback)
                        count += 1
        except Exception as e:
            update_table_callback("Có vấn đề", "Lỗi xảy ra")
