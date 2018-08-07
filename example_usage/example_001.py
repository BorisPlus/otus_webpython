import sys
import logging

from static_code_terms_analyzer.scta import (
    get_top_verbs_of_functions_names_in_path,
    get_top_nouns_of_variables_names_in_path,
    get_top_words_in_path
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

    # [2018-08-07 22:48:31,029] LOGGER: "scta.example_usage.001" RUN: example_001.py  INFO     TOTAL TOP FUNCTION VERBS: 5 words
    # [2018-08-07 22:48:31,030] LOGGER: "scta.example_usage.001" RUN: example_001.py  INFO     get: 35
    # [2018-08-07 22:48:31,030] LOGGER: "scta.example_usage.001" RUN: example_001.py  INFO     is: 8
    # [2018-08-07 22:48:31,030] LOGGER: "scta.example_usage.001" RUN: example_001.py  INFO     filtered: 2
    # [2018-08-07 22:48:31,030] LOGGER: "scta.example_usage.001" RUN: example_001.py  INFO     apply: 2
    # [2018-08-07 22:48:31,030] LOGGER: "scta.example_usage.001" RUN: example_001.py  INFO     applied: 1

    top_limit = 5
    limited_partition_of_words = get_top_nouns_of_variables_names_in_path(path_to_analyze, top_limit=top_limit)

    rootLogger.info(
        'TOTAL TOP %s NOUNS: %s words' % (
            top_limit,
            len(limited_partition_of_words)
        )
    )

    for word_item, occurence in limited_partition_of_words:
        rootLogger.info(
            '%s: %s' % (
                word_item,
                occurence
            )
        )

    # [2018-08-07 22:48:31,232] LOGGER: "scta.example_usage.001" RUN: example_001.py  INFO     TOTAL TOP 5 NOUNS: 5 words
    # [2018-08-07 22:48:31,232] LOGGER: "scta.example_usage.001" RUN: example_001.py  INFO     statements: 30
    # [2018-08-07 22:48:31,232] LOGGER: "scta.example_usage.001" RUN: example_001.py  INFO     trees: 29
    # [2018-08-07 22:48:31,232] LOGGER: "scta.example_usage.001" RUN: example_001.py  INFO     path: 26
    # [2018-08-07 22:48:31,232] LOGGER: "scta.example_usage.001" RUN: example_001.py  INFO     function: 25
    # [2018-08-07 22:48:31,232] LOGGER: "scta.example_usage.001" RUN: example_001.py  INFO     names: 25

    #

    top_limit = 5
    limited_partition_of_words = get_top_words_in_path(path_to_analyze, top_limit=top_limit)

    rootLogger.info(
        'TOTAL TOP %s WORDS: %s words' % (
            top_limit,
            len(limited_partition_of_words))
    )

    for word_item, occurence in limited_partition_of_words:
        rootLogger.info(
            '%s: %s' % (
                word_item,
                occurence
            )
        )

        # [2018-08-07 22:48:31,497] LOGGER: "scta.example_usage.001" RUN: example_001.py  INFO     TOTAL TOP 5 WORDS: 5 words
        # [2018-08-07 22:48:31,497] LOGGER: "scta.example_usage.001" RUN: example_001.py  INFO     path: 37
        # [2018-08-07 22:48:31,497] LOGGER: "scta.example_usage.001" RUN: example_001.py  INFO     trees: 36
        # [2018-08-07 22:48:31,497] LOGGER: "scta.example_usage.001" RUN: example_001.py  INFO     statements: 35
        # [2018-08-07 22:48:31,497] LOGGER: "scta.example_usage.001" RUN: example_001.py  INFO     names: 35
        # [2018-08-07 22:48:31,497] LOGGER: "scta.example_usage.001" RUN: example_001.py  INFO     function: 33
