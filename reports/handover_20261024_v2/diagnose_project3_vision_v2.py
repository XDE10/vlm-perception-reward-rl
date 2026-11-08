"""Paired original/black/no-image/occluded diagnostics on identical fixed IDs."""
import argparse,json,hashlib
from pathlib import Path
from src.training.approved_hf import check_math
from .project3_v2 import messages,answer_score,PROTOCOL

def weight_sha(path):
    if not path:return None
    root=Path(path)
    if not root.is_dir():raise ValueError('Adapter/local weight directory missing')
    files=[p for p in root.rglob('*') if p.is_file()]
    if not files:raise ValueError('Empty weight directory')
    result={}
    for p in sorted(files):
        h=hashlib.sha256()
        with p.open('rb') as f:
            for chunk in iter(lambda:f.read(4*1024*1024),b''):h.update(chunk)
        result[p.relative_to(root).as_posix()]=h.hexdigest()
    return result

def begin_identity(args):
    output=Path(args.output);output.parent.mkdir(parents=True,exist_ok=True)
    identity={'schema':'vision-diagnostic-v2','protocol':PROTOCOL,'status':'started','config':vars(args),
        'data_sha256':hashlib.sha256(Path(args.data).read_bytes()).hexdigest(),
        'adapter_sha256':weight_sha(args.adapter),'local_model_sha256':weight_sha(args.model) if Path(args.model).is_dir() else None,
        'occlusion':'fixed central 50% width/height; input perturbation, not geometric oracle',
        'actual_GPU_validation':'未验证'}
    with Path(args.output+'.identity.json').open('x',encoding='utf8') as f:json.dump(identity,f,ensure_ascii=False,indent=2)
    return identity

def perturb(image,mode):
    from PIL import Image,ImageDraw
    if mode=='none':return None
    if mode=='black':return Image.new('RGB',image.size,'black')
    result=image.copy()
    if mode=='occluded':
        w,h=image.size;ImageDraw.Draw(result).rectangle((w//4,h//4,3*w//4,3*h//4),fill='black')
    return result

def main():
    p=argparse.ArgumentParser();p.add_argument('--model',default='Qwen/Qwen2.5-VL-3B-Instruct');p.add_argument('--revision',default='66285546d2b821cf421d4f5eb2576359d3770cd3');p.add_argument('--adapter');p.add_argument('--data',required=True);p.add_argument('--image-archive-root',default='data/project3_sources/intergps/data/geometry3k');p.add_argument('--output',required=True);p.add_argument('--max-new-tokens',type=int,default=2048);a=p.parse_args()
    identity=begin_identity(a)
    try:
        run_diagnostic(a)
        identity['status']='completed'
    except BaseException as exc:
        identity['status']='failed_or_interrupted';identity['error_type']=type(exc).__name__
        raise
    finally:
        Path(a.output+'.identity.json').write_text(json.dumps(identity,ensure_ascii=False,indent=2),encoding='utf8')

def run_diagnostic(a):
    import torch
    from PIL import Image
    from transformers import AutoModelForVision2Seq,AutoProcessor
    if not torch.cuda.is_available():raise RuntimeError('Visual model diagnostic requires CUDA')
    if a.revision=='main':raise ValueError('Pin model revision')
    processor=AutoProcessor.from_pretrained(a.model,revision=a.revision,max_pixels=802816,local_files_only=True);model=AutoModelForVision2Seq.from_pretrained(a.model,revision=a.revision,torch_dtype=torch.bfloat16,attn_implementation='sdpa',local_files_only=True).to('cuda').eval()
    if a.adapter:
        from peft import PeftModel
        model=PeftModel.from_pretrained(model,a.adapter,local_files_only=True).eval()
    seen=set();data=Path(a.data)
    with data.open(encoding='utf-8') as f,Path(a.output).open('x',encoding='utf-8') as out:
        for line in f:
            r=json.loads(line)
            if r['sample_id'] in seen:raise ValueError('Duplicate diagnostic ID')
            seen.add(r['sample_id'])
            if 'image_path' in r:raw=Image.open(r['image_path']).convert('RGB')
            else:
                import io,zipfile
                archive,member=r['image_source_locator'].split('::',1)
                if Path(archive).name!=archive:raise ValueError('Invalid image archive locator')
                with zipfile.ZipFile(Path(a.image_archive_root)/archive) as z:raw=Image.open(io.BytesIO(z.read(member))).convert('RGB')
            if r.get('image_sha256') and hashlib.sha256(Path(r['image_path']).read_bytes()).hexdigest()!=r['image_sha256']:raise ValueError('Image changed')
            for mode in ['original','black','none','occluded']:
                image=perturb(raw,mode);conversation=messages(r)
                if image is None:conversation[-1]['content']=[x for x in conversation[-1]['content'] if x['type']!='image']
                text=processor.apply_chat_template(conversation,tokenize=False,add_generation_prompt=True)
                inputs=processor(text=[text],images=[image] if image is not None else None,return_tensors='pt').to('cuda')
                if mode=='none' and any(k in inputs for k in ['pixel_values','image_grid_thw']):raise ValueError('No-image condition contains visual tensors')
                with torch.no_grad():ids=model.generate(**inputs,do_sample=False,max_new_tokens=a.max_new_tokens)
                response=processor.tokenizer.decode(ids[0,inputs['input_ids'].shape[1]:],skip_special_tokens=True)
                generated=ids[0,inputs['input_ids'].shape[1]:]
                eos=model.generation_config.eos_token_id;eos=eos if isinstance(eos,list) else [eos]
                ended=bool(len(generated) and int(generated[-1]) in eos)
                out.write(json.dumps({'sample_id':r['sample_id'],'mode':mode,'text':response,'verification':answer_score(response,r['reference_answer']),
                    'prompt_tokens':inputs['input_ids'].shape[1],'generated_tokens':len(generated),'ended_eos':ended,
                    'budget_exhausted':len(generated)>=a.max_new_tokens and not ended,
                    'visual_tensor_keys':[k for k in inputs if k in ['pixel_values','image_grid_thw']]},ensure_ascii=False)+'\n');out.flush()

if __name__=='__main__':main()
