from pathlib import Path
from r2py.rparser import parse

dir_path = Path(__file__).parent


def test_sin():
    _ = parse("sin(a)")
    return


def test_cos():
    _ = parse("cos(a)")
    return


def test_tan():
    _ = parse("tan(a)")
    return


def test_log():
    _ = parse("log(a)")
    return


def test_log1p():
    _ = parse("log1p(a)")
    return


def test_exp():
    _ = parse("log(a)")
    return


def test_expm1():
    _ = parse("expm1(a)")
    return


def test_max():
    _ = parse("max(a, b)")
    return


def test_min():
    _ = parse("min(a, b)")
    return


def test_pow():
    _ = parse("pow(a, b)")
    return


def test_clip():
    _ = parse("clip(a, 0, 1)")
    return


def test_scale():
    # Same as plotrix::rescale in R
    _ = parse("scale(a, 0, 1)")
    return


def test_inv_logit():
    _ = parse("inv_logit(a)")
    return


def test_poly():
    _ = parse("poly(a, 2, 3)")
    return
