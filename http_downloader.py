import requests
import threading
import time
import sys
import os

class DownloadTracker:
    def __init__(self):
        self.downloaded_bytes = 0
        self.lock = threading.Lock()
        self.is_downloading = True

    def update_bytes(self, chunk_size):
        with self.lock:
            self.downloaded_bytes += chunk_size

    def get_bytes(self):
        with self.lock:
            return self.downloaded_bytes

def progress_reporter(tracker):
    while tracker.is_downloading:
        print(f"Скачано байт: {tracker.get_bytes():,}", end="\r")
        time.sleep(1)
    print()

def download_file(url):
    tracker = DownloadTracker()
    
    progress_thread = threading.Thread(target=progress_reporter, args=(tracker,))
    progress_thread.start()

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Referer': url
    }

    try:
        response = requests.get(url, headers=headers, stream=True, allow_redirects=True)
        response.raise_for_status()

        content_disposition = response.headers.get('Content-Disposition')
        if content_disposition and 'filename=' in content_disposition:
            filename = content_disposition.split('filename=')[-1].strip('"\'')
        else:
            filename = os.path.basename(url.split('?')[0])
            if not filename:
                filename = 'downloaded_file'
        
        print(f"Сохранение в файл: {filename}")
        
        with open(filename, 'wb') as file:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    file.write(chunk)
                    tracker.update_bytes(len(chunk))

    except requests.exceptions.HTTPError as e:
        print(f"\nОшибка HTTP: {e}")
        sys.exit(1)
    except requests.exceptions.RequestException as e:
        print(f"\nОшибка при скачивании: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\nНеожиданная ошибка: {e}")
        sys.exit(1)
    finally:
        tracker.is_downloading = False
        progress_thread.join()

def main():
    if len(sys.argv) != 2:
        print("Использование: python http_downloader.py <URL>")
        sys.exit(1)

    url = sys.argv[1]
    print(f"Начинаю скачивание файла с {url}")
    download_file(url)
    print("\nСкачивание завершено!")

if __name__ == "__main__":
    main()
