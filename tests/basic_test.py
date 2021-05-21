from pathlib import Path
from r2py import modelr

dir_path = Path(__file__).parent


def test_model1():
    mod = modelr.load(Path(dir_path, 'test1.rds'))
    print(mod)
    return


def test_model2():
    mod = modelr.load(Path(dir_path, 'test2.rds'))
    print(mod)
    return
