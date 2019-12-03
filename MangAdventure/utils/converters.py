class FloatConverter:
    regex = r'\d(\.\d+)?'

    def to_python(self, value):
        return float(value)

    def to_url(self, value):
        return f'{float(value):g}'
