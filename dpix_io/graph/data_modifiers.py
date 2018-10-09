from statistics import mean


class BaseModifier(object):
    @staticmethod
    def modify(res, apis_count):
        pass


class SumModifier(BaseModifier):
    @staticmethod
    def modify(res, apis_count):
        res['headers'].append({'Sum': 'number'})
        for i, row in enumerate(res['data']):
            res['data'][i] += [sum(row[1:apis_count + 1])]


class AverageModifier(BaseModifier):
    @staticmethod
    def modify(res, apis_count):
        res['headers'].append({'Average': 'number'})
        for i, row in enumerate(res['data']):
            res['data'][i] += [mean(row[1:apis_count + 1])]
