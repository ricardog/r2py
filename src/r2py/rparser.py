from pyparsing import (
    alphanums,
    alphas,
    dblQuotedString,
    delimitedList,
    Forward,
    Group,
    infixNotation,
    Literal,
    oneOf,
    opAssoc,
    Optional,
    ParserElement,
    ParseResults,
    pyparsing_common,
    Word,
)
import re

from .tree import Node, Operator

ParserElement.enablePackrat()


def rparser():
    expr = Forward()

    lparen = Literal("(").suppress()
    rparen = Literal(")").suppress()
    # double = Word(nums + ".").setParseAction(lambda t: float(t[0]))
    integer = pyparsing_common.signed_integer
    number = pyparsing_common.number
    ident = Word(
        initChars=alphas + "_", bodyChars=alphanums + "_" + "."
    )
    string = dblQuotedString
    funccall = Group(
        ident
        + lparen
        + Group(Optional(delimitedList(expr)))
        + rparen
        + Optional(integer)
    ).setResultsName("funccall")

    operand = number | string | funccall | ident

    expop = Literal("^")
    multop = oneOf("* /")
    plusop = oneOf("+ -")
    introp = oneOf("| :")

    (
        expr
        << infixNotation(
            operand,
            [
                (expop, 2, opAssoc.RIGHT),
                (introp, 2, opAssoc.LEFT),
                (multop, 2, opAssoc.LEFT),
                (plusop, 2, opAssoc.LEFT),
            ],
        ).setResultsName("expr")
    )
    return expr


PARSER = rparser()


def parse(text):                # noqa C901
    def walk(node):
        # ['log', [['cropland', '+', 1]]]
        # ['poly', [['log', [['cropland', '+', 1]]], 3], 3]
        # [[['factor', ['unSub'], 21], ':', ['poly', [['log', [['cropland', '+', 1]]], 3], 3], ':', ['poly', [['log', [['hpd', '+', 1]]], 3], 2]]] # noqa E501
        if type(node) in (int, float):
            return node
        if isinstance(node, str):
            if node == "Intercept" or node == '"Intercept"':
                return 1
            elif node[0] == '"' and node[-1] == '"':
                return node[1:-1]
            else:
                return node
        if len(node) == 1 and type(node[0]) in (int, str, float, ParseResults):
            return walk(node[0])
        if node[0] == "factor":
            assert (
                len(node) == 3
            ), "unexpected number of arguments to factor"
            assert len(node[1]) == 1, "argument to factor is an expression"
            assert (
                type(node[2]) == int
            ), "second argument to factor is not an int"
            return Node(
                Operator("=="),
                (Node(Operator("in"), (node[1][0], "float32[:]")), node[2]),
            )
        if node[0] == "poly":
            assert len(node) in (
                2,
                3,
            ), "unexpected number of arguments to poly"
            assert isinstance(
                node[1][1], int
            ), "degree argument to poly is not an int"
            inner = walk(node[1][0])
            degree = node[1][1]
            if len(node) == 2:
                pwr = 1
            else:
                assert (
                    type(node[2]) == int
                ), "power argument to poly is not an int"
                pwr = node[2]
            return Node(
                Operator("sel"),
                (Node(Operator("poly"), (inner, degree)), pwr),
            )
        if node[0] == "log":
            assert len(node) == 2, "unexpected number of arguments to log"
            args = walk(node[1])
            return Node(Operator("log"), [args])
        if node[0] == "log1p":
            assert len(node) == 2, "unexpected number of arguments to log"
            args = walk(node[1])
            return Node(Operator("log1p"), [args])
        if node[0] == "scale":
            assert len(node[1]) in (
                3,
                5,
            ), "unexpected number of arguments to scale"
            args = walk(node[1][0])
            return Node(Operator("scale"), [args] + node[1][1:])
        if node[0] == "I":
            assert len(node) == 2, "unexpected number of arguments to I"
            args = walk(node[1])
            return Node(Operator("I"), [args])
        # Only used for testing
        if node[0] in ("sin", "cos", "tan"):
            assert len(node) == 2, (
                "unexpected number of arguments to %s" % node[0]
            )
            args = walk(node[1])
            return Node(Operator(node[0]), [args])
        if node[0] in ("max", "min", "pow"):
            assert len(node) == 2, (
                "unexpected number of arguments to %s" % node[0]
            )
            assert len(node[1]) == 2, (
                "unexpected number of arguments to %s" % node[0]
            )
            left = walk(node[1][0])
            right = walk(node[1][1])
            return Node(Operator(node[0]), (left, right))
        if node[0] == "exp":
            assert len(node) == 2, "unexpected number of arguments to exp"
            args = walk(node[1])
            return Node(Operator("exp"), [args])
        if node[0] == "expm1":
            assert len(node) == 2, "unexpected number of arguments to exp"
            args = walk(node[1])
            return Node(Operator("expm1"), [args])
        if node[0] == "sqrt":
            assert len(node) == 2, "unexpected number of arguments to sqrt"
            args = walk(node[1])
            return Node(Operator("sqrt"), [args])
        if node[0] == "clip":
            assert len(node) == 2, (
                "unexpected number of arguments to %s" % node[0]
            )
            assert len(node[1]) == 3, (
                "unexpected number of arguments to %s" % node[0]
            )
            left = walk(node[1][0])
            low = walk(node[1][1])
            high = walk(node[1][2])
            return Node(Operator(node[0]), (left, low, high))
        if node[0] == "inv_logit":
            assert (
                len(node) == 2
            ), "unexpected number of arguments to inv_logit"
            args = walk(node[1])
            return Node(Operator("inv_logit"), [args])

        # Only binary operators left
        if len(node) == 1:
            import pdb
            pdb.set_trace()
            pass
        assert (
            len(node) % 2 == 1
        ), "unexpected number of arguments for binary operator"
        assert (
            len(node) != 1
        ), "unexpected number of arguments for binary operator"
        # FIXME: this only works for associative operators.  Need to either
        # special-case division or include an attribute that specifies
        # whether the op is associative.
        left = walk(node.pop(0))
        op = node.pop(0)
        right = walk(node)
        if type(right) != Node:
            return Node(Operator(op), (left, right))
        elif right.type.type == op:
            return Node(Operator(op), (left,) + right.args)
        return Node(Operator(op), (left, right))

    # FIXME: hack
    if not isinstance(text, str):
        text = str(text)
    new_text = re.sub(r"newrange = c\((\d), (\d+)\)", "\\1, \\2", text)
    new_text = new_text.replace("rescale(", "scale(")
    nodes = PARSER.parseString(new_text, parseAll=True)
    tree = walk(nodes)
    if isinstance(tree, (str, int, float)):
        tree = Node(Operator("I"), [tree])
    return tree
