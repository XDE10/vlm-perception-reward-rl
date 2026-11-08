"""Public trainer callback; sparse labels are private reward metadata only."""
from src.data.perception_v4 import perception_reward,scoped_score

def validate_reward_rows(rows):
    for r in rows:
        if r.get('perception_reward_mode')!='sparse_certified_v4' or not r.get('perception_reward_enabled') or not r.get('certified_positive_tokens') or r.get('split')!='train':
            raise ValueError('V4 requires approved train rows with nonempty certified facts and explicit sparse scope')
        if not isinstance(r.get('certified_negative_tokens'),list):raise ValueError('Explicit negative list required (may be empty)')
