import unittest
from asp import AdviceBuilder, generate_around_advice

class Target(object):
    def __init__(self):
        self.count = 0
        self.exceptions_handled = 0

    def increment_count(self):
        self.count += 1

    def raise_exception(self):
        raise Exception


def increment_count(attribute, context, optional_result=None):
    context.count += 1


def handle_exception(attribute, context, exception):
    context.exceptions_handled += 1


class TestAdviceBuilder(unittest.TestCase):
    def test_advice_builder_prelude(self):
        builder = AdviceBuilder()
        builder.add_prelude(Target.increment_count, increment_count)
        builder.apply()

        target = Target()
        target.increment_count()
        self.assertEqual(target.count, 1+1)  # Should have incremented after being initially incremented by a prelude.

    def test_advice_builder_encore(self):
        builder = AdviceBuilder()
        builder.add_encore(Target.increment_count, increment_count)
        builder.apply()

        target = Target()
        target.increment_count()
        self.assertEqual(target.count, 1+1)  # Should have incremented after being initially incremented by an encore.

    def test_advice_builder_error_handling(self):
        builder = AdviceBuilder()
        builder.add_error_handler(Target.raise_exception, handle_exception)
        builder.apply()

        target = Target()
        target.raise_exception()
        self.assertEqual(target.exceptions_handled, 1)  # No error should be raised, we just increment when we handle.

    def test_advice_builder_multiple_error_handlers(self):
        builder = AdviceBuilder()
        builder.add_error_handler(Target.raise_exception, handle_exception)
        builder.add_error_handler(Target.raise_exception, handle_exception)
        builder.apply()

        target = Target()
        target.raise_exception()
        self.assertEqual(target.exceptions_handled, 2)  # We increment twice if we run the exception handler twice.

    def test_advice_builder_multiple_preludes(self):
        builder = AdviceBuilder()
        builder.add_prelude(Target.increment_count, increment_count)
        builder.add_prelude(Target.increment_count, increment_count)
        builder.apply()

        target = Target()
        target.increment_count()
        self.assertEqual(target.count, 1+1+1)  # Should have incremented after being incremented twice by two preludes.

    def test_advice_builder_multiple_encores(self):
        builder = AdviceBuilder()
        builder.add_encore(Target.increment_count, increment_count)
        builder.add_encore(Target.increment_count, increment_count)
        builder.apply()

        target = Target()
        target.increment_count()
        self.assertEqual(target.count, 1+1+1)  # Should have incremented, then incremented twice more by two encores.

    def test_advice_builder_around(self):
        def around_to_test(attribute, context, *args, **kwargs):
            '''
            Add three, run the original (going to add another one), then multiply by two.
            '''
            context.count += 3
            result = attribute(*args, **kwargs)
            context.count *= 2
            return result

        builder = AdviceBuilder()
        builder.add_around(Target.increment_count, around_to_test)
        builder.apply()

        target = Target()
        target.increment_count()
        self.assertEqual(target.count, (3+1) * 2)

    def test_generated_advice(self):
        def add_three(attribute, context, *args, **kwargs):
            context.count += 3

        def mult_by_2(attribute, context, result):
            context.count *= 2

        generated_around = generate_around_advice(add_three, mult_by_2)
        builder = AdviceBuilder()
        builder.add_around(Target.increment_count, generated_around)
        builder.apply()

        target = Target()
        target.increment_count()
        self.assertEqual(target.count, (3+1) * 2)

    def test_multiple_arounds(self):
        def around_to_test(attribute, context, *args, **kwargs):
            '''
            Add three, run the original (going to add another one), then multiply by two.
            '''
            context.count += 3
            result = attribute(*args, **kwargs)
            context.count *= 2
            return result

        builder = AdviceBuilder()
        builder.add_around(Target.increment_count, around_to_test)
        builder.add_around(Target.increment_count, around_to_test)
        builder.apply()

        target = Target()
        target.increment_count()
        # We want arounds to wrap around each other, so we want to add three twice, then increment, then mult by 4.
        self.assertEqual(target.count, ((3+(3+1))*2)*2)


