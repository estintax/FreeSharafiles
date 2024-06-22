import threading
from concurrent.futures import ThreadPoolExecutor
from itertools import repeat

import requests
import json
import signal
import gzip
import os

THREADS = 16
SHARABALL_BASE_URI = "https://shararam.ru"
PROCESSING = True
DOWNLOAD_COUNTER = 0


# Хандлер нажатия на Ctrl+C
def signal_handler(signum, frame):
    global PROCESSING
    PROCESSING = False
    exit(1)


def download(url, length, thread_lock):
    global PROCESSING
    global DOWNLOAD_COUNTER

    if not PROCESSING:
        with thread_lock:
            print("Прерывание!")
        return

    file_path = "./output/fs/{}".format(url)

    if os.path.exists(file_path):
        with thread_lock:
            print("Файл {} уже загружен ({}/{})".format(url, DOWNLOAD_COUNTER, length))
            DOWNLOAD_COUNTER += 1
        return

    try:
        response = requests.get("{}/fs/{}".format(SHARABALL_BASE_URI, url), headers={
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/103.0.0.0 Safari/537.36'})
        response.raise_for_status()

        with open(file_path, "wb") as f:
            f.write(response.content)

        with thread_lock:
            print("Скачан файл {} ({}/{})".format(url, DOWNLOAD_COUNTER, length))
            DOWNLOAD_COUNTER += 1
    except requests.exceptions.RequestException:
        with thread_lock:
            print("Не удалось загрузить файл {}! ({}/{})".format(url, DOWNLOAD_COUNTER, length))


def main():
    # Регистрация обработки прерываний
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    print("FreeSharaFiles (c) 2022 Maksim Pinigin")
    print("Лучше поздно, чем никогда")

    # Получения списка дампов хранилища
    r = requests.get("https://pinig.in/nsf/storages.php")
    storages = r.json()
    latest = storages["latest"]
    latest_id = 0
    # Построение списка
    print("Дампы хранилища:")
    storages_arr = {}
    i = 1
    for storage in storages["storages"]:
        storages_arr[str(i)] = storage
        if storage["date"] == latest:
            latest_id = i
        print("[{}] {}".format(i, storage["date"]))
        i = i + 1
    input_text = input("Выберите нужную дату дампа, или нажмите Enter для загрузки последнего: [{}] ".format(latest_id))
    if input_text != "" and input_text not in storages_arr:
        print("Неверный ввод")
        exit(1)

    if input_text == "":
        input_text = str(latest_id)

    # Получение списка файлов
    print("Получение списка файлов...")
    storage = []
    try:
        r = requests.get(storages_arr[input_text]["url"])
        storage = json.loads(gzip.decompress(r.content))
    except:
        print("Неудачно! Попробуйте в другой раз")
        exit(2)

    # Создание папок для загрузки файлов
    if not os.path.exists("./output"):
        os.mkdir("./output")
        print("Создан каталог ./output")
    if not os.path.exists("./output/fs"):
        os.mkdir("./output/fs")
        print("Создан каталог ./output/fs")

    # Устарело
    # f = gzip.open("./storage.dat", "r")
    # storage = json.loads(f.read())
    # f.close()

    # Вывод информации
    print("Дата хранилища: {}".format(storage[0]))
    print("Всего файлов для загрузки: {}+2".format(len(storage) - 2))

    # Загрузка отсутствующего в дампе файла
    f = open("./output/fs/3p897j5lf4e0j.swf", "wb")
    r = requests.get("{}/fs/{}".format(SHARABALL_BASE_URI, "3p897j5lf4e0j.swf"), headers={
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/103.0.0.0'
                      'Safari/537.36'})
    f.write(r.content)
    f.close()
    print("Скачан файл {}".format("3p897j5lf4e0j.swf"))

    # Загрузка base.swf
    f = open("./output/base.swf", "wb")
    r = requests.get("{}/{}".format(SHARABALL_BASE_URI, "base.swf"), headers={
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/103.0.0.0'
                      'Safari/537.36'})
    f.write(r.content)
    f.close()
    print("Скачан файл {}".format("base.swf"))

    # Скачивание файлов
    print("Продолжаю скачивание в {} потоков".format(THREADS))
    thread_lock = threading.Lock()

    with ThreadPoolExecutor(max_workers=THREADS) as executor:
        executor.map(download, storage, repeat(len(storage) - 1), repeat(thread_lock))

    if PROCESSING:
        print("Готово!")


if __name__ == '__main__':
    main()
