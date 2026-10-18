#!/usr/bin/env python3
"""Portable read-only arithmetic acceptance of the fixed N>=180 evidence.

No extraction, file writes, historical imports, searches or optimization.
Results go to stdout; progress goes to stderr. Use Python 3.10 or later.
"""
import sys
sys.dont_write_bytecode = True
from pathlib import Path, PurePosixPath
from fractions import Fraction
import argparse
import hashlib
import importlib
import json
import time
import zipfile

ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/'validation'))

class AcceptanceError(ValueError):pass

def unique_json(data):
 def pairs(items):
  d={}
  for k,v in items:
   if k in d:raise AcceptanceError('duplicate JSON key: '+k)
   d[k]=v
  return d
 return json.loads(data,object_pairs_hook=pairs)

def sha_stream(stream):
 h=hashlib.sha256()
 for block in iter(lambda:stream.read(1<<20),b''):h.update(block)
 return h.hexdigest()

class Context:
 def __init__(self,archive,index):
  self.archive=Path(archive);self.index=unique_json(Path(index).read_text(encoding='utf-8'))
  self.zip=zipfile.ZipFile(self.archive);self.cache={};self.facts={};self.checks=0
  self.inputs={};self.stage='integrity';self.by_stage={};self.trace=None;self.started=time.monotonic()
 def require(self,condition,label):
  self.checks+=1;self.by_stage[self.stage]=self.by_stage.get(self.stage,0)+1
  if self.trace is not None:self.trace.append({'check':label,'accepted':bool(condition)})
  if not condition:raise AcceptanceError(self.stage+': '+label)
 def progress(self,label):
  print(json.dumps(dict(stage=self.stage,message=label,checks=self.checks,
       elapsed_seconds=round(time.monotonic()-self.started,2))),file=sys.stderr,flush=True)
 def note(self,*args):self.progress(' '.join(map(str,args)))
 def read(self,name):
  name=str(name).replace('\\','/')
  p=PurePosixPath(name)
  self.require(not p.is_absolute() and '..' not in p.parts and ':' not in name,'archive-relative input')
  if name in self.cache:return self.cache[name]
  raw=self.zip.read(name);self.inputs[name]=hashlib.sha256(raw).hexdigest()
  value=unique_json(raw.decode('utf-8-sig'))
  if len(raw)<25_000_000:self.cache[name]=value
  return value
 def drop(self,name):self.cache.pop(name,None)
 def bytes(self,name):return self.zip.read(name)
 def integrity(self):
  index=self.index
  self.require(index['format']=='codim2-180-supplement-v1','index format')
  with self.archive.open('rb') as f:actual=sha_stream(f)
  self.require(actual==index['archive']['sha256'],'archive SHA256')
  self.require(self.archive.stat().st_size==index['archive']['size'],'archive size')
  expected={x['path']:x for x in index['members']}
  self.require(len(expected)==len(index['members']),'unique declared names')
  infos=self.zip.infolist()
  self.require(len(infos)==len(expected) and {x.filename for x in infos}==set(expected),'exact membership')
  for item in infos:
   p=PurePosixPath(item.filename)
   self.require(not item.is_dir() and not p.is_absolute() and '..' not in p.parts
          and ':' not in item.filename and '\\' not in item.filename,'safe member name')
   target=expected[item.filename]
   self.require(item.file_size==target['size'],'member length: '+item.filename)
   with self.zip.open(item) as f:digest=sha_stream(f)
   self.require(digest==target['sha256'],'member SHA256: '+item.filename)
  return dict(members=len(infos),sha256=actual,scope='integrity only; arithmetic follows')

def encode(value):
 if isinstance(value,Fraction):return str(value)
 if isinstance(value,Path):return str(value)
 raise TypeError(type(value).__name__)

def main():
 parser=argparse.ArgumentParser(description=__doc__)
 parser.add_argument('--archive',type=Path,default=ROOT/'certificate/supplement.zip')
 parser.add_argument('--index',type=Path,default=ROOT/'certificate/INDEX.json')
 parser.add_argument('--stage',choices=['all','global','continuous','local'],default='all',
   help='diagnostics; local first recomputes global and continuous dependencies; only all reports complete acceptance')
 args=parser.parse_args();ctx=None
 try:
  ctx=Context(args.archive,args.index);ctx.progress('fixed archive integrity')
  reports={'integrity':ctx.integrity()}
  code_hashes={'certificate/verify_certificates.py':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
  stages=['global','continuous','local'] if args.stage in ('all','local') else [args.stage]
  for stage in stages:
   ctx.stage=stage;ctx.progress('independent fixed-witness arithmetic')
   rel='validation/'+stage+'_arithmetic.py'
   code_hashes[rel]=hashlib.sha256((ROOT/rel).read_bytes()).hexdigest()
   module=importlib.import_module(stage+'_arithmetic')
   reports[stage]=module.verify(ctx);ctx.progress('completed')
  for rel,digest in code_hashes.items():
   ctx.require(hashlib.sha256((ROOT/rel).read_bytes()).hexdigest()==digest,'checker source stable during acceptance: '+rel)
  complete=args.stage=='all'
  answer=dict(status='PASS' if complete else 'PASS_PARTIAL',fixed_threshold=180,
   complete_arithmetic_acceptance=complete,checks=ctx.checks,checks_by_stage=ctx.by_stage,
   stages=reports,input_sha256=ctx.inputs,verifier_sha256=code_hashes,
   mathematical_searches_executed=False,optimization_executed=False,
   historical_modules_imported=False,files_written_or_extracted=False,
   scope='Fixed rational witness acceptance; analytic implications remain the manuscript proof',
   elapsed_seconds=round(time.monotonic()-ctx.started,2))
  if 'C3_WORST' in ctx.facts:answer['C3_worst']=ctx.facts['C3_WORST']
  print(json.dumps(answer,indent=2,default=encode));return 0
 except Exception as e:
  answer=dict(status='FAIL',error=type(e).__name__+': '+str(e),
    stage=ctx.stage if ctx else 'initialization',checks=ctx.checks if ctx else 0,
    complete_arithmetic_acceptance=False)
  print(json.dumps(answer,indent=2));return 1
 finally:
  if ctx is not None:ctx.zip.close()

if __name__=='__main__':raise SystemExit(main())
