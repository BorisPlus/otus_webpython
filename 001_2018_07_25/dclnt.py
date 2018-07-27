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


def filtered_split(statement, sep=None, filter_function=None):
    if sep is None:
        sep = '_'
    if filter_function is None:
        filter_function = get_raw
    return [_part for _part in statement.split(sep) if filter_function(_part)]


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
    if with_file_names is None:
        with_file_names = False
    if with_file_content is None:
        with_file_content = False
    files_names = []
    trees = []
    for dir_names, dirs, files in os.walk(_path, topdown=True):
        for file in files:
            if file.endswith('.py'):
                files_names.append(os.path.join(dir_names, file))
                if len(files_names) == 100:
                    break
    print('total %s files' % len(files_names))
    for file_name in files_names:
        with open(file_name, 'r', encoding='utf-8') as attempt_handler:
            main_file_content = attempt_handler.read()
        tree = get_tree_of_file_content(main_file_content)
        if with_file_names:
            if with_file_content:
                trees.append((file_name, main_file_content, tree))
            else:
                trees.append((file_name, tree))
        else:
            trees.append(tree)
    print('trees generated')
    return trees


def get_node_id(node):
    return node.id


def get_node_name_at_lowercase(node):
    return node.name.lower()


def is_ast_name(node):
    return isinstance(node, ast.Name)


def is_ast_function_def(node):
    return isinstance(node, ast.FunctionDef)


def get_list_of_nodes_attribute(tree, node_attribute_function, node_filter_function):
    return [node_attribute_function(node) for node in ast.walk(tree) if node_filter_function(node)]


def get_nodes_names_at_lowercase(tree):
    return get_list_of_nodes_attribute(
        tree,
        node_attribute_function=get_node_name_at_lowercase,
        node_filter_function=is_ast_function_def
    )


def get_all_names(tree):
    return get_list_of_nodes_attribute(
        tree,
        node_attribute_function=get_node_id,
        node_filter_function=is_ast_name
    )


def get_verbs_from_function_name(function_name):
    return filtered_split(function_name, is_verb)


def split_snake_case_name_to_words(name):
    return filtered_split(name)


def get_trees_nodes_with_powered_function_apply(trees, powered_function):
    function_names = [
        element for element in convert_to_flat(
            [
                powered_function(tree) for tree in trees
            ]
        ) if not (element.startswith('__') and element.endswith('__'))
    ]
    return function_names


def get_real_trees(path):
    return [tree for tree in get_trees(path) if tree]


def get_all_words_in_path(path):
    trees = get_real_trees(path)
    function_names = get_trees_nodes_with_powered_function_apply(trees, get_all_names)
    return convert_to_flat([split_snake_case_name_to_words(function_name) for function_name in function_names])


def get_functions_names_at_lowercase_in_trees(trees):
    function_names = get_trees_nodes_with_powered_function_apply(trees, get_nodes_names_at_lowercase)
    return function_names


def get_top_verbs_in_path(path, top_size=None):
    if top_size is None:
        top_size = 10
    trees = get_real_trees(path)
    functions_names = get_functions_names_at_lowercase_in_trees(trees)
    print('functions extracted')
    verbs = convert_to_flat([get_verbs_from_function_name(function_name) for function_name in functions_names])
    return collections.Counter(verbs).most_common(top_size)


def get_top_functions_names_in_path(path, top_size=None):
    if top_size is None:
        top_size = 10
    trees = get_trees(path)
    functions_names = get_functions_names_at_lowercase_in_trees(trees)
    return collections.Counter(functions_names).most_common(top_size)


# Можно передавать директорию в качетве sys.args[0]
# c if __name__ == '__main__':
if __name__ == '__main__':

    base_path = sys.argv[1] if len(sys.argv) >= 2 else '.'

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

    limit_top_size = sys.argv[2] if len(sys.argv) >= 3 else 200
    print('total %s words, %s unique' % (
        len(limit_top_size_partitions_of_verbs),
        len(set(limit_top_size_partitions_of_verbs)))
          )
    for word_item, occurence in collections.Counter(limit_top_size_partitions_of_verbs).most_common(limit_top_size):
        print(word_item, occurence)
