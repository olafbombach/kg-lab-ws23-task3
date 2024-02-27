from source.archive.data_search import SearchEngine
import json


class Evaluator:
    """
        This class evaluates a specified testset as a dataset.
        Format of the dataset has to be
    """

    def __init__(self, tokenized_set: str):
        self._tokenized_set = tokenized_set
        self._testdata = self._read_in_json()
        self._eval_dict = dict()
        self._recall_measure = None
        self._precision_measure = None

    def _read_in_json(self) -> list:
        json_file = open('../datasets/wikidata/'+self._tokenized_set)
        testdata = json.loads(json_file.read())
        return testdata

    def self_evaluation(self) -> None:
        se = SearchEngine('proceedings.com')

        for i in [7, 8, 11, 16, 18, 21, 29, 32, 34, 42, 43, 44, 49, 54, 58, 63, 65, 70, 71, 73, 74, 77, 83, 91, 97, 98]:
            entry = self._testdata[i]
            print(se.search_dict(entry)[["Conference Title", "score"]])
            value = input("At which position is the correct conference? (position or N)")
            self._eval_dict[i] = value

    def compute_recall(self):
        pass

    def compute_precision(self):
        pass

    def print_eval_dict(self):
        return self._eval_dict


proceedings_eval = {7: 'top', 8: 'top', 11: 'top', 16: 'top', 18: 'top', 21: 'top', 29: 'fifth', 32: 'top', 34: 'top',
                    42: 'top', 43: 'top', 44: 'third', 49: 'top', 54: 'Not unique', 58: 'top', 63: 'second', 65: 'top',
                    70: 'top', 71: 'top', 73: 'top', 74: 'top', 77: 'top', 83: 'top', 91: 'top', 97: 'third', 98: 'top'}
'''
df = pd.DataFrame(data=proceedings_eval.values(), index=proceedings_eval.keys(), columns=['position in search'])
df['position in search'] = pd.Categorical(df['position in search'], ['top', 'second', 'third', 'fifth', 'Not unique'])

ev = Evaluator("output_tokenizer.json")
ev.self_evaluation()
print(ev.print_eval_dict())

print(df)
sn.histplot(data=df, x='position in search', color='r')
plt.yticks(range(0, 25, 1))
plt.savefig('../results/testset_v1_perf.png')
plt.show()
'''
