from src.data.project3_perception_preview import preview

def candidate(relation,entities,value='',unit='',number='x'):
    return dict(category='visual_candidate',fact=dict(relation=relation,entities=entities,value=value,unit=unit),fact_id=number,raw=number)

def test_fixed_order_fraction_dedup_and_angle_vertex():
    rows=[candidate('Parallel',[['D','C'],['B','A']]),
          candidate('Length',['B','A'],'2/4','unspecified_source_unit','1'),
          candidate('Angle',['C','B','A'],'90.0','deg'),
          candidate('Length',['A','B'],'0.5','unspecified_source_unit','2')]
    result=preview(rows)
    assert [x['fact']['relation'] for x in result['canonical_facts']]==['Angle','Length','Parallel']
    assert result['canonical_facts'][0]['fact']['entities']==['A','B','C']
    assert result['canonical_facts'][1]['canonical']=='Length(A,B)=1/2'
    assert result['canonical_facts'][1]['source_fact_ids']==['1','2']

def test_tangent_preserves_line_center_roles():
    result=preview([candidate('Tangent',[['B','A'],'O'])])
    assert result['canonical_facts'][0]['canonical']=='Tangent(AB,O)'
    assert result['review_only'] and not result['training_approved']

def test_numeric_and_parallel_conflicts_are_all_quarantined():
    result=preview([candidate('Length',['A','B'],'2','unspecified_source_unit'),
                    candidate('Length',['B','A'],'3','unspecified_source_unit'),
                    candidate('Parallel',[['A','B'],['C','D']]),
                    candidate('Perpendicular',[['D','C'],['B','A']])])
    assert not result['canonical_facts']
    assert len(result['quarantined'])==4

def test_non_candidate_and_congruent_cannot_enter_preview():
    item=candidate('Angle',['A','B','C'],'30','deg');item['category']='text_explicit'
    result=preview([item,candidate('Congruent',[['A','B'],['C','D']])])
    assert not result['canonical_facts']
    assert len(result['quarantined'])==1
