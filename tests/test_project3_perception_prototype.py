from src.data.project3_perception_prototype import parse_ast,parse_record,classify,key

def parsed(raw):return parse_record(raw)

def test_nested_ast_and_angle_vertex_are_preserved():
    ast=parse_ast('Equals(MeasureOf(Angle(C, B, A)), 90)')
    assert ast['args'][0]['args'][0]['op']=='Angle'
    result=parsed('Equals(MeasureOf(Angle(C, B, A)), 90)')['fact']
    assert result['entities']==['A','B','C']
    assert key(result)!=key(parsed('Equals(MeasureOf(Angle(A, C, B)),90)')['fact'])

def test_tangent_roles_survive_argument_swap():
    a=parsed('Tangent(Circle(O),Line(B,A))')['fact']
    b=parsed('Tangent(Line(A,B),Circle(O))')['fact']
    assert a==b
    assert a['entities']==[['A','B'],'O']

def test_only_explicit_shared_vertex_perpendicular_can_entail_angle():
    diagram=[parsed('Equals(MeasureOf(Angle(A,B,C)),90)')]
    text=[parsed('Perpendicular(Line(A,B),Line(B,C))')]
    assert classify(diagram,text)[0]['category']=='text_entailed'
    unrelated=[parsed('Perpendicular(Line(A,D),Line(C,E))')]
    result=classify(diagram,unrelated)[0]
    assert result['category']=='visual_candidate'
    assert not result['training_approved']

def test_symbolic_numeric_and_outside_schema_stay_uncertain():
    for raw in ['Equals(LengthOf(Line(A,B)),x+21)','Congruent(Triangle(A,B,C),Triangle(D,E,F))']:
        result=classify([parsed(raw)],[])[0]
        assert result['category']=='uncertain'
        assert result['ast'] is not None

def test_conflicting_diagram_and_text_are_not_visual_gold():
    diagram=[parsed('Equals(LengthOf(Line(A,B)),5)')]
    text=[parsed('Equals(LengthOf(Line(B,A)),6)')]
    result=classify(diagram,text)[0]
    assert result['category']=='uncertain'
    assert result['classification_reason'].startswith('conflicting')
    assert result['human_review']=='pending'

def test_inferred_conflict_is_uncertain_and_raw_evidence_retained():
    diagram=[parsed('Equals(MeasureOf(Angle(A,B,C)),60)')]
    text=[parsed('Perpendicular(Line(A,B),Line(B,C))')]
    assert classify(diagram,text)[0]['category']=='uncertain'
    raw='Equals(LengthOf(Line(A,B)), 5)'
    explicit=classify([parsed(raw)],[parsed('Equals(5,LengthOf(Line(B,A)))')])[0]
    assert explicit['category']=='text_explicit'
    assert explicit['raw']==raw
