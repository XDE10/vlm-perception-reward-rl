from src.data.geometry_split_guard import guard

def test_test_then_validation_then_train_pixel_precedence():
    links=[{'wrapper_locator':s+':1','wrapper_split':s,'original_id':s,'image_pixel_sha256':'a'*64} for s in ['train','validation','test']]
    records=[{'sample_id':s+':1','split':s,'original_id':s,'training_approved':s=='train'} for s in ['train','validation']]
    kept,rejected=guard(records,links)
    assert not kept and len(rejected)==2
    assert all(r['training_approved'] is False and r['evaluation_approved'] is False for r in rejected)

def test_unseen_train_image_survives_but_missing_identity_cannot():
    links=[{'wrapper_locator':'train:1','wrapper_split':'train','original_id':'1','image_pixel_sha256':'b'*64}]
    records=[{'sample_id':'train:1','split':'train','original_id':'1'},{'sample_id':'train:2','split':'train','original_id':'2'}]
    kept,rejected=guard(records,links)
    assert len(kept)==len(rejected)==1 and kept[0]['image_split_guard_passed']
