"""
Core weaving functionality.
@author twsswt
"""
import inspect


_reference_get_attributes = dict()


class IdentityAspect(object):

    def prelude(self, attribute, context, *args, **kwargs):
        pass

    def encore(self, attribute, context, result):
        pass

    def error_handling(self, attribute, context, exception):
        '''
        Takes in an exception and handles it.
        The identity is to raise the exception anyway (as if the handler was never there)
        :param attribute: The attribute which raised the excdption
        :param context: The context of the attribute (generally, the object of a method)
        :param exception: the exception raised
        :return: pass
        '''
        raise exception


def prelude(func):
    '''
    A decorator which turns the target function into advice to run it as a prelude to something else.
    '''
    class AutoGeneratedAdvice(IdentityAspect):
        def prelude(self, attribute, context, *args, **kwargs):
            return func(attribute, context, *args, **kwargs)

    return AutoGeneratedAdvice()


def encore(func):
    '''
    A decorator which turns the target function into advice to run it as an encore to something else.
    '''
    class AutoGeneratedAdvice(IdentityAspect):
        def encore(self, attribute, context, result):
            return func(attribute, context, result)

    return AutoGeneratedAdvice()


def error_handler(func):
    '''
    A decorator which turns the target function into advice to run it as an error handler for something else.
    '''
    class AutoGeneratedAdvice(IdentityAspect):
        def error_handling(self, attribute, context, exception):
            func(attribute, context, exception)

    return AutoGeneratedAdvice()


def generate_around_advice(prelude, encore):

    class AutoGeneratedAdvice(IdentityAspect):

        def around(self, attribute, context, *args, **kwargs):
            prelude(attribute, context, *args, **kwargs)

            # Check whether we need to supply `self`, which for an unbound method would be what we've got as `context`.
            if not (hasattr(attribute, '__self__') or inspect.isfunction(attribute)):
                args = (context,) + args

            result = attribute(*args, **kwargs)

            encore(attribute, context, result)

            return result

    return AutoGeneratedAdvice()


identity = IdentityAspect()


def weave_clazz(clazz, advice):
    """
    Applies aspects specified in the supplied advice dictionary to methods in the supplied class.

    Weaving is applied dynamically at runtime by intercepting invocations of __getattribute__ on target objects.
    The method requested by the __getattribute__ call is weaved using the aspect specified in the supplied advice
    dictionary (which maps method references to aspects) before returning it to the requester.

    An aspect value may itself be a dictionary of object filter->aspect mappings.  In this case, the dictionary is
    searched for a filter that matches the target (self) object specified in the __getattribute__ call.

    :param clazz : the class to weave.
    :param advice : the dictionary of method reference->aspect mappings to apply for the class.
    """

    if clazz not in _reference_get_attributes:
        _reference_get_attributes[clazz] = clazz.__getattribute__

    def __weaved_getattribute__(self, item):
        attribute = object.__getattribute__(self, item)

        if item[0:2] == '__':
            return attribute

        elif inspect.isfunction(attribute) or inspect.ismethod(attribute):

            def wrap(*args, **kwargs):

                # Sensible defaults for a function.
                reference_function = attribute
                advice_key = reference_function

                # If we're working with a method, we need to be clever about these values.
                if inspect.ismethod(attribute):
                    reference_function = attribute.im_func

                    # Ensure that advice key is unbound method for instance methods.
                    advice_key = getattr(attribute.im_class, attribute.func_name)

                # Retrieve our aspect
                aspect = advice.get(advice_key, identity)

                # Run our function
                try:
                    if hasattr(aspect, 'prelude'):
                        aspect.prelude(attribute, self, *args, **kwargs)

                    if hasattr(aspect, 'around'):
                        result = aspect.around(attribute, self, *args, **kwargs)
                    else:

                        # If we're on an unbound method, supply `self` as the first parameter.
                        func_args = args
                        if inspect.ismethod(attribute):
                            func_args = (self,) + args

                        result = reference_function(*func_args, **kwargs)

                    if hasattr(aspect, 'encore'):
                        aspect.encore(attribute, self, result)

                    return result

                # If exceptions are raised, handle with the error handler.
                except Exception as exception:
                    if hasattr(aspect, 'error_handling'):
                        return aspect.error_handling(attribute, self, exception)
                    else:
                        raise exception

            wrap.func_name = attribute.func_name

            return wrap

        else:
            return attribute

    clazz.__getattribute__ = __weaved_getattribute__


def weave_module(mod, advice):
    """
    Weaves specified advice in the supplied dictionary to methods in the supplied module.  All member classes and
    functions are inspected in turn, with the specified advice being applied to each.
    :param mod : the module to weave.
    :param advice : the dictionary of method->aspect mappings to apply.
    """
    for _, member in inspect.getmembers(mod):
        if inspect.isclass(member):
            weave_clazz(member, advice)


def unweave_class(clazz):
    if clazz in _reference_get_attributes:
        clazz.__getattribute__ = _reference_get_attributes[clazz]


def unweave_all_classes():
    for clazz in _reference_get_attributes.keys():
        unweave_class(clazz)
