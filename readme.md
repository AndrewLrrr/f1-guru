# F1 Guru

Проект представляет собой попытку интеллектуального анализа прошедших результатов гонок Формулы-1 с целью предсказания результатов будущих гонок при помощи методов машинного обучения.

Основная цель проекта - на практике познакомиться с процессом Data mining от извлечения данных из неструктурированных источников до построения моделей по ним.

В рамках проекта были созданы инструменты позволяющие извлекать и систематизировать необходимые данные из интернета, а также проведено [исследование](https://github.com/AndrewLrrr/f1-guru/blob/master/f1-guru.ipynb) данных и построена модель предсказывающая результаты.

Система сбора данных поддерживает следующие команды:

```
>> python3 main.py [testing|racing|team] [year_from] [year_to]
```
Генерирует датасеты [тестов|гонок|составов команд] в указанном промежутке времени в годах.

Если никаки параметров не задано, то генерирует все датасеты за 2014-2017 год

-----------------------------------------------------------------------------------

```
>> python3 main.py race-blank|race-result year number
```
Генерирует датасет для каждой отдельной гонки, в случае race-blank - датасет содержит все необходиые для модели признаки.

В случае race-result - датасет содаржит результаты гонки.

year - Год проведения чемпионата.

num - Порядковый номер этапа в календаре чемпионата.

-----------------------------------------------------------------------------------

Также стоит отметить, что система сбора данных по умолчанию работает через прокси сервера, это может быть существенно медленнее, чем прямое соединение. Чтобы отключить проксирование запросов, в файле `settings.py` необходимо выставить `USE_PROXY = False`.

С другой стороны, все запросы кешируются, поэтому скачав данные один раз больше этого делать не понадобится.