class vec2:
    pass

class vec3:
    pass

class vec4:
    pass

def type2str(cls):
    if cls is bool:
        return 'bool'
    elif cls is int:
        return 'int'
    elif cls is float:
        return 'float'
    elif cls is vec2:
        return 'vec2'
    elif cls is vec3:
        return 'vec3'
    elif cls is vec4:
        return 'vec4'
    else:
        raise ValueError('Invalid GLSL type.')

class Function:
    def __init__(self, name, in_vars, out_type, code=None, uniforms=None):
        # save settings
        self.name = name
        self.in_vars = in_vars
        self.out_type = out_type

        # set code
        if code is None:
            code = ''
        self.code = code

        # set uniforms
        if uniforms is None:
            uniforms = []
        self.uniforms = uniforms

    def __str__(self):
        retval = ''

        # uniform declarations
        retval += ''.join(str(uniform)+';\n' for uniform in self.uniforms)

        # add function declaration
        retval += type2str(self.out_type) + ' '
        retval += self.name + '('
        retval += ', '.join(str(in_var) for in_var in self.in_vars)
        retval += '){\n'

        # add function body
        retval += self.code + '\n'

        # add closing brace
        retval += '}\n'

        return retval

class Variable:
    def __init__(self, name, type, size=1, is_array=None):
        """
        :param name: Name of the variable.
        :param type: Type of the variable (not a string).  int, bool, float, and vec2/3/4 are currently supported.
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
        # variable declaration
        retval = '{} {}'.format(type2str(self.type), self.name)

        # add array bounds if needed
        if self.is_array:
            retval += '['+str(self.size)+']'

        return retval

class Uniform(Variable):
    def __str__(self):
        return 'uniform ' + super().__str__()