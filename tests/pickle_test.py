import pickle
from r2py import reval, rparser


def test_pickle():
    tree = reval.make_inputs(rparser.parse("a + b + c"))
    pickle.loads(pickle.dumps(tree))
    assert True
