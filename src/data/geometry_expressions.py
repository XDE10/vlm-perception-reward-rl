"""Canonical relation order and bounded symbolic expressions for perception rewards."""

import ast
import re

import sympy as sp


ORDER = ['Angle','ArcMeasure','ArcLength','Area','CongruentAngle','CongruentLength',
         'Length','Parallel','Perpendicular','PointLiesOnCircle','PointLiesOnLine','Tangent']


def expression(raw):
    if not isinstance(raw,str) or len(raw)>160: raise ValueError('expression_length')
    s=raw.strip().replace('^','**').replace(r'\pi','pi')
    for _ in range(4):
        s=re.sub(r'\\frac\{([^{}]+)\}\{([^{}]+)\}',r'((\1)/(\2))',s)
        s=re.sub(r'\\sqrt\{([^{}]+)\}',r'sqrt(\1)',s)
    s=re.sub(r'(?<=\d)(?=[A-Za-z(])|(?<=\))(?=[A-Za-z(])','*',s)
    if not re.fullmatch(r'[A-Za-z0-9_+*/(). \-]+',s):raise ValueError('expression_outside_whitelist')
    tree=ast.parse(s,mode='eval')
    if len(list(ast.walk(tree)))>70:raise ValueError('expression_complexity')
    def build(n):
        if isinstance(n,ast.Constant) and type(n.value) in (int,float):
            if abs(n.value)>10**12:raise ValueError('constant_bound')
            return sp.Rational(str(n.value))
        if isinstance(n,ast.Name) and re.fullmatch('[a-z][a-z0-9_]{0,15}',n.id):
            if n.id in {'nan','inf','infinity','oo','zoo'}:raise ValueError('reserved_nonfinite_name')
            return sp.pi if n.id=='pi' else sp.Symbol(n.id,real=True)
        if isinstance(n,ast.UnaryOp) and isinstance(n.op,(ast.UAdd,ast.USub)):
            v=build(n.operand);return -v if isinstance(n.op,ast.USub) else v
        if isinstance(n,ast.Call) and isinstance(n.func,ast.Name) and n.func.id=='sqrt' and len(n.args)==1 and not n.keywords:
            return sp.sqrt(build(n.args[0]))
        if isinstance(n,ast.BinOp):
            a,b=build(n.left),build(n.right)
            if isinstance(n.op,ast.Add):return a+b
            if isinstance(n.op,ast.Sub):return a-b
            if isinstance(n.op,ast.Mult):return a*b
            if isinstance(n.op,ast.Div) and b!=0:return a/b
            if isinstance(n.op,ast.Pow) and b.is_Integer and abs(b)<=8:return a**b
        raise ValueError('expression_ast_rejected')
    v=build(tree.body)
    if v.has(sp.zoo,sp.oo,-sp.oo,sp.nan) or v.is_real is False:raise ValueError('nonfinite_or_nonreal')
    return sp.sstr(v),not bool(v.free_symbols),v
