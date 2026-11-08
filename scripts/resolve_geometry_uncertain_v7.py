"""One recorded independent pixel+exact-proof adjudication; no new API."""
import sympy as sp
from scripts.finalfill_common import *
def run():
    cases={r['original_id']:r for p in [ROOT/'data/topup_v6_20261024/project3/cases.jsonl',ROOT/'data/topup_v6_20261024/project3_reserve/cases.jsonl'] for r in rows(p)}
    c=cases['1683'];a=3/sp.sqrt(2);W=sp.Matrix([a,a]);X=sp.Matrix([-a,a]);Y=sp.Matrix([-a,-a]);Z=sp.Matrix([a,-a]);T=sp.zeros(2,1)
    sides=[sp.simplify((u-v).dot(u-v)) for u,v in [(W,X),(X,Y),(Y,Z),(Z,W)]]
    assert sides==[18]*4 and sp.simplify((W-T).dot(Z-T))==0 and sp.simplify((W-T).dot(W-T))==9
    assert W+Y==2*T and X+Z==2*T and c['reference_answer']=='90' and 'WXYZ is a square' in c['problem']
    proof={'original_id':'1683','question':c['problem'],'stored_answer':'90','image_sha256':sha(c['image_path']),'method':'Codex direct original pixels + exact square coordinate witness/theorem; not human review','pixel_evidence':'Printed W/X/Y/Z/T; T lies at the drawn WY/XZ diagonal intersection. Corner right angles follow from square text and are masked as text-derived, not image-only.','certified_image_only_tokens':['PointLiesOnLine(T,(W,Y))','PointLiesOnLine(T,(X,Z))'],'mathematical_evidence':{'square_equal_side_squared':18,'WT_squared':9,'diagonal_dot_product':0,'diagonal_intersection':'T=(W+Y)/2=(X+Z)/2','angle_WTZ_degrees':90},'previous_AI_claim_refuted':'At vertex T, TW and TZ are rays on the two diagonals, not a diagonal and boundary side. Square diagonals are perpendicular.','human_review_performed':False,'api_calls':0}
    dump(REPORT/'geometry_1683_independent_proof.json',proof)
    dump(REPORT/'geometry_1423_kept_uncertain.json',{'original_id':'1423','reason':'Angle-sum algebra yields x=68 and3x-11=193, but the actual diagram appears convex at V; do not promote solely because it matches the source answer. Exact geometric feasibility/angle-role ambiguity remains unresolved.','human_review_performed':False,'api_calls':0})
    print('1683 independently resolved;1423 remains uncertain; no API calls',flush=True)
if __name__=='__main__':run()
