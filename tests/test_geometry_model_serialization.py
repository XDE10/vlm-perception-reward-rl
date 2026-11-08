import pytest
from src.data.geometry_model_serialization import render,circle_key


def test_internal_ids_removed_but_unknown_labels_not_training_targets():
    c={'center':'B','source_radius_id':'radius_3_0'}
    f={'relation':'PointLiesOnCircle','entities':['A',c],'value':'','unit':''}
    r=render([f]);assert 'radius_' not in r['annotation_only_preview'];assert r['model_perception'] is None
    r=render([f],{'A'},{circle_key(c):'Circle'})
    assert r['model_perception']=='<perception>PointLiesOnCircle(A,Circle)</perception>'
    assert render([f],{'A','B'})['model_perception']=='<perception>PointLiesOnCircle(A,Circle(B))</perception>'


def test_concentric_circles_never_collapsed():
    assert render([])['model_perception'] is None
    cs=[{'center':'B','source_radius_id':'radius_'+str(i)} for i in range(2)]
    fs=[{'relation':'PointLiesOnCircle','entities':['A',c],'value':'','unit':''} for c in cs]
    with pytest.raises(ValueError):render(fs,{'A','B'})
    with pytest.raises(ValueError):render(fs,{'A'},{circle_key(c):'Circle' for c in cs})
