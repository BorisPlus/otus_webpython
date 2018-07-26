import ast
import os
import collections

from nltk import pos_tag


def flat(_list):
    """ [(1,2), (3,4)] -> [1, 2, 3, 4]"""
    return sum([list(item) for item in _list], [])


def is_verb(_word):
    if not _word:
        return False
    pos_info = pos_tag([_word])
    return pos_info[0][1] == 'VB'


def filter_function_raw(x):
    return x


def filtered_split(name, sep=None, filter_function=None):
    if sep is None:
        sep = '_'
    if filter_function is None:
        filter_function = filter_function_raw
    return [_part for _part in name.split(sep) if filter_function(_part)]


def split_snake_case_name_to_words(name):
    return filtered_split(name)


def get_verbs_from_function_name(function_name):
    return filtered_split(function_name, filter_function=is_verb)


def get_all_names(_tree):
    return [node.id for node in ast.walk(_tree) if isinstance(node, ast.Name)]


# Path = ''


def get_trees(_path=None, with_file_names=None, with_file_content=None, top_count=None):
    if _path is None:
        _path = ''
    if top_count is None:
        top_count = -1
    if with_file_names is None:
        with_file_names = False
    if with_file_content is None:
        with_file_content = False
    file_names = []
    trees = []
    # path = Path
    for dir_name, dirs, files in os.walk(_path, topdown=True):
        for file in files:
            if file.endswith('.py'):
                file_names.append(os.path.join(dir_name, file))
                if len(file_names) == top_count and top_count >= 0:
                    break
    print('total %s files' % len(file_names))
    for file_name in file_names:
        with open(file_name, 'r', encoding='utf-8') as attempt_handler:
            main_file_content = attempt_handler.read()
        try:
            tree = ast.parse(main_file_content)
        except SyntaxError as e:
            print(e)
            tree = None
        if with_file_names:
            if with_file_content:
                trees.append((file_name, main_file_content, tree))
            else:
                trees.append((file_name, tree))
        else:
            trees.append(tree)
    print('trees generated')
    return trees


def get_all_words_in_path(_path):
    trees = get_trees(_path)
    function_names = [
        f for f in flat([get_all_names(t) for t in trees]) if
        not (f.startswith('__') and f.endswith('__'))
    ]
    return flat([split_snake_case_name_to_words(function_name) for function_name in function_names])


def get_functions_names_in_path(_path):
    trees = get_trees(_path)
    function_names = [
        f for f in flat(
            [
                [
                    node.name.lower() for node in ast.walk(t) if isinstance(node, ast.FunctionDef)
                ] for t in trees
            ]
        ) if not (f.startswith('__') and f.endswith('__'))
    ]
    return function_names


def get_top_functions_names_in_path(_path, top_count=10):
    function_names = get_functions_names_in_path(_path)
    return collections.Counter(function_names).most_common(top_count)


def get_top_verbs_in_path(_path, top_count=10):
    function_names = get_functions_names_in_path(_path)
    print('functions extracted')
    verbs = flat([get_verbs_from_function_name(function_name) for function_name in function_names])
    return collections.Counter(verbs).most_common(top_count)

wds = []
projects = [
    'django',
    'flask',
    'pyramid',
    'reddit',
    'requests',
    'sqlalchemy',
]
for project in projects:
    path = os.path.join('.', project)
    wds += get_top_verbs_in_path(path)

top_size = 200
print('total %s words, %s unique' % (len(wds), len(set(wds))))
for word, occurence in collections.Counter(wds).most_common(top_size):
    print(word, occurence)
