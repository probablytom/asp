import unittest
from asp import weave_clazz, prelude, encore


class CountingAspect(object):
    def __init__(self):
        self.invocations = 0

    def prelude(self, attribute, context, *args, **kwargs):
        self.invocations += 1

    def encore(self, attribute, context, result):
        pass


class Target(object):

    def __init__(self):
        self.count = 0

    def foo(self):
        return self

    def increment_count(self):
        self.count += 1
        return self


class WeaverTestCase(unittest.TestCase):

    def test_before_and_after(self):

        counting_aspect = CountingAspect()
        advice = {Target.foo: counting_aspect}
        weave_clazz(Target, advice)

        Target().foo().foo().foo()

        self.assertEqual(3, counting_aspect.invocations)

    def test_prelude_decorator(self):

        @prelude
        def set_count_to_5_before_running(attr, context, *args, **kwargs):
            context.count = 5

        advice = {Target.increment_count: set_count_to_5_before_running}
        weave_clazz(Target, advice)

        target = Target()
        target.increment_count()

        self.assertEqual(target.count, 5+1)

    def test_encore_decorator(self):

        @encore
        def set_count_to_5_after_running(attr, context, *args, **kwargs):
            context.count = 5

        advice = {Target.increment_count: set_count_to_5_after_running}
        weave_clazz(Target, advice)

        target = Target()
        target.increment_count()

        self.assertEqual(target.count, 5)


if __name__ == '__main__':
    unittest.main()
