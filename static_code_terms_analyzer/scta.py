import ast
import os
import collections
import sys

from nltk import pos_tag

from static_code_terms_analyzer.helpers.utils import (
    filtered_split,
    convert_to_flat,
    split_snake_case_name_to_words,
    get_filtered_applied_items,
    get_raw_value,
    get_object_attribute_with_apply_function,
    to_lowercase
)

import logging

rootLogger = logging.getLogger('SCTA')
rootLogger.setLevel(logging.INFO)
logFormatter = logging.Formatter("[%(asctime)s] %(filename)-15s %(levelname)-8s %(message)s")

consoleHandler = logging.StreamHandler()
consoleHandler.setFormatter(logFormatter)
consoleHandler.setLevel(logging.INFO)
rootLogger.addHandler(consoleHandler)


# https://www.nltk.org/book/ch05.html
# Table 7.1:
# Some morphosyntactic distinctions in the Brown tagset
#
# Form 	Category 	Tag
# go 	base 	VB
# goes 	3rd singular present 	VBZ
# gone 	past participle 	VBN
# going gerund 	VBG
# went 	simple past 	VBD


def is_verb(word):
    """
    Является ли слово глаголом
    :param word: слова
    :return:
    """
    if not word:
        return False
    pos_info = pos_tag([word])
    # in ('VB', 'VBN', 'VBP', 'VBZ', 'VBD', 'VBG')
    return pos_info[0][1].startswith('VB')


def get_verbs_from_function_name(function_name):
    """
    Возвращает список используемых в названии функции глаголов
    :param function_name: имя функции
    :return: список используемых в названии функции глаголов
    """
    return filtered_split(function_name, is_verb)


def get_node_id(node):
    return get_object_attribute_with_apply_function(node, 'id')


def get_node_name_at_lowercase(node):
    return get_object_attribute_with_apply_function(node, 'name', apply_attribute_function=to_lowercase)


def is_ast_name(node):
    return isinstance(node, ast.Name)


def is_ast_function_def(node):
    return isinstance(node, ast.FunctionDef)


def get_tree_of_file_content(file_content):
    try:
        return ast.parse(file_content)
    except SyntaxError as e:
        rootLogger.error(e)
        return


def get_files_of_path(path, top_files=100, files_extension='.py'):
    """
    Возвращает список путей до файлов определенного расширения из корневой категории
    :param path: корневая дирктория
    :param top_files: сколько первых файлов взять (-1 = все, 0 = ничего, по у молчанию = 100)
    :param files_extension: какого расширения файлы отбирать
    :return:
    """
    files_paths = []
    for dir_name, dirs, files in os.walk(path, topdown=True):
        for file in files:
            if file.endswith(files_extension):
                files_paths.append(os.path.join(dir_name, file))
                if len(files_paths) == top_files:
                    break
        # чтобы не было лишних циклов
        if len(files_paths) == top_files:
            break

    rootLogger.debug('total %s files' % len(files_paths))
    return files_paths


def get_trees_of_files_list(files_paths, with_file_names=False, with_file_content=False):
    trees = []
    for file_path in files_paths:
        with open(file_path, 'r', encoding='utf-8') as attempt_handler:
            main_file_content = attempt_handler.read()
            stored_file_tree = get_tree_of_file_content(main_file_content)
            stored_file_path = file_path if with_file_names else None
            stored_file_content = main_file_content if with_file_names and with_file_content else None
            trees.append((stored_file_path, stored_file_content, stored_file_tree))
    rootLogger.debug('trees were generated')
    return trees


def get_trees_of_path(path, with_file_names=False, with_file_content=False, top_files=100, files_extension='.py'):
    files_paths = get_files_of_path(path, top_files=top_files, files_extension=files_extension)
    trees = get_trees_of_files_list(files_paths, with_file_names=with_file_names, with_file_content=with_file_content)
    return trees


#
# def get_list_of_nodes_attribute(tree, node_attribute_function, node_filter_function):
#     return [node_attribute_function(node) for node in ast.walk(tree) if node_filter_function(node)]


def get_function_def_nodes_names_at_lowercase(tree):
    return get_filtered_applied_items(
        tree,
        input_apply_function=ast.walk,
        item_apply_function=get_node_name_at_lowercase,
        filter_function=is_ast_function_def
    )


def get_name_nodes_ids(tree):
    return get_filtered_applied_items(
        tree,
        input_apply_function=ast.walk,
        item_apply_function=get_node_id,
        filter_function=is_ast_name
    )


def get_not_special_elements_at_flat_of_trees_apply_function(trees, apply_function):
    not_special_elements = [
        element for element in convert_to_flat(
            [
                apply_function(tree) for tree in trees
            ]
        ) if not (element.startswith('__') and element.endswith('__'))
    ]
    return not_special_elements


def get_real_trees(path):
    return get_filtered_applied_items(
        path,
        input_apply_function=get_trees_of_path,
        item_apply_function=get_raw_value,
        filter_function=get_raw_value
    )


def get_all_words_in_path(path):
    trees = get_real_trees(path)
    nodes_names = get_not_special_elements_at_flat_of_trees_apply_function(trees, get_name_nodes_ids)
    return convert_to_flat([split_snake_case_name_to_words(node_name) for node_name in nodes_names])


def get_functions_names_at_lowercase_in_trees(trees):
    function_names = get_not_special_elements_at_flat_of_trees_apply_function(
        trees,
        get_function_def_nodes_names_at_lowercase)
    return function_names


def get_top_verbs_in_path(path, top_size=10):
    trees = get_real_trees(path)
    functions_names = get_functions_names_at_lowercase_in_trees(trees)
    rootLogger.debug('functions extracted')
    verbs = convert_to_flat([get_verbs_from_function_name(function_name) for function_name in functions_names])
    return collections.Counter(verbs).most_common(top_size)


def get_top_functions_names_in_path(path, top_size=10):
    trees = get_trees_of_path(path)
    functions_names = get_functions_names_at_lowercase_in_trees(trees)
    return collections.Counter(functions_names).most_common(top_size)


if __name__ == '__main__':
    pass
