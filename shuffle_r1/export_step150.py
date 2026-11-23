#!/usr/bin/env python3
"""Stage verified checkpoint 150 for inference, offline; no training/optimizer inputs."""
import argparse
import hashlib
import json
import os
import pathlib
import shutil
import tempfile

PF = "a392f10722b0c73227e79f5ad3e561e358d4c0886c3f9829b87bfadade656eea"

def sha(p):
    with p.open("rb") as f:
        return hashlib.file_digest(f, "sha256").hexdigest()

def main():
    if not __debug__:
        raise RuntimeError("Use Python without -O so checkpoint verification remains enabled")
    p=argparse.ArgumentParser()
    p.add_argument("--source",type=pathlib.Path,required=True,help="Root with actor/model_world_size_1_rank_0.pt and actor/huggingface/")
    p.add_argument("--manifest",type=pathlib.Path,required=True)
    p.add_argument("--expected-export",type=pathlib.Path,help="Optional original EXPORT_VERIFIED.json")
    p.add_argument("--out",type=pathlib.Path,required=True)
    args=p.parse_args()
    assert sha(args.manifest)==PF, "not pinned 150 input manifest"
    manifest=json.loads(args.manifest.read_text())
    assert (manifest["global_step"],manifest["optimizer_steps"],manifest["scheduler_steps"])==(150,600,150)
    model_rel="actor/model_world_size_1_rank_0.pt"
    entries={k:v for k,v in manifest["files"].items() if k.startswith("actor/huggingface/") or k==model_rel}
    assert len(entries)==12 and model_rel in entries, "missing manifest input"
    for name,info in entries.items():
        f=args.source/name
        assert f.is_file() and f.stat().st_size==info["bytes"] and sha(f)==info["sha256"], f"corrupt or missing {name}"
    print("P3_CKPT150_INPUT_VERIFIED",flush=True)
    if args.out.exists():
        raise FileExistsError(args.out)
    args.out.parent.mkdir(parents=True,exist_ok=True)
    with tempfile.TemporaryDirectory(prefix=".p3-export-",dir=args.out.parent) as tmp:
        stage=pathlib.Path(tmp)/"model";stage.mkdir()
        import torch
        from torch.distributed.tensor import DTensor
        from huggingface_hub import save_torch_state_dict
        from safetensors import safe_open
        from transformers import Qwen2_5_VLForConditionalGeneration,AutoConfig
        from collections.abc import Mapping
        raw=torch.load(args.source/model_rel,map_location="cpu",mmap=True,weights_only=False)
        assert isinstance(raw,Mapping) and len(raw)==825, "unexpected actor state structure"
        state={}
        seen_storage=set()
        for k,v in raw.items():
            assert isinstance(k,str) and isinstance(v,torch.Tensor), (k,type(v))
            if isinstance(v,DTensor):
                assert v.device_mesh.size()==1, f"not a full local shard: {k}"
                v=v.to_local()
            assert isinstance(v,torch.Tensor) and v.device.type=="cpu" and v.layout==torch.strided, k
            sid=(v.untyped_storage().data_ptr(),v.untyped_storage().nbytes())
            # Preserve every checkpoint key, including any tied alias; HF's saver otherwise drops duplicate storage.
            if sid in seen_storage:
                v=v.clone()
            seen_storage.add(sid)
            state[k]=v
        for name in entries:
            if name!=model_rel:
                f=args.source/name
                shutil.copyfile(f,stage/f.name)
        cfg=AutoConfig.from_pretrained(stage,local_files_only=True,trust_remote_code=False)
        with torch.device("meta"):
            skeleton=Qwen2_5_VLForConditionalGeneration(cfg)
        wanted=skeleton.state_dict()
        del skeleton
        assert wanted.keys()==state.keys(), f"key difference: missing={list(wanted.keys()-state.keys())[:15]} unexpected={list(state.keys()-wanted.keys())[:15]}"
        for k,v in state.items():
            assert wanted[k].shape==v.shape, k
        del wanted
        save_torch_state_dict(state,stage,max_shard_size=2147483648,safe_serialization=True,force_contiguous=True)
        seen=set()
        for f in sorted(stage.glob("*.safetensors")):
            with safe_open(f,framework="pt",device="cpu") as h:
                for k in h.keys():
                    got=h.get_tensor(k)
                    assert k not in seen and k in state and got.dtype==state[k].dtype and got.shape==state[k].shape and torch.equal(got,state[k]),k
                    seen.add(k)
        assert seen==state.keys(), f"{len(seen)} of {len(state)} tensor keys survived"
        files={f.name:{"bytes":f.stat().st_size,"sha256":sha(f)} for f in stage.iterdir() if f.is_file()}
        alike=None
        if args.expected_export:
            proof=json.loads(args.expected_export.read_text())
            assert proof["checkpoint"]==150 and proof["input_manifest_sha256"]==PF
            alike=files==proof["files"]
        receipt={"checkpoint":150,"source_sha256":entries[model_rel]["sha256"],"source_manifest_sha256":PF,"tensor_count":len(seen),"tensor_roundtrip_equal":True,"identical_to_previous_export":alike,"files":files}
        (stage/"P3_STAGE_RECEIPT.json").write_text(json.dumps(receipt,sort_keys=True,indent=2)+"\n")
        stage.rename(args.out)
        print(json.dumps({k:v for k,v in receipt.items() if k!="files"}),flush=True)

if __name__=="__main__":
    os.environ.update(HF_HUB_OFFLINE="1",TRANSFORMERS_OFFLINE="1")
    main()
