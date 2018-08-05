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
        if isinstance(item, collections.Iterable):
            result.extend(convert_to_flat(item))
        else:
            result.append(item)
    return result


def get_raw_value(x):
    return x


def filtered_split(statement, sep=None, filter_function=None):
    """
    Функция разбиения строки с применением фильтрационной функции.
    :param statement: Строковое выражение для разбиения на части
    :param sep: Разделитель, по умолчанию "-"
    :param filter_function: Фильрующая функция, оставляет только удовлетворяющие ей после разбиения части
    :return:
    """
    if sep is None:
        sep = '_'
    if filter_function is None:
        filter_function = get_raw_value
    return [part for part in statement.split(sep) if filter_function(part)]


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
    return string.lower()

if __name__ == '__main__':

    class A:
        a = 2

        def get_at_power(self):
            return self.a**2

    b = A()

    z1 = get_object_attribute_with_apply_function(
        b,
        'a'
    )
    print('b.a %s' % z1)

    z2 = get_object_attribute_with_apply_function(
        b,
        'get_at_power'
    )
    print('b.get_at_power %s' % z2)
