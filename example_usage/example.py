import os
import collections
import sys
import logging

from static_code_terms_analyzer.scta import (
    get_top_verbs_in_path,
)

rootLogger = logging.getLogger('SCTA')
rootLogger.setLevel(logging.INFO)
logFormatter = logging.Formatter("[%(asctime)s] %(filename)-15s %(levelname)-8s %(message)s")

consoleHandler = logging.StreamHandler()
consoleHandler.setFormatter(logFormatter)
consoleHandler.setLevel(logging.INFO)
rootLogger.addHandler(consoleHandler)


if __name__ == '__main__':

    base_path = sys.argv[1] if len(sys.argv) >= 2 else '.'
    limit_top_size = sys.argv[2] if len(sys.argv) >= 3 else 200

    limit_top_size_partitions_of_verbs = []
    projects = [
        'django',
        'flask',
        'pyramid',
        'reddit',
        'requests',
        'sqlalchemy',
    ]
    for project in projects:
        path_to_analyze = os.path.join(base_path, project)
        limit_top_size_partitions_of_verbs += get_top_verbs_in_path(path_to_analyze)

    rootLogger.info(
        'total: %s words, %s unique' % (
            len(limit_top_size_partitions_of_verbs),
            len(set(limit_top_size_partitions_of_verbs))
        )
    )

    for word_item, occurence in collections.Counter(limit_top_size_partitions_of_verbs).most_common(limit_top_size):
        rootLogger.info(
            '%s: %s' % (
                word_item,
                occurence
            )
        )
