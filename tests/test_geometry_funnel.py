from scripts.data.build_geometry_funnel_v8 import classify

def sample():
    return {'split':'train','response_received':True,'review':{'valid':True,'task_status':'pass','facts':[{'index':0}]},'pruning':{'accepted':False,'positive_tokens':[],'masked':[]},'release_approved':False}

def test_format_failure_precedes_parser_uncertain():
    r=sample();r['review'].update(valid=False,task_status='uncertain')
    assert classify(r,True,True)[0]=='格式失败'

def test_all_text_is_distinct_from_mixed_no_positive():
    r=sample();r['pruning']['masked']=[{'index':0,'status':'text'}]
    assert classify(r,True,True)[0]=='全部事实被文字蕴含剔除'
    r['review']['facts'].append({'index':1});r['pruning']['masked'].append({'index':1,'status':'uncertain'})
    assert classify(r,True,True)[0]=='无剩余认证事实'

def test_task_uncertainty_precedes_image_and_independent_resolution_is_used():
    r=sample();r['review']['task_status']='uncertain';r['pruning'].update(accepted=True,positive_tokens=['fact'])
    assert classify(r,True,True)[0]=='题答 uncertain'
    r['independent_task_resolution']='recorded proof'
    assert classify(r,True,True)[0]=='同图隔离'
