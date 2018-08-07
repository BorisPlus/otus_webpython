import ast
import os
import collections

from nltk import pos_tag

from static_code_terms_analyzer.helpers.utils import (
    filtered_split,
    # convert_to_flat,
    get_filtered_applied_items,
    get_raw_value,
    get_object_attribute_with_apply_function,
    to_lowercase,
    apply_function_to_list,
    is_not_special
)

import logging

rootLogger = logging.getLogger('SCTA')
while rootLogger.handlers:
    rootLogger.handlers.pop()
rootLogger.setLevel(logging.INFO)
logFormatter = logging.Formatter("[%(asctime)s] %(filename)-15s %(levelname)-8s %(message)s")

consoleHandler = logging.StreamHandler()
consoleHandler.setFormatter(logFormatter)
consoleHandler.setLevel(logging.INFO)
rootLogger.addHandler(consoleHandler)


# БЛОК ИЗВЛЕЧЕНИЯ ЧАСТЕЙ РЕЧИ: НАЧАЛО

#


def is_term(word, term_prefixes, term_list):
    """
    Является ли слово определенной частью речи
    :param word: слово
    :param term_prefixes: префиксы ('VB',)
    :param term_list: явное перечисление ('NOUN',)
    :return:
    """
    if not word:
        return False
    try:
        pos_info = pos_tag([word])
        return pos_info[0][1].startswith(term_prefixes) or pos_info[0][1] in term_list
    except LookupError as e:
        # return False
        raise


def is_verb(word):
    """
    Является ли слово глаголом
    :param word: слово
    :return:
    """
    return is_term(word, term_prefixes=('VB',), term_list=('VERB',))


def is_noun(word):
    """
    Является ли слово существительным
    :param word: слово
    :return:
    """
    return is_term(word, term_prefixes=('NN',), term_list=('NOUN',))


#


def get_verbs_from_statement(statement):
    """
    Возвращает список используемых в выражении глаголов
    :param statement: строковое выражение
    :return: список глаголов
    """
    return filtered_split(statement, filter_function=is_verb)


def get_verbs_from_statements(statements):
    """
    Все глаголы из выражений
    :param statements: список выражений
    :return:
    """
    return apply_function_to_list(statements, apply_function=get_verbs_from_statement)


#

def get_nouns_from_statement(statement):
    """
    Возвращает список используемых в выражении существитеьлных
    :param statement: строковое выражение
    :return: список существитеьлных
    """
    return filtered_split(statement, filter_function=is_noun)


def get_nouns_from_statements(statements):
    """
    Все существитеьлные из выражений
    :param statements: список выражений
    :return:
    """
    return apply_function_to_list(statements, apply_function=get_nouns_from_statement)


#


def get_words_from_statement(statement):
    """
    Возвращает список используемых в выражении существитеьлных
    :param statement: строковое выражение
    :return: список существитеьлных
    """
    return filtered_split(statement, filter_function=is_noun)


def get_words_from_statements(statements):
    """
    Все слова из выражений
    :param statements: список выражений
    :return:
    """
    # words_list = []
    # for statement in statements:
    #     words_list.extend(get_words_from_statement(statement))
    # return words_list
    return apply_function_to_list(statements, apply_function=get_words_from_statement)


# БЛОК ИЗВЛЕЧЕНИЯ ЧАСТЕЙ РЕЧИ: КОНЕЦ


# БЛОК ВСПОМАГАТЕЛЬНЫХ ФУНКЦИЙ AST И NLTK: НАЧАЛО

#

def get_node_id(node):
    """
    Вернет имя переменной
    :param node: вершина AST-дерева
    :return:
    """
    return get_object_attribute_with_apply_function(node, 'id', apply_attribute_function=to_lowercase)


def get_function_def_node_name_at_lowercase(node):
    """
    Вернет имя функции
    :param node: вершина AST-дерева
    :return:
    """
    return get_object_attribute_with_apply_function(node, 'name', apply_attribute_function=to_lowercase)


def get_node_name_at_lowercase(node):
    """
    Вернет имя вершины
    :param node: вершина AST-дерева
    :return:
    """
    if hasattr(node, 'name'):
        return get_function_def_node_name_at_lowercase(node)
    elif hasattr(node, 'id'):
        return get_node_id(node)
    else:
        return ''

#

def is_ast_name(node):
    """
    Является ли вершина AST-дерева переменной
    :param node: вершина AST-дерева
    :return:
    """
    return isinstance(node, ast.Name)


def is_ast_function_def(node):
    """
    Является ли вершина AST-дерева функцией
    :param node: вершина AST-дерева
    :return:
    """
    return isinstance(node, ast.FunctionDef)


# БЛОК ВСПОМАГАТЕЛЬНЫХ ФУНКЦИЙ AST И NLTK: КОНЕЦ


# БЛОК ИЗВЛЕЧЕНИЯ И РАБОТЫ С AST-ДЕРЕВЬЯМИ: НАЧАЛО

#


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
                # чтобы не было лишнего вычисления len(files_paths) при top_files=-1
                if (top_files >= 0) and len(files_paths) == top_files:
                    break
        # чтобы не было лишних циклов и не было лишнего вычисления len(files_paths) при top_files=-1
        if (top_files >= 0) and len(files_paths) == top_files:
            break

    rootLogger.debug('total %s files' % len(files_paths))
    return files_paths


def get_tree_of_file_content(file_content):
    """
    Вернет AST-дерево по содержанию файла
    :param file_content: содержание файла
    :return:
    """
    try:
        return ast.parse(file_content)
    except SyntaxError as e:
        rootLogger.error(e)
        return


def get_trees_of_files_list(files_paths, with_file_names=False, with_file_content=False):
    """
    Возвращает список из кортежей AST-деревьев
    :param files_paths: список путей до файлов на обработку
    :param with_file_names: сохранять ли имя файла для AST-дерева
    :param with_file_content:  сохранять ли содержание файла для AST-дерева
    :return:
    """
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


# БЛОК ИЗВЛЕЧЕНИЯ И РАБОТЫ С AST-ДЕРЕВЬЯМИ: КОНЕЦ


# БЛОК РАБОТЫ С ВЕРШИНАМИ AST-ДЕРЕВЬЕВ: НАЧАЛО

#

# def get_name_nodes_ids(tree):
#     return get_filtered_applied_items(
#         tree,
#         input_apply_function=ast.walk,
#         item_apply_function=get_node_id,
#         filter_function=is_ast_name
#     )


def get_all_nodes_names_at_lowercase(tree):
    """
    Извлечение имен вершин AST-дерева
    :param tree: AST-дерево
    :return: список выражений
    """
    return get_filtered_applied_items(
        tree[2],
        input_apply_function=ast.walk,
        item_apply_function=get_node_name_at_lowercase
    )


def get_all_nodes_names_at_lowercase_of_trees(trees):
    """
    Извлечение имен вершин AST-деревев
    :param trees: AST-деревья
    :return: список выражений
    """
    return apply_function_to_list(trees, apply_function=get_all_nodes_names_at_lowercase)


#


def get_variable_nodes_names_at_lowercase(tree):
    """
    Извлечение имен переменных AST-дерева
    :param tree: AST-дерево
    :return: список выражений
    """
    return get_filtered_applied_items(
        tree[2],
        input_apply_function=ast.walk,
        item_apply_function=get_node_id,
        filter_function=is_ast_name
    )


def get_variable_nodes_names_at_lowercase_of_trees(trees):
    """
    Извлечение имен переменных AST-деревев
    :param trees: AST-деревья
    :return: список выражений
    """
    return apply_function_to_list(trees, apply_function=get_variable_nodes_names_at_lowercase)


#


def get_function_def_nodes_names_at_lowercase(tree):
    """
    Извлечение имен функций AST-дерева
    :param tree: AST-дерево
    :return: список выражений
    """
    return get_filtered_applied_items(
        tree[2],
        input_apply_function=ast.walk,
        item_apply_function=get_function_def_node_name_at_lowercase,
        filter_function=is_ast_function_def
    )


def get_function_def_nodes_names_at_lowercase_of_trees(trees):
    """
    Извлечение имен функций AST-деревев
    :param trees: AST-деревья
    :return: список выражений
    """
    return apply_function_to_list(trees, apply_function=get_function_def_nodes_names_at_lowercase)


#


def get_trees_of_path(path, with_file_names=False, with_file_content=False, top_files=100, files_extension='.py'):
    files_paths = get_files_of_path(path, top_files=top_files, files_extension=files_extension)
    trees = get_trees_of_files_list(files_paths, with_file_names=with_file_names, with_file_content=with_file_content)
    return trees


#


def get_not_special_statements(statements):
    """
    Отфильровывает список выражений на предмет специальный типа __<special>__
    :param statements: список выражений
    :return:
    """
    return get_filtered_applied_items(
        statements,
        input_apply_function=get_raw_value,
        item_apply_function=get_raw_value,
        filter_function=is_not_special
    )


def is_real_tree(tree):
    """
    Является ли AST-дерево реальным
    :param tree: AST-дерево
    :return:
    """
    if isinstance(tree, tuple) and len(tree) == 3 and tree[2]:
        return True
    return False


def get_real_trees_in_path(path):
    """
    Отфильровывает список AST-деревьев на предмет реальных по директории
    :param path: файловая директория
    :return:
    """
    return get_filtered_applied_items(
        path,
        input_apply_function=get_trees_of_path,
        item_apply_function=get_raw_value,
        filter_function=is_real_tree
    )


def get_real_trees(trees):
    """
    Отфильровывает список AST-деревьев на предмет реальных
    :param trees: AST-деревья
    :return:
    """
    return get_filtered_applied_items(
        trees
    )


def get_real_statements(statements):
    """
    Отфильровывает список выражений на предмет реальных
    :param statements: выражения
    :return:
    """
    return get_filtered_applied_items(
        statements
    )

#
#
# def get_all_words_in_path(path):
#     """
#     Получает список всех слов в коде файловой директории
#     :param path: файловая директория
#     :return:
#     """
#     real_trees = get_real_trees(path)
#     nodes_names_at_lowercase = get_all_nodes_names_at_lowercase_of_trees(real_trees)
#     not_special_nodes_names_at_lowercase = get_not_special_statements(nodes_names_at_lowercase)
#     return convert_to_flat([split_snake_case_name_to_words(node_name)
#                             for node_name in not_special_nodes_names_at_lowercase])
#
#
# def get_all_words_in_paths(paths):
#     return apply_function_to_list(paths, get_all_words_in_path)


#


def get_verbs_of_functions_names_in_path(path):
    """
    Получает список глаголов в коде из файловой директории
    :param path: файловая директория
    :return:
    """
    real_trees = get_real_trees_in_path(path)
    functions_names = get_function_def_nodes_names_at_lowercase_of_trees(real_trees)
    not_special_functions_names = get_not_special_statements(functions_names)
    return get_verbs_from_statements(not_special_functions_names)


def get_top_verbs_of_functions_names_in_path(path, top_limit=10):
    """
    Получает список глаголов в коде из файловой директории
    :param path: файловая директория
    :param top_limit: отбор первых по частоте
    :return:
    """
    verbs = get_verbs_of_functions_names_in_path(path)
    return collections.Counter(verbs).most_common(top_limit)


def get_nouns_of_variables_names_in_path(path):
    """
    Получает список существительных в коде из файловой директории
    :param path: файловая директория
    :return:
    """
    real_trees = get_real_trees_in_path(path)
    variables_names = get_variable_nodes_names_at_lowercase_of_trees(real_trees)
    not_special_variables_names = get_not_special_statements(variables_names)
    nouns_in_variables_names = get_nouns_from_statements(not_special_variables_names)
    return nouns_in_variables_names


def get_top_nouns_of_variables_names_in_path(path, top_limit=10):
    """
    Получает список существительных в коде из файловой директории
    :param path: файловая директория
    :param top_limit: отбор первых по частоте
    :return:
    """
    nouns = get_nouns_of_variables_names_in_path(path)
    return collections.Counter(nouns).most_common(top_limit)


def get_words_in_path(path):
    """
    Получает список слов в коде из файловой директории
    :param path: файловая директория
    :return:
    """
    real_trees = get_real_trees_in_path(path)
    statements = get_all_nodes_names_at_lowercase_of_trees(real_trees)
    real_statements = get_real_statements(statements)
    not_special_statements = get_not_special_statements(real_statements)
    words = get_words_from_statements(not_special_statements)
    return words


def get_top_words_in_path(path, top_limit=10):
    """
    Получает список слов в коде из файловой директории
    :param path: файловая директория
    :param top_limit: отбор первых по частоте
    :return:
    """
    words = get_words_in_path(path)
    return collections.Counter(words).most_common(top_limit)


# Мега обобщающий диспетчер


def get_terms_of_entities_in_path(path, term_type='all', entity_type='all'):
    entity_types_extract_functions = dict(
        variables=get_variable_nodes_names_at_lowercase_of_trees,
        functions=get_function_def_nodes_names_at_lowercase,
        all=get_all_nodes_names_at_lowercase_of_trees,
        default=get_all_nodes_names_at_lowercase_of_trees,
    )
    entity_types_extract_function = entity_types_extract_functions.get(
        entity_type,
        entity_types_extract_functions.get('default'),
    )
    term_type_extract_functions = dict(
        noun=get_nouns_from_statements,
        verb=get_verbs_from_statements,
        all=get_words_from_statements,
        default=get_words_from_statements,
    )
    term_type_extract_function = term_type_extract_functions.get(
        term_type,
        term_type_extract_functions.get('default'),
    )
    real_trees = get_real_trees_in_path(path)
    statements = entity_types_extract_function(real_trees)
    real_statements = get_real_statements(statements)
    not_special_statements = get_not_special_statements(real_statements)
    term_words = term_type_extract_function(not_special_statements)
    return term_words


def get_top_term_words(term_words, top_limit=10):
    return collections.Counter(term_words).most_common(top_limit)


def get_top_terms_of_entities_in_path(path, term_type='all', entity_type='all', top_limit=10):
    term_words = get_terms_of_entities_in_path(path, term_type=term_type, entity_type=entity_type)
    return get_top_term_words(term_words, top_limit)


if __name__ == '__main__':
    pass
