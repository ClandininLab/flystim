from math import pi

# modular interval arithmetic
# ref: https://fgiesen.wordpress.com/2015/09/24/intervals-in-modular-arithmetic/

class ModuloInterval:
    def __init__(self, start, end, modulus):
        self.start   = start
        self.end     = end
        self.modulus = modulus

    def size(self):
        return (self.end - self.start) % self.modulus

    def swap(self):
        self.start, self.end = self.end, self.start

    def normalize(self):
        # compute new start and end
        start = self.start % self.modulus
        end   = start + self.size()

        # assign start and end
        self.start, self.end = start, end

    def __contains__(self, item):
        return (item - self.start) % self.modulus <= (self.end - self.start) % self.modulus

    def intersect(self, other_start, other_end):
        # construct interval object for other
        other = ModuloInterval(start=other_start, end=other_end, modulus=self.modulus)

        # set the start of the new interval
        if other.start in self:
            new_start = other.start
        elif self.start in other:
            new_start = self.start
        else:
            return None

        # set the end of the new interval
        if other.end in self:
            new_end = other.end
        elif self.end in other:
            new_end = self.end
        else:
            return None

        # return the new interval
        return ModuloInterval(start=new_start, end=new_end, modulus=self.modulus)

class AngleInterval(ModuloInterval):
    def __init__(self, start, end):
        super().__init__(start=start, end=end, modulus=2*pi)