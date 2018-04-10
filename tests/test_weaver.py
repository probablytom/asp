import unittest
from asp import weave_clazz, prelude, encore, error_handler, generate_around_advice


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

    def raise_exception(self):
        raise Exception()


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

    def test_error_raising(self):
        class ExceptionHandlingCounter(CountingAspect):
            def error_handling(aspect_self, attribute, context, exception):
                self.assertTrue(True)  # We handled! Pass the test!

        ehc = ExceptionHandlingCounter()
        advice = {Target.raise_exception: ehc}
        weave_clazz(Target, advice)

        target = Target()

        try:
            target.raise_exception()
        except:
            self.assertTrue(False)  # We should have caught this; fail the test.

    def test_error_handling_decorator(self):
        @error_handler
        def handle_exception(attribute, context, exception):
            self.assertTrue(True)  # We caught the exception successfully! Pass!

        advice = {Target.raise_exception: handle_exception}
        weave_clazz(Target, advice)

        target = Target()

        try:
            target.raise_exception()
        except:
            self.assertTrue(False)  # We should have caught this; fail the test.

    def test_around(self):

        class AroundTestingAspect(object):
            def around(self, attribute, context, *args, **kwargs):
                context.count = context.count ** 3
                result = attribute(*args, **kwargs)
                context.count *= 2
                return result

            def prelude(self, attribute, context, *args, **kwargs):
                context.count += 2

        test_around = AroundTestingAspect()
        advice = {Target.increment_count: test_around}
        weave_clazz(Target, advice)

        target = Target()
        target.increment_count()

        # We add two in the prelude, then ^3, then add one, then multiply by two.
        # This tests that the prelude is being executed before the around, but also that both are being executed.
        self.assertEqual(target.count, ((2**3)+1)*2)

    def test_around_decorator(self):

        def set_count_to_5_before_running(attr, context, *args, **kwargs):
            context.count = 5

        def increment_counter_after_running(attr, context, *args, **kwargs):
            context.count += 1

        around_advice = generate_around_advice(set_count_to_5_before_running, increment_counter_after_running)
        advice = {Target.increment_count: around_advice}
        weave_clazz(Target, advice)

        target = Target()
        target.increment_count()

        self.assertEqual(target.count, 5+1+1)


if __name__ == '__main__':
    unittest.main()
