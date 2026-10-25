"""Download official Apache-2.0 Vosk models and repack for vosk-browser."""
from pathlib import Path, PurePosixPath
from urllib.request import urlopen
import zipfile,tarfile,io,hashlib,json
ROOT=Path(__file__).resolve().parents[1]
out=ROOT/'public/models';out.mkdir(parents=True,exist_ok=True)
manifest={}
for lang,name in [('en','vosk-model-small-en-in-0.4'),('hi','vosk-model-small-hi-0.22')]:
 target=out/(lang+'.bin')
 if not target.exists():
  url='https://alphacephei.com/vosk/models/'+name+'.zip'
  print('Downloading',url,flush=True)
  with urlopen(url,timeout=120) as response: raw=response.read()
  with zipfile.ZipFile(io.BytesIO(raw)) as archive,tarfile.open(target,'w:gz',format=tarfile.USTAR_FORMAT) as tar:
   directories=set()
   for item in archive.infolist():
    if item.is_dir():continue
    parts=PurePosixPath(item.filename).parts
    if '..' in parts or len(parts)<2:raise ValueError('Invalid archive path')
    for n in range(1,len(parts)):
     directory='/'.join(('model',)+parts[1:n])
     if directory not in directories:
      entry=tarfile.TarInfo(directory);entry.type=tarfile.DIRTYPE;entry.mode=0o755;entry.mtime=1700000000
      tar.addfile(entry);directories.add(directory)
    data=archive.read(item);entry=tarfile.TarInfo('model/'+'/'.join(parts[1:]));entry.size=len(data);entry.mode=0o644;entry.mtime=1700000000
    tar.addfile(entry,io.BytesIO(data))
 manifest[lang]={'file':'/models/'+lang+'.bin','source':'https://alphacephei.com/vosk/models/'+name+'.zip','license':'Apache-2.0','bytes':target.stat().st_size,'sha256':hashlib.sha256(target.read_bytes()).hexdigest()}
 print(lang,manifest[lang]['bytes'],flush=True)
(out/'manifest.json').write_text(json.dumps(manifest,indent=2))
