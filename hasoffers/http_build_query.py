from urllib.parse import quote


def http_build_query(d):

    """
    >>> d = {'data': {'name': 'John', 'email': 'john@johnmail.com', 'friends':['Paul', 'Alan']}}
    >>> http_build_query(d)
    'data[friends][]=Paul&data[friends][]=Alan&data[name]=John&data[email]=john%40johnmail.com'
    """

    def combine_qs_key_from_list(l):

        """
        Example:
            converts
                ['data', 'options', 'param']
            to
                data[options][param]
        """

        if len(l) == 0:
            return ''

        s = l[0]

        for el in l[1:]:
            s += '[%s]' % str(el)

        return s

    def deep(d, base=[]):

        KV = []

        for key, value in d.items():

            new_base = base + [key]

            if type(value) == dict:
                KV += deep(value, new_base)

            elif type(value) == list:
                for el in value:
                    KV.append('%s[]=%s' % (combine_qs_key_from_list(new_base), quote(str(el))))

            else:
                if len(base) > 0:
                    KV.append('%s[%s]=%s' % (combine_qs_key_from_list(base), str(key), quote(str(value))))
                else:
                    KV.append('%s=%s' % (str(key), quote(str(value))))

        return KV

    pairs = deep(d)

    return '&'.join(pairs)
