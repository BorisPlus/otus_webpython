import collections


def convert_to_flat(items):
    """
    Конвертирует в плоский список
    [(1,2), [3,4]] -> [1, 2, 3, 4]
    :param items: список элементов
    :return: плоский список
    """
    result = []
    for item in items:
        if isinstance(item, list) or isinstance(item, tuple) or isinstance(item, set):
            result.extend(convert_to_flat(item))
        else:
            result.append(item)
    return result


def get_raw_value(x):
    return x


def filtered_split(statement, sep='_', filter_function=get_raw_value):
    """
    Функция разбиения строки с применением фильтрационной функции.
    :param statement: Строковое выражение для разбиения на части
    :param sep: Разделитель, по умолчанию "-"
    :param filter_function: Фильрующая функция, оставляет только удовлетворяющие ей после разбиения части
    :return:
    """
    return [part for part in statement.split(sep=sep) if filter_function(part)]


def apply_function_to_list(elements, apply_function=get_raw_value, filter_function=get_raw_value):
    result_list = []
    for element in elements:
        if filter_function(element):
            result_list.extend(apply_function(element))
    return result_list


# для снижения вложенности, если было б нужно
def complex_append_to_list(list_of_elements, last_element, first_element, second_element):
    if first_element and second_element:
        list_of_elements.append((first_element, second_element, last_element))
    elif first_element and not second_element:
        list_of_elements.append((first_element, last_element))
    else:
        list_of_elements.append(last_element)


def split_snake_case_name_to_words(name):
    """
    Разбивает snake_case - нотацию на слова
    :param name: snake_case именование
    :return: список слов
    """
    return filtered_split(name)


def get_filtered_applied_items(input,
                               input_apply_function=get_raw_value,
                               item_apply_function=get_raw_value,
                               filter_function=get_raw_value):
    """
    Функция фильтрации элементов с применением функций к списку элементов и элементам списка.
    :param input: список элементов или входное значение для input_apply_function для получения списка
    :param input_apply_function: применяемая к входному значению функция
    :param item_apply_function: применяемая к элементам списка функция
    :param filter_function: Фильрующая функция, оставляет только удовлетворяющие ей элементы
    :return: списиок
    """
    return [item_apply_function(item) for item in input_apply_function(input) if filter_function(item)]


def get_object_attribute_with_apply_function(obj, field_name, apply_attribute_function=get_raw_value):
    """
    Вернет значение аттрибута объекта с применением функции к результату
    :param obj: Объект
    :param field_name: имя свойства или метода
    :param apply_attribute_function: Применяемая функция
    :return: значение аттрибута объекта с применением функции к результату
    """
    field = getattr(obj, field_name)
    return apply_attribute_function(field() if callable(field) else field)


def to_lowercase(string):
    if not string:
        return None
    return string.lower()


def is_special(statement):
    if statement.startswith('__') and statement.endswith('__'):
        return True
    return False


def is_not_special(statement):
    return not is_special(statement)


if __name__ == '__main__':
    pass