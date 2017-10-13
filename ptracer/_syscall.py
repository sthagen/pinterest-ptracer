import functools
import operator


class SysCallPattern(object):
    def __init__(self, name, args=None, result=None):
        self.name = name
        self.args = args
        self.result = result

        self.matcher = []

        self.matcher.append(self._get_comparator(
            operator.attrgetter('_name'), name))

        if result is not None:
            self.matcher.append(self._get_comparator(
                operator.attrgetter('result'), result))

        if args:
            def arg_getter(call, argno):
                return call.args[argno]

            for i, arg in enumerate(args):
                if arg is None:
                    continue

                indirection = functools.partial(arg_getter, argno=i)
                self.matcher.append(self._get_comparator(indirection, arg))

    def _get_comparator(self, indirection, value):
        if callable(value):
            checker = value
            getter = indirection
        elif hasattr(value, 'match'):
            checker = value.match
            getter = lambda sc: '{}'.format(indirection(sc).value)
        else:
            checker = lambda v: v == value
            getter = lambda sc: indirection(sc).value

        return getter, checker

    def match(self, syscall):
        return all(m[1](m[0](syscall)) for m in self.matcher)
