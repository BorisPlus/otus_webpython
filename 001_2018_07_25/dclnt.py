import ast
import os
import collections
import sys

from nltk import pos_tag


def convert_to_flat(_list):
    """ [(1,2), (3,4)] -> [1, 2, 3, 4]"""
    return sum([list(item) for item in _list], [])


def is_verb(word):
    if not word:
        return False
    pos_info = pos_tag([word])
    return pos_info[0][1] == 'VB'


def get_raw(x):
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


def get_tree_of_file_content(file_content):
    try:
        return ast.parse(file_content)
    except SyntaxError as e:
        print(e)
        return


# для снижения вложенности, если было б нужно
def complex_append_to_list(list_of_elements, last_element, first_element, second_element):
    if first_element and second_element:
        list_of_elements.append((first_element, second_element, last_element))
    elif first_element and not second_element:
        list_of_elements.append((first_element, last_element))
    else:
        list_of_elements.append(last_element)


def get_trees(_path, with_file_names=None, with_file_content=None):
    # Выявлено, что _path не используется, но я не трогал логику,
    # так как возможно предполагается, что get_trees может УЖЕ вызываться чем-то сторонним

    # Я обычно так инициализирую значения по умолчанию
    if with_file_names is None:
        with_file_names = False
    if with_file_content is None:
        with_file_content = False
    files_names = []
    trees = []
    # Ver.0
    # path = Path
    # for dir_names, dirs, files in os.walk(path, topdown=True):
    for dir_names, dirs, files in os.walk(_path, topdown=True):
        for file in files:
            if file.endswith('.py'):
                files_names.append(os.path.join(dir_names, file))
                # Могу 100 вынести в kwargs
                if len(files_names) == 100:
                    break
    print('total %s files' % len(files_names))
    for file_name in files_names:
        with open(file_name, 'r', encoding='utf-8') as attempt_handler:
            main_file_content = attempt_handler.read()

        # Ver.0
        # try:
        #     tree = ast.parse(main_file_content)
        # except SyntaxError as e:
        #     print(e)
        #     tree = None
        # Ver.1
        tree = get_tree_of_file_content(main_file_content)

        # Можно снизить вложенность последующего, просто вынеся в функцию
        # не будет if if else else тут, а только вызов функции
        # Ver.0
        if with_file_names:
            if with_file_content:
                trees.append((file_name, main_file_content, tree))
            else:
                trees.append((file_name, tree))
        else:
            trees.append(tree)
        # Ver.1
        # Больше фича, нежели необходимость
        # complex_append_to_list(
        #     trees,
        #     tree,
        #     first_element=file_name if with_file_names else False,
        #     second_element=main_file_content if with_file_content else False,
        # )

    print('trees generated')
    return trees


# node_attribute_function в get_list_of_nodes_attribute для get_all_names
def get_node_id(node):
    return node.id


# node_attribute_function в get_list_of_nodes_attribute для get_nodes_names_at_lowercase
def get_node_lowercase_name(node):
    return node.name.lower()


# node_filter_function
def is_ast_name(node):
    return isinstance(node, ast.Name)


# node_filter_function
def is_ast_function_def(node):
    return isinstance(node, ast.FunctionDef)


def get_list_of_nodes_attribute(tree, node_attribute_function, node_filter_function):
    return [node_attribute_function(node) for node in ast.walk(tree) if node_filter_function(node)]


def get_nodes_names_at_lowercase(tree):
    return get_list_of_nodes_attribute(
        tree, 
        node_attribute_function=get_node_lowercase_name, 
        node_filter_function=is_ast_function_def
    )


def get_all_names(tree):
    # Ver.0
    # return [node.id for node in ast.walk(tree) if isinstance(node, ast.Name)]
    return get_list_of_nodes_attribute(
        tree, 
        node_attribute_function=get_node_id, 
        node_filter_function=is_ast_name
    )


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
        f for f in convert_to_flat(
            [
                powered_function(t) for t in trees
            ]
        ) if not (f.startswith('__') and f.endswith('__'))
    ]
    return function_names


def get_all_words_in_path(path):
    trees = [t for t in get_trees(path) if t]
    # Ver.0
    # function_names = [f for f in convert_to_flat([get_all_names(t) for t in trees]) if
    #                   not (f.startswith('__') and f.endswith('__'))]
    function_names = get_trees_nodes_with_powered_function_apply(trees, get_all_names)
    return convert_to_flat([split_snake_case_name_to_words(function_name) for function_name in function_names])


def get_functions_names_at_lowercase_in_trees(trees):
    # Ver.0
    # function_names = [
    #     f for f in convert_to_flat(
    #         [
    #             [
    #                 node.name.lower() for node in ast.walk(t) if isinstance(node, ast.FunctionDef)
    #             ] for t in trees
    #         ]
    #     ) if not (f.startswith('__') and f.endswith('__'))
    # ]
    # Ver.1
    # function_names = [
    #     f for f in convert_to_flat(
    #         [
    #             get_list_of_nodes_attribute(t, node_function=get_node_lowercase_name, node_filter_function=is_ast_function_def)
    #             for t in trees
    #         ]
    #     ) if not (f.startswith('__') and f.endswith('__'))
    # ]
    # Ver.2
    # function_names = [
    #     f for f in convert_to_flat(
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
    #         convert_to_flat([[node.name.lower() for node in ast.walk(t) if isinstance(node, ast.FunctionDef)] for t in trees]) if
    #         not (f.startswith('__') and f.endswith('__'))]
    # Ver.1
    fncs = get_functions_names_at_lowercase_in_trees(trees)
    print('functions extracted')
    verbs = convert_to_flat([get_verbs_from_function_name(function_name) for function_name in fncs])
    return collections.Counter(verbs).most_common(top_size)


def get_top_functions_names_in_path(path, top_size=None):
    # Я обычно так инициализирую значения по умолчанию
    if top_size is None:
        top_size = 10
    t = get_trees(path)
    # Ver.0
    # nms = [f for f in
    #        convert_to_flat([[node.name.lower() for node in ast.walk(t) if isinstance(node, ast.FunctionDef)] for t in t]) if
    #        not (f.startswith('__') and f.endswith('__'))]
    # return collections.Counter(nms).most_common(top_size)
    nms = get_functions_names_at_lowercase_in_trees(t)
    return collections.Counter(nms).most_common(top_size)


# Можно передавать директорию в качетве sys.args[0]
# c if __name__ == '__main__':
if __name__ == '__main__':

    base_path = sys.argv[1] if len(sys.argv) >= 2 else '.'

    verbs = []
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
        path_to_analyze = os.path.join(base_path, project)
        verbs += get_top_verbs_in_path(path_to_analyze)

    # Ver.0
    # top_size = 200
    # Ver.1
    top_size = sys.argv[2] if len(sys.argv) >= 3 else 200
    print('total %s words, %s unique' % (len(verbs), len(set(verbs))))
    for word, occurence in collections.Counter(verbs).most_common(top_size):
        print(word, occurence)
