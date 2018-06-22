class Uniform:
    def __init__(self, name, type, size=1, is_array=None):
        """

        :param name: Name of the uniform variable.
        :param type: Type of the uniform variable (not a string).  int, bool, and float are currently supported.
        :param size: Array length.  Ignored if is_array is False
        :param is_array: Boolean.  If None, automatically determine whether the variable is an array based on the size.
        Otherwise, True means array and False means scalar.  In the scalar case, size must be 1.
        """

        # save name, type, and size
        self.name = name
        self.type = type
        self.size = size

        # determine if this is an array, if necessary
        if is_array is None:
            is_array = size > 1
        elif not is_array:
            assert size == 1

        # save the is_array setting
        self.is_array = is_array

    def __str__(self):
        retval = ''
        retval += 'uniform'
        retval += ' '

        # handle uniform type
        if self.type is bool:
            retval += 'bool'
        elif self.type is int:
            retval += 'int'
        elif self.type is float:
            retval += 'float'
        else:
            raise ValueError('Invalid GLSL type.')

        retval += ' '

        # handle uniform name
        retval += self.name

        # handle array
        if self.is_array:
            retval += '['+str(self.size)+']'

        return retval