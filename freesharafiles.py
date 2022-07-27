import requests
import json
import signal
import gzip
import os

processing = True

# Хандлер нажатия на Ctrl+C
def signal_handler(signum, frame):
    global processing
    processing = False
    exit(1)

# Регистрация обработки прерываний
signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

print("FreeSharaFiles (c) 2022 Maksim Pinigin")
print("Лучше поздно, чем никогда")

# Получения списка дампов хранилища
r = requests.get("https://sdirg.eix.by/nsf/storages.php")
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
    i = i+1
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
#f = gzip.open("./storage.dat", "r")
#storage = json.loads(f.read())
#f.close()

# Вывод информации
print("Дата хранилища: {}".format(storage[0]))
print("Всего файлов для загрузки: {}+2".format(len(storage)-2))

# Загрузка отсутствующего в дампе файла
f = open("./output/fs/3p897j5lf4e0j.swf", "wb")
r = requests.get("https://sharaball.ru/fs/{}".format("3p897j5lf4e0j.swf"), headers={'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36'})
f.write(r.content)
f.close()
print("Скачан файл {}".format("3p897j5lf4e0j.swf"))

# Загрузка base.swf
f = open("./output/base.swf", "wb")
r = requests.get("https://sharaball.ru/{}".format("base.swf"), headers={'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36'})
f.write(r.content)
f.close()
print("Скачан файл {}".format("base.swf"))

# Скачивание файлов по очереди
i = 0
for url in storage:
    if not processing:
        print("Прерывание!")
        break
    if i == 0:
        i += 1
        continue
    try:
        if os.path.exists("./output/fs/{}".format(url)):
            print("Файл {} уже загружен ({}/{})".format(url, i, len(storage)-1))
            i += 1
            continue
        f = open("./output/fs/{}".format(url), "wb")
        r = requests.get("https://sharaball.ru/fs/{}".format(url), headers={'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36'})
        f.write(r.content)
        f.close()
        del r
        print("Скачан файл {} ({}/{})".format(url, i, len(storage)-1))
    except:
        print("Неудалось загрузить файл {}! ({}/{})".format(url, i, len(storage)))
        try:
            f.close()
        except:
            pass
        os.remove("./output/fs/{}".format(url))
        
    i += 1

if processing:
    print("Готово!")
