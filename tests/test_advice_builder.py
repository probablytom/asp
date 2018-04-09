import unittest
from asp import AdviceBuilder

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
