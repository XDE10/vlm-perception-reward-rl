"""Separate audit identities from model-facing geometry text.

Source radius IDs never enter serialized text. Unverified point/circle grounding
cannot silently become an approved training target.
"""
import json,re


def circle_key(value):return json.dumps(value,sort_keys=True,separators=(',',':'))


def circles_in(value):
    if isinstance(value,dict):
        if 'source_radius_id' in value and 'center' in value:yield value
        for x in value.values():yield from circles_in(x)
    elif isinstance(value,(tuple,list)):
        for x in value:yield from circles_in(x)


def points_in(value):
    if isinstance(value,str) and re.fullmatch('[A-Z][0-9]*',value):yield value
    elif isinstance(value,dict):
        for k,v in value.items():
            if k not in {'source_radius_id','shape','kind'}:yield from points_in(v)
    elif isinstance(value,(tuple,list)):
        for x in value:yield from points_in(x)


def render(facts,visible_points=None,circle_bindings=None):
    """Bindings are image-grounded aliases supplied after review, not inferred IDs."""
    circle_bindings=circle_bindings or {};circle_values={circle_key(c):c for f in facts for c in circles_in(f['entities'])}
    centers={}
    for key,c in circle_values.items():centers.setdefault(c['center'],[]).append(key)
    visibility_known=visible_points is not None;visible=set(visible_points or []);issues=[]
    if not facts:issues.append('no_visual_candidates; empty_target_not_reviewed')
    def entity(v):
        if isinstance(v,str):return v
        if isinstance(v,(tuple,list)):return '('+','.join(entity(x) for x in v)+')'
        if 'source_radius_id' in v:
            key=circle_key(v);binding=circle_bindings.get(key)
            if binding:
                if not re.fullmatch(r'Circle(?:\([A-Z][0-9]*\)|[1-9][0-9]*|)',binding):raise ValueError('invalid_visible_circle_binding')
                if binding=='Circle' and len(circle_values)>1:raise ValueError('generic_circle_would_merge_distinct_circles')
                return binding
            if len(centers[v['center']])>1:raise ValueError('concentric_circle_identity_requires_visible_grounding')
            if not visibility_known or v['center'] not in visible:issues.append('circle_center_label_not_confirmed_visible')
            return 'Circle('+v['center']+')'
        if 'boundary' in v:return v['shape']+'('+','.join(v['boundary'])+')'
        if 'points' in v:return v['kind']+'Arc('+','.join(v['points'])+')'
        raise ValueError('unknown_entity_schema')
    text=[]
    for f in facts:
        required=set(points_in(f['entities']))
        # A binding may replace an invisible source center. Other point aliases
        # still need grounding even when a circle has a reviewed alias.
        for c in circles_in(f['entities']):
            if circle_key(c) in circle_bindings:required.discard(c['center'])
        if not visibility_known or not required<=visible:issues.append('point_labels_or_coordinate_grounding_not_reviewed')
        value=f.get('value','');unit=f.get('unit','')
        args=','.join(entity(x) for x in f['entities']) if isinstance(f['entities'],(tuple,list)) else entity(f['entities'])
        token=f["relation"]+'('+args+')'
        if value:token+='='+value+(' deg' if unit=='deg' else '')
        text.append(token)
    preview='<perception>'+'; '.join(text)+'</perception>'
    if re.search(r'radius_[A-Za-z0-9_]*|source_radius_id',preview):raise ValueError('source_identity_leak')
    return {'annotation_only_preview':preview,'model_perception':preview if not issues else None,
        'grounding_status':'reviewed_visible_labels' if not issues else 'pending_image_grounding',
        'issues':sorted(set(issues)),'training_approved':False}
