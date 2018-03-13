import unittest
from asp import weave_clazz


class CountingAspect(object):
    def __init__(self):
        self.invocations = 0

    def prelude(self, attribute, context, *args, **kwargs):
        self.invocations += 1

    def encore(self, attribute, context, result):
        pass


class Target(object):

    def foo(self):
        return self


class WeaverTestCase(unittest.TestCase):

    def test_before_and_after(self):

        counting_aspect = CountingAspect()
        advice = {Target.foo: counting_aspect}
        weave_clazz(Target, advice)

        Target().foo().foo().foo()

        self.assertEqual(3, counting_aspect.invocations)


if __name__ == '__main__':
    unittest.main()
