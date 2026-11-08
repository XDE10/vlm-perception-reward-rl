"""Paired original/black/no-image/occluded diagnostics on identical fixed IDs."""
import argparse,json,hashlib
from pathlib import Path
from src.training.approved_hf import check_math

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
    import torch
    from PIL import Image
    from transformers import AutoProcessor
    from src.training.hf_compat import vision_model_class
    if not torch.cuda.is_available():raise RuntimeError('Visual model diagnostic requires CUDA')
    if a.revision=='main':raise ValueError('Pin model revision')
    processor=AutoProcessor.from_pretrained(a.model,revision=a.revision,max_pixels=802816);model=vision_model_class().from_pretrained(a.model,revision=a.revision,dtype=torch.bfloat16,attn_implementation='sdpa').to('cuda').eval()
    if a.adapter:
        from peft import PeftModel
        model=PeftModel.from_pretrained(model,a.adapter).eval()
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
                image=perturb(raw,mode);content=([{'type':'image'}] if image is not None else [])+[{'type':'text','text':r['problem'].removeprefix('<image>').strip()+r' Put the final answer within \boxed{}.'}]
                text=processor.apply_chat_template([{'role':'user','content':content}],tokenize=False,add_generation_prompt=True)
                inputs=processor(text=[text],images=[image] if image is not None else None,return_tensors='pt').to('cuda')
                with torch.no_grad():ids=model.generate(**inputs,do_sample=False,max_new_tokens=a.max_new_tokens)
                response=processor.tokenizer.decode(ids[0,inputs['input_ids'].shape[1]:],skip_special_tokens=True)
                out.write(json.dumps({'sample_id':r['sample_id'],'mode':mode,'text':response,'verification':check_math(response,r['reference_answer'])},ensure_ascii=False)+'\n');out.flush()
    Path(a.output+'.identity.json').write_text(json.dumps({'config':vars(a),'data_sha256':hashlib.sha256(data.read_bytes()).hexdigest(),'occlusion':'fixed central 50% width/height; input perturbation, not geometric oracle'},indent=2),encoding='utf-8')

if __name__=='__main__':main()
