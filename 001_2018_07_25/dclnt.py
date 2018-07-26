import ast
import os
import collections
import sys

from nltk import pos_tag


def flat(_list):
    """ [(1,2), (3,4)] -> [1, 2, 3, 4]"""
    return sum([list(item) for item in _list], [])


def is_verb(word):
    if not word:
        return False
    pos_info = pos_tag([word])
    return pos_info[0][1] == 'VB'


def raw(x):
    return x


# Будет использоваться у
# + get_verbs_from_function_name
# + split_snake_case_name_to_words


def filtered_split(statement, sep=None, filter_function=None):
    """
    Будет использоваться у
    + get_verbs_from_function_name
    + split_snake_case_name_to_words
    :param statement: исходное выражение
    :param sep: разделитель для split
    :param filter_function: функция фильтрации
    :return:
    """
    if sep is None:
        sep = '_'
    if filter_function is None:
        filter_function = raw
    return [_part for _part in statement.split(sep) if filter_function(_part)]


# Ver.0
# Path = ''


def get_trees(_path, with_filenames=None, with_file_content=None):
    # Выявлено, что _path не используется, но я не трогал логику,
    # так как возможно предполагается, что get_trees может УЖЕ вызываться чем-то сторонним

    # Я обычно так инициализирую значения по умолчанию
    if with_filenames is None:
        with_filenames = False
    if with_file_content is None:
        with_file_content = False
    filenames = []
    trees = []
    # Ver.0
    # path = Path
    # for dirname, dirs, files in os.walk(path, topdown=True):
    for dirname, dirs, files in os.walk(_path, topdown=True):
        for file in files:
            if file.endswith('.py'):
                filenames.append(os.path.join(dirname, file))
                # Могу 100 вынести в kwargs
                if len(filenames) == 100:
                    break
    print('total %s files' % len(filenames))
    for filename in filenames:
        with open(filename, 'r', encoding='utf-8') as attempt_handler:
            main_file_content = attempt_handler.read()
        try:
            tree = ast.parse(main_file_content)
        except SyntaxError as e:
            print(e)
            tree = None
        # Можно снизить вложенность последующего, просто вынеся в функцию
        # не будет if if else else тут, а только вызов функции
        if with_filenames:
            if with_file_content:
                trees.append((filename, main_file_content, tree))
            else:
                trees.append((filename, tree))
        else:
            trees.append(tree)
    print('trees generated')
    return trees


# node_attr_function в get_nodes_attr для get_all_names
def get_node_id(node):
    return node.id


# node_attr_function в get_nodes_attr для get_nodes_names_at_lowercase
def get_node_lowercase_name(node):
    return node.name.lower()


# filter_node_function
def is_ast_name(node):
    return isinstance(node, ast.Name)


# filter_node_function
def is_ast_function_def(node):
    return isinstance(node, ast.FunctionDef)


def get_nodes_attr(_tree, node_attr_function, filter_node_function):
    return [node_attr_function(node) for node in ast.walk(_tree) if filter_node_function(node)]


def get_nodes_names_at_lowercase(_tree):
    return get_nodes_attr(_tree, node_attr_function=get_node_lowercase_name, filter_node_function=is_ast_function_def)


def get_all_names(tree):
    # Ver.0
    # return [node.id for node in ast.walk(tree) if isinstance(node, ast.Name)]
    return get_nodes_attr(tree, node_attr_function=get_node_id, filter_node_function=is_ast_name)


def get_verbs_from_function_name(function_name):
    # Ver.0
    # return [word for word in function_name.split('_') if is_verb(word)]
    return filtered_split(function_name, is_verb)


def split_snake_case_name_to_words(name):
    # Ver.0
    # return [n for n in name.split('_') if n]
    return filtered_split(name)


def get_trees_nodes_with_powered_function_apply(trees, powered_function):
    function_names = [
        f for f in flat(
            [
                powered_function(t) for t in trees
            ]
        ) if not (f.startswith('__') and f.endswith('__'))
    ]
    return function_names


def get_all_words_in_path(path):
    trees = [t for t in get_trees(path) if t]
    # Ver.0
    # function_names = [f for f in flat([get_all_names(t) for t in trees]) if
    #                   not (f.startswith('__') and f.endswith('__'))]
    function_names = get_trees_nodes_with_powered_function_apply(trees, get_all_names)
    return flat([split_snake_case_name_to_words(function_name) for function_name in function_names])


def get_functions_names_at_lowercase_in_trees(trees):
    # Ver.0
    # function_names = [
    #     f for f in flat(
    #         [
    #             [
    #                 node.name.lower() for node in ast.walk(t) if isinstance(node, ast.FunctionDef)
    #             ] for t in trees
    #         ]
    #     ) if not (f.startswith('__') and f.endswith('__'))
    # ]
    # Ver.1
    # function_names = [
    #     f for f in flat(
    #         [
    #             get_nodes_attr(t, node_function=get_node_lowercase_name, filter_node_function=is_ast_function_def)
    #             for t in trees
    #         ]
    #     ) if not (f.startswith('__') and f.endswith('__'))
    # ]
    # Ver.2
    # function_names = [
    #     f for f in flat(
    #         [
    #             get_nodes_names_at_lowercase(t) for t in trees
    #         ]
    #     ) if not (f.startswith('__') and f.endswith('__'))
    # ]
    function_names = get_trees_nodes_with_powered_function_apply(trees, get_nodes_names_at_lowercase)
    return function_names


def get_top_verbs_in_path(path, top_size=None):
    # Я обычно так инициализирую значения по умолчанию
    if top_size is None:
        top_size = 10

    # Ver.0
    # global Path
    # Path = path
    # trees = [t for t in get_trees(None) if t]
    # Ver.1
    trees = [t for t in get_trees(path) if t]

    # Ver.0
    # fncs = [f for f in
    #         flat([[node.name.lower() for node in ast.walk(t) if isinstance(node, ast.FunctionDef)] for t in trees]) if
    #         not (f.startswith('__') and f.endswith('__'))]
    # Ver.1
    fncs = get_functions_names_at_lowercase_in_trees(trees)
    print('functions extracted')
    verbs = flat([get_verbs_from_function_name(function_name) for function_name in fncs])
    return collections.Counter(verbs).most_common(top_size)


def get_top_functions_names_in_path(path, top_size=None):
    # Я обычно так инициализирую значения по умолчанию
    if top_size is None:
        top_size = 10
    t = get_trees(path)
    # Ver.0
    # nms = [f for f in
    #        flat([[node.name.lower() for node in ast.walk(t) if isinstance(node, ast.FunctionDef)] for t in t]) if
    #        not (f.startswith('__') and f.endswith('__'))]
    # return collections.Counter(nms).most_common(top_size)
    nms = get_functions_names_at_lowercase_in_trees(t)
    return collections.Counter(nms).most_common(top_size)


# Можно передавать директорию в качетве sys.args[0]
# c if __name__ == '__main__':
if __name__ == '__main__':

    base_path = sys.argv[1] if len(sys.argv) >= 2 else '.'

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
        # Ver.0
        # path = os.path.join('.', project)
        # Ver.1
        path = os.path.join(base_path, project)
        wds += get_top_verbs_in_path(path)

    # Ver.0
    # top_size = 200
    # Ver.1
    top_size = sys.argv[2] if len(sys.argv) >= 3 else 200
    print('total %s words, %s unique' % (len(wds), len(set(wds))))
    for word, occurence in collections.Counter(wds).most_common(top_size):
        print(word, occurence)
