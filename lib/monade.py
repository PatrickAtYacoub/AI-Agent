import traceback
 
 
# <<monad>>
class CallResult:
    """
    Base class for all call results.
    """
 
    def then(self, func, *args, **kwargs):
        """
        Applies the given function to the result if it's valid.
        Propagates the error otherwise, capturing exceptions and stack traces.
        This method is otherwise also often called 'bind'.
        """
        if isinstance(self, ValidResult):
            try:
                return func(self.value(), *args, **kwargs)
            except Exception as e:
                return ErrorResult.from_exception(e)
        else:
            return self  # Propagate the ErrorResult
 
 
class ValidResult(CallResult):
    """
    Represents a successful result.
    """
 
    def __init__(self, value):

        if isinstance(value, ValidResult):
            self._value = value.value()
        else:
            self._value = value
 
    def value(self):
        """
        Returns the encapsulated value.
        """
        return self._value
 
    def __repr__(self):
        return f"ValidResult({self._value})"
 
 
class ErrorResult(CallResult):
    """
    Represents an error result, containing an exception and its stack trace.
    """
 
    def __init__(self, error_message, exception=None, stack_trace=None):
        self.error_message = error_message
        self.exception = exception
        self.stack_trace = stack_trace
 
    @classmethod
    def from_exception(cls, exception, custom_message=None):
        """
        Creates an ErrorResult from an exception, capturing the stack trace.
        """
        error_message = str(exception)
        if custom_message is not None:
            error_message = f"{custom_message}: {error_message}"
        stack_trace = traceback.format_exc()
        return cls(error_message, exception, stack_trace)
    
    def get_error_message(self):
        """
        Returns the error message.
        """
        return self.error_message
 
    def get_exception(self):
        """
        Returns the stored exception object.
        """
        return self.exception
 
    def get_stack_trace(self):
        """
        Returns the formatted stack trace.
        """
        return self.stack_trace
 
    def __repr__(self):
        return f"ErrorResult({self.error_message})"
 
 
class LazyCallResult(CallResult):
    """
    Represents a lazily evaluated result.
    """
 
    def __init__(self, func):
        self.func = func
        self._evaluated = False
        self._result = None
 
    def value(self):
        """
        Evaluates the function if not already evaluated and returns the value.
        Captures exceptions and stack traces if errors occur.
        """
        if not self._evaluated:
            try:
                result = self.func()
                self._result = ValidResult(result)
            except Exception as e:
                self._result = ErrorResult.from_exception(e)
            self._evaluated = True
 
        if isinstance(self._result, ValidResult):
            return self._result.value()
        else:
            raise Exception(f"Cannot retrieve value: {self._result.error_message}")
 
    def get_result(self):
        """
        Performs the calculation, but returns the monad instead of the value, so may return an
        ErrorResult too.
        """
        if not self._evaluated:
            self.value()
 
        return self._result
 
    def then(self, func):
        """
        Chains the function to the result, ensuring lazy evaluation.
        Captures exceptions and stack traces during evaluation.
        """
        def new_func():
            result = self.value()  # May raise exception if ErrorResult
            return func(result).value()
        return LazyCallResult(new_func)
 
    def __repr__(self):
        if self._evaluated:
            return repr(self._result)
        else:
            return "LazyCallResult(<unevaluated>)"
 
 
# Utility Functions
 
def try_call(func, *args, **kwargs):
    """
    Tries to call the function and returns a ValidResult or ErrorResult.
    Captures exceptions and stack traces in case of errors.
    """
    try:
        return ValidResult(func(*args, **kwargs))
    except Exception as e:
        return ErrorResult.from_exception(e)
 
 
def get_result_value(call_result, default=None):
    """
    ('unwrap')
    Returns the value if it's a ValidResult, or the default value.
    """
    if isinstance(call_result, ValidResult):
        return call_result.value()
    else:
        return default
 
 
def log_error(error_result):
    """
    Logs the error message and stack trace from an ErrorResult.
    """
    print(f"Error: {error_result.error_message}")
    print("Stack Trace:")
    print(error_result.get_stack_trace())
 
 
# Example Usage
if __name__ == "__main__":
    def main():
        # Example 1: Basic Chaining with then()
        def increment(x):
            return ValidResult(x + 1)
 
        def double(x):
            return ValidResult(x * 2)
 
        def to_string(x):
            return ValidResult(f"The result is {x}")
 
        result = ValidResult(5)
        final_result = result.then(increment).then(double).then(to_string)
 
        if isinstance(final_result, ValidResult):
            print(final_result.value())  # Output: "The result is 12"
        else:
            log_error(final_result)
 
        # Example 2: Handling Errors
        def safe_divide(x):
            if x == 0:
                return ErrorResult("Division by zero")
            else:
                return ValidResult(10 / x)
 
        def multiply_by_three(x):
            return ValidResult(x * 3)
 
        def multiply_by(n):
            def _core(x):
                return ValidResult(n * 3)
 
            return _core
 
        result = ValidResult(0)
        final_result = result.then(safe_divide).then(multiply_by_three)
 
        if isinstance(final_result, ValidResult):
            print(final_result.value())
        else:
            log_error(final_result)
 
        # Example 3: Capturing Exceptions and Stack Traces
        def faulty_function(x):
            return 10 / x  # Will raise ZeroDivisionError if x is 0
 
        result = try_call(faulty_function, 0)
 
        if isinstance(result, ValidResult):
            print(f"Success: {result.value()}")
        else:
            log_error(result)
 
        # Example 4: Lazy Evaluation with Exception Handling
        import time
 
        def compute_delayed_value():
            time.sleep(1)
            raise RuntimeError("Simulated runtime error")
 
        def process_value(x):
            return ValidResult(x * 2)
 
        lazy_result = LazyCallResult(compute_delayed_value).then(process_value)
 
        try:
            value = lazy_result.value()
            print(f"Computed Value: {value}")
        except Exception as e:
            print(f"Exception Occurred: {e}")
            if isinstance(lazy_result.get_result(), ErrorResult):
                log_error(lazy_result.get_result())
 
 
    main()