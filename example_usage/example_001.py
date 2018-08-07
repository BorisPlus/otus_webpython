import sys
import logging

from static_code_terms_analyzer.scta import (
    get_top_verbs_at_functions_names_in_path,
    get_top_nouns_at_variables_names_in_path,
    get_top_words_in_path
)

rootLogger = logging.getLogger('SCTA')
rootLogger.setLevel(logging.INFO)
while rootLogger.handlers:
    rootLogger.handlers.pop()
logFormatter = logging.Formatter("[%(asctime)s] %(filename)-15s %(levelname)-8s %(message)s")

consoleHandler = logging.StreamHandler()
consoleHandler.setFormatter(logFormatter)
consoleHandler.setLevel(logging.INFO)
rootLogger.addHandler(consoleHandler)

if __name__ == '__main__':

    path_to_analyze = sys.argv[1] if len(sys.argv) >= 2 else '../static_code_terms_analyzer'
    limit_top_size = int(sys.argv[2]) if len(sys.argv) >= 3 and sys.argv[2].isdigit() else 10

    #

    limited_partition_of_words = get_top_verbs_at_functions_names_in_path(path_to_analyze)

    rootLogger.info(
        'TOTAL TOP VERBS: %s words, %s unique' % (
            len(limited_partition_of_words),
            len(set(limited_partition_of_words))
        )
    )

    for word_item, occurence in limited_partition_of_words:
        rootLogger.info(
            '%s: %s' % (
                word_item,
                occurence
            )
        )

    # [2018-08-07 17:45:22,394] example_001.py  INFO     TOTAL TOP 10 NOUNS: 10 words, 10 unique
    # [2018-08-07 17:45:22,394] example_001.py  INFO     path: 32
    # [2018-08-07 17:45:22,395] example_001.py  INFO     self: 30
    # [2018-08-07 17:45:22,395] example_001.py  INFO     files: 28
    # [2018-08-07 17:45:22,395] example_001.py  INFO     file: 26
    # [2018-08-07 17:45:22,395] example_001.py  INFO     source: 23
    # [2018-08-07 17:45:22,395] example_001.py  INFO     trees: 22
    # [2018-08-07 17:45:22,395] example_001.py  INFO     names: 21
    # [2018-08-07 17:45:22,395] example_001.py  INFO     target: 20
    # [2018-08-07 17:45:22,395] example_001.py  INFO     os: 19
    # [2018-08-07 17:45:22,395] example_001.py  INFO     list: 18

    #

    top_limit = 10
    limited_partition_of_words = get_top_nouns_at_variables_names_in_path(path_to_analyze, top_limit=top_limit)

    rootLogger.info(
        'TOTAL TOP %s NOUNS: %s words, %s unique' % (
            top_limit,
            len(limited_partition_of_words),
            len(set(limited_partition_of_words))
        )
    )

    for word_item, occurence in limited_partition_of_words:
        rootLogger.info(
            '%s: %s' % (
                word_item,
                occurence
            )
        )

    # [2018-08-07 17:45:22,394] example_001.py  INFO     TOTAL TOP 10 NOUNS: 10 words, 10 unique
    # [2018-08-07 17:45:22,394] example_001.py  INFO     path: 32
    # [2018-08-07 17:45:22,395] example_001.py  INFO     self: 30
    # [2018-08-07 17:45:22,395] example_001.py  INFO     files: 28
    # [2018-08-07 17:45:22,395] example_001.py  INFO     file: 26
    # [2018-08-07 17:45:22,395] example_001.py  INFO     source: 23
    # [2018-08-07 17:45:22,395] example_001.py  INFO     trees: 22
    # [2018-08-07 17:45:22,395] example_001.py  INFO     names: 21
    # [2018-08-07 17:45:22,395] example_001.py  INFO     target: 20
    # [2018-08-07 17:45:22,395] example_001.py  INFO     os: 19
    # [2018-08-07 17:45:22,395] example_001.py  INFO     list: 18

    #

    top_limit = 15
    limited_partition_of_words = get_top_words_in_path(path_to_analyze, top_limit=top_limit)

    rootLogger.info(
        'TOTAL TOP %s WORDS: %s words, %s unique' % (
            top_limit,
            len(limited_partition_of_words),
            len(set(limited_partition_of_words))
        )
    )

    for word_item, occurence in limited_partition_of_words:
        rootLogger.info(
            '%s: %s' % (
                word_item,
                occurence
            )
        )

    # [2018-08-07 17:45:22,637] example_001.py  INFO     TOTAL TOP 15 WORDS: 15 words, 15 unique
    # [2018-08-07 17:45:22,637] example_001.py  INFO     path: 32
    # [2018-08-07 17:45:22,637] example_001.py  INFO     self: 30
    # [2018-08-07 17:45:22,637] example_001.py  INFO     files: 28
    # [2018-08-07 17:45:22,638] example_001.py  INFO     file: 26
    # [2018-08-07 17:45:22,638] example_001.py  INFO     source: 23
    # [2018-08-07 17:45:22,638] example_001.py  INFO     trees: 22
    # [2018-08-07 17:45:22,638] example_001.py  INFO     names: 21
    # [2018-08-07 17:45:22,638] example_001.py  INFO     target: 20
    # [2018-08-07 17:45:22,638] example_001.py  INFO     os: 19
    # [2018-08-07 17:45:22,638] example_001.py  INFO     list: 18
    # [2018-08-07 17:45:22,638] example_001.py  INFO     function: 17
    # [2018-08-07 17:45:22,638] example_001.py  INFO     rootlogger: 16
    # [2018-08-07 17:45:22,638] example_001.py  INFO     top: 15
    # [2018-08-07 17:45:22,638] example_001.py  INFO     name: 14
    # [2018-08-07 17:45:22,638] example_001.py  INFO     kwargs: 14
