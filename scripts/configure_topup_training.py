"""Versioned smoke configs for approved V6 rows, not a GPU acceptance claim."""
from scripts.topup_common import *
def run():
    out=DATA/'training_configs';out.mkdir(exist_ok=True);release=DATA/'release';m=read(release/'manifest.json')
    old=ROOT/'project_blueprints/configs/approved_release_20261024'
    for name in ['project1_raw_sft_smoke','project1_compact_sft_smoke','project2_opd_smoke']:
        c=read(old/(name+'.json'));c['data_manifest']=str(release/'manifest.json');c['output_dir']=str(ROOT/'runs'/('topup_v6_'+name))
        if name.startswith('project1'):c['data_file']='project1_'+('raw' if 'raw' in name else 'compact')+'_paired.jsonl'
        else:c['data_files']={'math':'project2_math_train.jsonl','code':'project2_code_train.jsonl'}
        dump(out/(name+'.json'),c)
    c=read(old/'project3_perception_sft_smoke.json');c.update(data_manifest=str(release/'manifest.json'),data_file='project3_train_fact_pruned.jsonl',export_merged_base=True,output_dir=str(ROOT/'runs/topup_v6_project3_perception_sft_smoke'))
    dump(out/'project3_fact_sft_smoke.json',c)
    rl={**c,'stage':'rl','initial_state':'sft','model':str(Path(c['output_dir'])/'merged'),'model_revision':'local-merged-with-weight-manifest','reward_mode':'sparse_certified_v4','perception_reward_weight':.2,'algorithm':'grpo','max_new_tokens':2048,'num_generations':4,'generation_batch_size':4,'beta':.04,'output_dir':str(ROOT/'runs/topup_v6_project3_sparse_grpo_smoke')}
    dump(out/'project3_sparse_v4_grpo_smoke.json',rl)
    for alg in ['grpo','dr_grpo']:
        for arm in ['raw','compact']:
            c=read(old/f'project1_{arm}_{alg}_smoke.json');c.update(data_manifest=str(release/'manifest.json'),data_file=f'project1_{arm}_paired.jsonl',model=str(ROOT/f'runs/topup_v6_project1_{arm}_sft_smoke/merged'),output_dir=str(ROOT/f'runs/topup_v6_project1_{arm}_{alg}_smoke'));dump(out/f'project1_{arm}_{alg}_smoke.json',c)
    dump(out/'manifest.json',{'approved_data_manifest_sha':sha(release/'manifest.json'),'files':{p.name:sha(p) for p in out.glob('*.json') if p.name!='manifest.json'},'gpu_executed':False,'visual_reward':'sparse TP/explicit FP only; unknown masked; not full-image precision'})
if __name__=='__main__':run()
