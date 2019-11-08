from scipy.interpolate import interp1d


class Trajectory:
    def __init__(self, tv_pairs, kind='linear'):
        self.tv_pairs = tv_pairs
        self.kind = kind

        # define interpolation function
        # ref: https://stackoverflow.com/questions/2184955/test-if-a-variable-is-a-list-or-tuple
        if hasattr(tv_pairs, '__iter__'):
            times, values = zip(*tv_pairs)
            self.eval_at = interp1d(times, values, kind=self.kind, fill_value='extrapolate')
        else:
            self.eval_at = lambda t: self.tv_pairs

    def to_dict(self):
        return {'tv_pairs': self.tv_pairs, 'kind': self.kind}

    @staticmethod
    def from_dict(d):
        return Trajectory(tv_pairs=d['tv_pairs'], kind=d['kind'])
