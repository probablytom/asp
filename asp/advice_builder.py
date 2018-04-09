from .weaver import IdentityAspect, weave_clazz

class FlexibleAdvice(IdentityAspect):
    def __init__(self, target):
        super(FlexibleAdvice, self).__init__()
        self.preludes = []
        self.encores = []
        self.error_handlers = []
        self.target = target

    def prelude(self, attribute, context, *args, **kwargs):
        [prelude(attribute, context, *args, **kwargs) for prelude in self.preludes]

    def encore(self, attribute, context, result):
        [encore(attribute, context, result) for encore in self.encores]

    def error_handling(self, attribute, context, exception):

        if len(self.error_handlers) == 0:
            raise exception

        [handler(attribute, context, exception) for handler in self.error_handlers]

    def apply_advice(self):
        weave_clazz(self.target.im_class, {self.target: self})


class AdviceBuilder(object):
    def __init__(self):
        self.advice = {}

    def add_prelude(self, target, prelude):
        specific_advice = self.advice.get(target, FlexibleAdvice(target))
        specific_advice.preludes.append(prelude)
        self.advice[target] = specific_advice
        return self

    def add_encore(self, target, encore):
        specific_advice = self.advice.get(target, FlexibleAdvice(target))
        specific_advice.encores.append(encore)
        self.advice[target] = specific_advice
        return self

    def add_error_handler(self, target, err_handler):
        specific_advice = self.advice.get(target, FlexibleAdvice(target))
        specific_advice.error_handlers.append(err_handler)
        self.advice[target] = specific_advice
        return self

    def apply(self):
        [aspect.apply_advice() for aspect in self.advice.values()]
