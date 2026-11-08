"""Reserve evaluation pixel identities; inspect no held-out answers or facts."""
def guard(records,links):
    by={r['wrapper_locator']:r for r in links}
    test={r['image_pixel_sha256'] for r in links if r['wrapper_split']=='test'}
    evaluation={r['image_pixel_sha256'] for r in links if r['wrapper_split'] in {'test','validation'}}
    kept=[];excluded=[]
    for r in records:
        image=by.get(r['sample_id']);reason=None
        if not image or image.get('original_id')!=r['original_id']:reason='missing_or_mismatched_pixel_identity'
        else:
            pixel=image.get('image_pixel_sha256')
            if not isinstance(pixel,str) or len(pixel)!=64:reason='invalid_pixel_digest'
            elif r['split']=='train' and pixel in evaluation:reason='pixel_identity_reserved_by_validation_or_test'
            elif r['split']=='validation' and pixel in test:reason='pixel_identity_reserved_by_test'
        if reason:excluded.append({**r,'training_approved':False,'evaluation_approved':False,'image_split_guard_reason':reason})
        else:kept.append({**r,'image_pixel_sha256':pixel,'image_split_guard_passed':True})
    return kept,excluded
