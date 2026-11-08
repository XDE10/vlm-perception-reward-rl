import pytest
from src.data.project3_perception_v2 import parse_record,expression,classify


def f(s):
    r=parse_record(s);assert r['parse_status']=='supported',r;return r['fact']


def test_symbolic_radical_and_reject_code():
    assert expression('2x+7')[0]=='2*x + 7'
    assert expression(r'11\sqrt{2}')[0]=='11*sqrt(2)'
    assert expression(r'\frac{1}{2}x+12')[0]=='x/2 + 12'
    for s in ["__import__('os').system('x')",'x[0]','2**10000','1/0','nan']:
        with pytest.raises((ValueError,SyntaxError)):expression(s)


def test_angles_congruence_and_polygon_preserve_roles():
    assert f('Equals(MeasureOf(Angle(C,B,A)),2x+7)')['entities']==['A','B','C']
    assert f('Equals(LengthOf(Line(R,T)),LengthOf(Line(R,S)))')['relation']=='CongruentLength'
    assert f('Equals(AreaOf(Pentagon(A,D,B,O,C)),272)')['entities']['boundary']==['A','D','B','O','C']


def test_arc_measure_length_circle_and_incidence_distinct():
    a=f('Equals(MeasureOf(Major(Arc(A,D,C))),56)')
    b=f('Equals(LengthOf(Arc(A,D,C)),56)')
    assert (a['relation'],a['unit'])==('ArcMeasure','deg')
    assert (b['relation'],b['unit'])==('ArcLength','unspecified_source_unit')
    assert a['entities']=={'points':['A','D','C'],'kind':'major'}
    assert f('PointLiesOnCircle(A,Circle(B,radius_3_0))')['entities'][1]['center']=='B'
    r=parse_record('PointLiesOnLine(A,Line(B,C))')
    assert classify([r],[r])[0]['category']=='text_explicit'
    r=parse_record('PointLiesOnLine(B,Line(B,C))')
    assert classify([r],[])[0]['category']=='text_entailed'


def test_symbolic_constraints_not_contradictions_but_constant_conflicts_are():
    rs=[parse_record('Equals(LengthOf(Line(A,B)),x)'),parse_record('Equals(LengthOf(Line(A,B)),3)')]
    assert all(r['category']=='visual_candidate' for r in classify(rs,[]))
    rs.append(parse_record('Equals(LengthOf(Line(A,B)),4)'))
    assert all(r['category']=='uncertain' for r in classify(rs,[]))
