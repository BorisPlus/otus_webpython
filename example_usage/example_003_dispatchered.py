import sys
import logging

from static_code_terms_analyzer.scta import (
    get_top_terms_of_entities_in_path,
)

if __name__ == '__main__':

    rootLogger = logging.getLogger('scta.example_usage.003')
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
    term_type = sys.argv[3] if len(sys.argv) >= 4 else 'verb'
    entity_type = sys.argv[4] if len(sys.argv) >= 5 else 'default'

    #

    limited_partition_of_words = get_top_terms_of_entities_in_path(
        path_to_analyze,
        term_type=term_type,
        entity_type=entity_type
    )

    rootLogger.info(
        'TOTAL TOP "%s" of "%s": %s words, %s unique' % (
            term_type,
            entity_type,
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
