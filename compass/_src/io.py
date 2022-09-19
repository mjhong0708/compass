import json
import pickle


def save_pickle(obj, filename):
    with open(filename, "wb") as f:
        pickle.dump(obj, f)


def load_pickle(filename):
    with open(filename, "rb") as f:
        return pickle.load(f)


# TODO (mjhong): Support arbitrary object which as to_json() and from_json() method
#                Using mixin class 'JsonSerializable' might be a good idea.
def save_json(obj, filename):
    with open(filename, "w") as f:
        json.dump(obj, f)


def load_json(filename):
    with open(filename, "r") as f:
        return json.load(f)
