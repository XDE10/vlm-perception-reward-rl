"""Constructed CPU callback demonstration; not model-generated predictions."""
import json
from pathlib import Path
from .project3_v2 import LoggedRewards,summarize_rollouts

def main():
    out=Path(__file__).parent
    path=out/'constructed_reward_log.jsonl'
    if path.exists():raise FileExistsError('Preserve existing demo evidence')
    logger=LoggedRewards(path,.2,origin='constructed_CPU_test_NOT_model_predictions')
    texts=['<perception>Length(A,C)=1; Length(C,D)=6; Length(A,C)=2; Parallel((A,B),(D,E))</perception><answer>4</answer>',
           '<perception>Angle(A,B)=60 deg</perception><answer>3</answer>']
    logger.answer_reward(texts,['4','4'],['constructed_1','constructed_2'],[['Length(A,C)=1','Length(C,D)=6'],['Length(A,C)=1']],[[],[]])
    records=[json.loads(x) for x in path.read_text(encoding='utf8').splitlines()]
    (out/'constructed_monitoring.json').write_text(json.dumps(summarize_rollouts(records),ensure_ascii=False,indent=2),encoding='utf8')

if __name__=='__main__':main()
