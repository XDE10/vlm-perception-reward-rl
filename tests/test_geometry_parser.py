import itertools
import pytest
from src.evaluation.geometry_perception_parser import canonicalize, parse_fact, parse_facts, parse_response, perception_f1, GeometryError


def test_canonical_order_permutations_roundtrip_idempotence():
    facts = ['Perpendicular(DC,BA)','Length(B,A)=5','Angle(C,B,A)=60°']
    expected = 'Angle(A,B,C)=60deg; Length(A,B)=5; Perpendicular(AB,CD)'
    for permutation in itertools.permutations(facts):
        result = canonicalize(';'.join(permutation))
        assert result==expected and canonicalize(result)==result
        assert parse_facts(result)==parse_facts(';'.join(permutation))


def test_duplicate_and_reverse_entity_attack():
    gold = 'Perpendicular(AB,CD); Length(A,B)=5'
    pred = ';'.join(['Perpendicular(DC,BA)']*100+['Length(B,A)=5']*30)
    score = perception_f1(pred,gold,{'Perpendicular','Length'})
    assert score['tp']==2 and score['f1']==1.


def test_hallucination_penalty_in_complete_categories():
    gold = 'Length(A,B)=5'
    score = perception_f1(gold+';Length(C,D)=8',gold,{'Length'})
    assert score['precision']==.5 and score['recall']==1 and score['f1']==pytest.approx(2/3)


def test_uncovered_relations_and_missing_labels_not_rewarded_as_full_score():
    score = perception_f1('Length(A,B)=5;Parallel(AB,CD)','Length(A,B)=5',{'Length'})
    assert score['f1']==1 and score['unscored_count']==1
    score = perception_f1('Length(A,B)=5','',set())
    assert not score['mask'] and score['f1']==0


@pytest.mark.parametrize('bad',[
 'Length(A,B)=5;Length(B,A)=6',
 'Angle(A,B,C)=30;Angle(C,B,A)=60',
 'Parallel(AB,CD);Perpendicular(DC,BA)',
 'FakeRelation(AB,CD)', 'Length(A,A)=5','Angle(A,A,B)=30',
 'Length(A,B)=-2','Length(A,B)=1/0','Length(A,B)=5deg',
 'Tangent(O,AB)','Perpendicular(AB,AB)',
 ])
def test_invalid_and_conflicting_facts_cannot_score(bad):
    with pytest.raises(GeometryError): canonicalize(bad)
    assert perception_f1(bad,'Length(A,B)=5',{'Length'})['f1']==0


def test_vertex_directed_roles_and_tangent_roles_preserved():
    assert parse_fact('Angle(A,B,C)=60')!=parse_fact('Angle(A,C,B)=60')
    assert parse_fact('DirectedAngle(A,B,C)=60')!=parse_fact('DirectedAngle(C,B,A)=60')
    assert canonicalize('Tangent(BA,O)')=='Tangent(AB,O)'
    assert canonicalize('Length(A2,A10)=5')=='Length(A10,A2)=5'


def test_units_values_and_normalization():
    assert canonicalize('Length(BA)=0.5cm')=='Length(A,B)=1/2cm'
    assert parse_fact('Angle(A,B,C)=60deg')==parse_fact('Angle(C,B,A)=60°')
    assert perception_f1('Length(A,B)=5cm','Length(A,B)=5m',{'Length'})['f1']==0


def test_response_three_sections():
    text = '<perception>Length(B,A)=5</perception><reasoning>Use length.</reasoning><answer>10</answer>'
    r = parse_response(text)
    assert r['canonical_perception']=='Length(A,B)=5' and r['answer']=='10'
    for bad in [text+'trailing',text.replace('</answer>',''),text.replace('<answer>10','<answer>'),
                text.replace('Use length.','<answer>1</answer>')]:
        with pytest.raises(GeometryError): parse_response(bad)


def test_empty_predictions_and_coverage_errors():
    assert perception_f1('','Length(A,B)=5',{'Length'})['f1']==0
    with pytest.raises(GeometryError): perception_f1('','Length(A,B)=5',{'Angle'})
