"""Write explicit initial A100 smoke configs; no weight downloads or execution."""
import json
from pathlib import Path

def run():
    root=Path(__file__).resolve().parents[1];out=root/'project_blueprints/configs/approved_release_20261024';out.mkdir(parents=True,exist_ok=True)
    manifest=str(root/'data/delegated_ai_releases_20261024/manifest.json');audit=json.loads((root/'reports/tokenizer_alignment_report.json').read_text(encoding='utf-8'));models={r['model']:r['revision'] for r in audit['models']}
    def save(name,c): (out/(name+'.json')).write_text(json.dumps(c,ensure_ascii=False,indent=2),encoding='utf-8')
    base={'data_manifest':manifest,'model':'Qwen/Qwen2.5-7B-Instruct','model_revision':models['Qwen/Qwen2.5-7B-Instruct'],'tokenizer_path':str(root/'data/tokenizers/Qwen2.5-7B-Instruct'),'seed':42,'max_steps':2,'learning_rate':2e-5,'batch_size':1,'gradient_accumulation_steps':8,'save_steps':1,'max_length':3800,'export_merged_base':True,'stage':'sft','vision':False}
    for arm in ['raw','compact']:
        c={**base,'data_file':f'project1_{arm}_paired_ai_approved.jsonl','output_dir':str(root/f'runs/project1_{arm}_sft_smoke')};save(f'project1_{arm}_sft_smoke',c)
        for alg in ['grpo','dr_grpo']:
            r={**c,'stage':'rl','initial_state':'sft','model':str(Path(c['output_dir'])/'merged'),'model_revision':'local-merged-with-weight-manifest','max_new_tokens':2048,'algorithm':alg,'num_generations':4,'generation_batch_size':4,'beta':.04,'output_dir':str(root/f'runs/project1_{arm}_{alg}_smoke')};save(f'project1_{arm}_{alg}_smoke',r)
    def spec(name):return {'model':name,'revision':models[name]}
    save('project2_opd_smoke',{'data_manifest':manifest,'data_files':{'math':'project2_math_train_ai_approved.jsonl','code':'project2_code_train_ai_approved.jsonl'},'student':spec('Qwen/Qwen2.5-1.5B-Instruct'),'teachers':{'math':spec('Qwen/Qwen2.5-Math-7B-Instruct'),'code':spec('Qwen/Qwen2.5-Coder-7B-Instruct')},'tokenizer_audit':str(root/'reports/tokenizer_alignment_report.json'),'tokenizer_path':str(root/'data/tokenizers/Qwen2.5-1.5B-Instruct'),'seed':42,'max_steps':2,'domain_order':['math','code'],'domain_block_steps':1,'learning_rate':2e-5,'gradient_accumulation_steps':1,'max_new_tokens':{'math':1024,'code':1536},'save_steps':1,'output_dir':str(root/'runs/project2_opd_smoke')})
    save('project3_perception_sft_smoke',{**base,'model':'Qwen/Qwen2.5-VL-3B-Instruct','model_revision':'66285546d2b821cf421d4f5eb2576359d3770cd3','data_file':'project3_perception_prototype_ai_approved.jsonl','vision':True,'max_pixels':802816,'export_merged_base':False,'output_dir':str(root/'runs/project3_perception_sft_smoke')})
    print(out)

if __name__=='__main__':run()
