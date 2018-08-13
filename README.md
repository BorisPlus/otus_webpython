# Static Code Terms Analyzer

Проект библиотеки по статическому анализу кода

## Как использовать

### Требования

Использует версию nltk==3.3 (http://www.nltk.org/)

```
pip3 install nltk==3.3
```

или

```
pip3 install -r requirements.txt
```

не забудте проверить

```bash
Please use the NLTK Downloader to obtain the resource:
python3
>>> import nltk
>>> nltk.download('averaged_perceptron_tagger')

  Searched in:
    - '/home/developer/nltk_data'
    - '/usr/share/nltk_data'
    - '/usr/local/share/nltk_data'
    - '/usr/lib/nltk_data'
    - '/usr/local/lib/nltk_data'
    - '/usr/nltk_data'
    - '/usr/share/nltk_data'
    - '/usr/lib/nltk_data'
```

если не сработает

```bash
>>> import nltk
>>> nltk.download('all')
```

### Установка

Скопируйте к себе в проект папку static_code_terms_analyzer или установите иным известным Вам и возможным образом.

### Примеры

См. директорию https://github.com/BorisPlus/otus_webpython_001/tree/master/example_usage

#### Пример №1

```python

import sys
import logging


from static_code_terms_analyzer.scta import (
    get_top_verbs_of_functions_names_in_path,
)

if __name__ == '__main__':

    rootLogger = logging.getLogger('scta.example_usage.001')
    rootLogger.setLevel(logging.INFO)
    while rootLogger.handlers:
        rootLogger.handlers.pop()
    logFormatter = logging.Formatter("[%(asctime)s] LOGGER: \"%(name)s\" "
                                     "RUN: %(filename)-15s %(levelname)-8s %(message)s")

    consoleHandler = logging.StreamHandler()
    consoleHandler.setFormatter(logFormatter)
    consoleHandler.setLevel(logging.INFO)
    rootLogger.addHandler(consoleHandler)

    path_to_analyze = sys.argv[1] if len(sys.argv) >= 2 else '../static_code_terms_analyzer'
    limit_top_size = int(sys.argv[2]) if len(sys.argv) >= 3 and sys.argv[2].isdigit() else 10

    #

    limited_partition_of_words = get_top_verbs_of_functions_names_in_path(path_to_analyze)

    rootLogger.info(
        'TOTAL TOP FUNCTION VERBS: %s words' % len(limited_partition_of_words)
    )

    for word_item, occurence in limited_partition_of_words:
        rootLogger.info(
            '%s: %s' % (
                word_item,
                occurence
            )
        )
```

РЕЗУЛЬТАТ

```
[2018-08-07 22:48:31,029] LOGGER: "scta.example_usage.001" RUN: example_001.py  INFO     TOTAL TOP FUNCTION VERBS: 5 words
[2018-08-07 22:48:31,030] LOGGER: "scta.example_usage.001" RUN: example_001.py  INFO     get: 35
[2018-08-07 22:48:31,030] LOGGER: "scta.example_usage.001" RUN: example_001.py  INFO     is: 8
[2018-08-07 22:48:31,030] LOGGER: "scta.example_usage.001" RUN: example_001.py  INFO     filtered: 2
[2018-08-07 22:48:31,030] LOGGER: "scta.example_usage.001" RUN: example_001.py  INFO     apply: 2
[2018-08-07 22:48:31,030] LOGGER: "scta.example_usage.001" RUN: example_001.py  INFO     applied: 1
```

#### Пример №2 (если в статическом коде есть ошибка)

```python
import os
import collections
import sys
import logging

from static_code_terms_analyzer.scta import (
    get_words_in_path,
)


if __name__ == '__main__':

    rootLogger = logging.getLogger('scta.example_usage.002')
    rootLogger.setLevel(logging.INFO)
    while rootLogger.handlers:
        rootLogger.handlers.pop()
    logFormatter = logging.Formatter("[%(asctime)s] LOGGER: \"%(name)s\" "
                                     "RUN: %(filename)-15s %(levelname)-8s %(message)s")

    consoleHandler = logging.StreamHandler()
    consoleHandler.setFormatter(logFormatter)
    consoleHandler.setLevel(logging.INFO)
    rootLogger.addHandler(consoleHandler)

    base_path = sys.argv[1] if len(sys.argv) >= 2 \
        else os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'downloads')
    limit_top_size = sys.argv[2] if len(sys.argv) >= 3 else 100

    limit_top_size_partitions_of_verbs = []
    projects = [
        'python-image-restoration',
    ]
    for project in projects:
        path_to_analyze = os.path.join(base_path, project)
        if os.path.exists(path_to_analyze):
            rootLogger.info('"%s" CHECKING' % path_to_analyze)
            limit_top_size_partitions_of_verbs.extend(
                get_words_in_path(path_to_analyze)
            )
        else:
            rootLogger.warning('"%s" NOT EXISTS' % path_to_analyze)

    rootLogger.info(
        'TOTAL: %s words, %s unique' % (
            len(limit_top_size_partitions_of_verbs),
            len(set(limit_top_size_partitions_of_verbs))
        )
    )
    for word_item, occurence in collections.Counter(limit_top_size_partitions_of_verbs).most_common(
            int(limit_top_size)
    ):
        rootLogger.info(
            '%s: %s' % (
                word_item,
                occurence
            )
        )
```

РЕЗУЛЬТАТ

```
[2018-08-07 22:54:59,442] LOGGER: "scta.example_usage.002" RUN: example_002.py  INFO     "/home/developer/PycharmProjects/otus_webpython_002/downloads/python-image-restoration" CHECKING
[2018-08-07 22:54:59,444] scta.py ERROR    Missing parentheses in call to 'print' (<unknown>, line 75)
[2018-08-07 22:54:59,445] LOGGER: "scta.example_usage.002" RUN: example_002.py  INFO     TOTAL: 0 words, 0 unique
```

#### Пример №3 (используя "супердиспетчер")

Комбинируя параметры диспетчера отчетов, такие как части речи (term_type:=['verb','noun','all']) или сущности кода (entity_type:=['variables','functions','all']), возможно получение стьатистического среза по любым сущностям и используемым в них частям речи. Результат этого примера идентичен Примеру №1.

```python
from static_code_terms_analyzer.scta import (
    get_top_terms_of_entities_in_path
)
...
    limited_partition_of_words = get_top_terms_of_entities_in_path(
        path_to_analyze,
        term_type='verbs',
        entity_type='functions'
    )
```


## Авторы

* **BorisPlus** - *Refactor work* - [BorisPlus](https://github.com/BorisPlus/otus_webpython_001)

## Лицензия

Огриничивается лицензиями используемых библиотек

## Дополнительные сведения

* Проект в рамках курса "Web-разработчик на Python" на https://otus.ru/learning

