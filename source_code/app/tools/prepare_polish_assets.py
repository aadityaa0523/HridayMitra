"""Generate draft UI translations and synthetic Hindi MP3 prompts from public copy only.
No patient content is read or sent. Review translations/recordings before clinical use.
Re-running reuses generated files. Network is needed only during authoring.
"""
from pathlib import Path
import concurrent.futures, hashlib, json, re, time, urllib.parse, urllib.request

ROOT=Path(__file__).resolve().parents[1]
LOCALES=ROOT/'src/i18n'
LANGS=['ta','te','kn','mr','bn','gu','ml','or']
def read(path): return json.loads(path.read_text(encoding='utf-8-sig'))
def write(path,value): path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def flatten(obj,prefix=''):
    return {k:v for key,value in obj.items() for k,v in (flatten(value,prefix+key+'.').items() if isinstance(value,dict) else [(prefix+key,value)])}
def unflatten(values):
    result={}
    for key,value in values.items():
        node=result;parts=key.split('.')
        for part in parts[:-1]:node=node.setdefault(part,{})
        node[parts[-1]]=value
    return result
def copy_key(text):
    n=2166136261
    for c in text:n=((n^ord(c))*16777619)&0xffffffff
    return 'c'+format(n,'x')
def request(url):
    for attempt in range(5):
        try:
            with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0'}),timeout=45) as response:return response.read()
        except Exception:
            if attempt==4:raise
            time.sleep(2+attempt*3)

def prepare_sources():
    en=read(LOCALES/'en.json');hi=read(LOCALES/'hi.json')
    en['phase']='Phase 9 · Demo polish';hi['phase']='चरण 9 · डेमो सुधार'
    en['polish']={'display':'Display and audio','theme':'Colour theme','light':'Light','dark':'Dark','contrast':'High contrast','large':'Larger text','elderContrast':'Elder mode always uses high contrast.','draft':'Machine translation · needs review. Voice recognition and reports support English/Hindi.','needsReview':'Needs review','audio':'Hindi offline audio','audioHelp':'48 synthetic Hindi clips are saved with the app. They are not human recordings and need listening review.','playAudio':'Play Hindi greeting','stopAudio':'Stop audio','audioUnavailable':'This exact message needs an installed local voice. Read the visible text or ask your caregiver.','languageFailed':'Could not switch language. Try again.','loading':'Loading this view…','reportLanguage':'Clinical PDF output is English/Hindi only.','voiceLanguages':'Voice recognition supports English and Hindi only.'}
    hi['polish']={'display':'दिखावट और आवाज़','theme':'रंग शैली','light':'हल्की','dark':'गहरी','contrast':'अधिक स्पष्ट','large':'बड़े अक्षर','elderContrast':'बुज़ुर्ग मोड में रंग हमेशा अधिक स्पष्ट रहते हैं।','draft':'मशीन अनुवाद · समीक्षा ज़रूरी। आवाज़ पहचान और रिपोर्ट हिंदी/अंग्रेज़ी में हैं।','needsReview':'समीक्षा ज़रूरी','audio':'हिंदी ऑफ़लाइन आवाज़','audioHelp':'ऐप में 48 कृत्रिम हिंदी आवाज़ क्लिप हैं। ये मानव रिकॉर्डिंग नहीं हैं; सुनकर समीक्षा ज़रूरी है।','playAudio':'हिंदी नमस्ते सुनें','stopAudio':'आवाज़ बंद करें','audioUnavailable':'इस पूरे संदेश के लिए फ़ोन की स्थानीय आवाज़ चाहिए। लिखे शब्द पढ़ें या परिवार की मदद लें।','languageFailed':'भाषा नहीं बदल सके। फिर कोशिश करें।','loading':'यह पृष्ठ खुल रहा है…','reportLanguage':'चिकित्सकीय PDF केवल हिंदी/अंग्रेज़ी में है।','voiceLanguages':'आवाज़ पहचान केवल हिंदी और अंग्रेज़ी में है।'}
    for lang,obj in [('en',en),('hi',hi)]:obj['_meta']={'status':'needs review','source':'authored demo' if lang=='en' else 'authored Hindi demo'}
    pattern=re.compile(r"tr\('((?:\\.|[^'\\])*)','((?:\\.|[^'\\])*)'\)")
    pairs={}
    for path in (ROOT/'src').rglob('*.tsx'):
        for english,hindi in pattern.findall(path.read_text(encoding='utf-8-sig')):
            english=english.replace("\\'","'");hindi=hindi.replace("\\'","'")
            key=copy_key(english)
            if key in pairs and pairs[key][0]!=english:raise ValueError('Copy key collision')
            pairs[key]=(english,hindi)
    en['extra']={k:p[0] for k,p in pairs.items()};hi['extra']={k:p[1] for k,p in pairs.items()}
    write(LOCALES/'en.json',en);write(LOCALES/'hi.json',hi)
    return en,hi

def translate(lang,source):
    flat=flatten(source);cache_path=ROOT/'tools/translation-cache'/f'{lang}.json';cache=read(cache_path) if cache_path.exists() else {};items=[(key,value) for key,value in flat.items() if key not in cache or cache[key].get('source')!=value]
    batches=[];batch=[];size=0
    for item in items:
        if size+len(item[1])>2600 and batch:batches.append(batch);batch=[];size=0
        batch.append(item);size+=len(item[1])+20
    if batch:batches.append(batch)
    for batch in batches:
        placeholders={}
        def protect(match):
            key=f'XVAR{len(placeholders):04d}';placeholders[key]=match.group();return key
        text='\n'.join(f'[K{i:04d}] '+re.sub(r'\{\{[^}]+\}\}',protect,value) for i,(_,value) in enumerate(batch))
        url='https://translate.googleapis.com/translate_a/single?'+urllib.parse.urlencode({'client':'gtx','sl':'en','tl':lang,'dt':'t','q':text})
        response=json.loads(request(url));translated=''.join(part[0] for part in response[0] if part[0]);parts=re.split(r'\[\s*K\s*(\d{4})\s*\]',translated)
        values={int(parts[i]):parts[i+1].strip() for i in range(1,len(parts),2)}
        if set(values)!=set(range(len(batch))):
            values={}
            for i,line in enumerate(text.split('\n')):
                single=line.split('] ',1)[1]
                url='https://translate.googleapis.com/translate_a/single?'+urllib.parse.urlencode({'client':'gtx','sl':'en','tl':lang,'dt':'t','q':single})
                response=json.loads(request(url));values[i]=''.join(part[0] for part in response[0] if part[0]).strip()
        for i,(key,value) in enumerate(batch):
            result=values[i]
            for token,original in placeholders.items():result=re.sub(token,lambda _:original,result,flags=re.I)
            if re.findall(r'\{\{[^}]+\}\}',value)!=re.findall(r'\{\{[^}]+\}\}',result):raise ValueError(f'{lang}: placeholder changed {key}')
            cache[key]={'source':value,'value':result}
        write(cache_path,cache)
    result=unflatten({key:cache[key]['value'] for key in flat});result['_meta']={'status':'needs review','source':'machine translation from English'};write(LOCALES/f'{lang}.json',result);print('Translated',lang,len(flat),'keys',flush=True)

def audio(hi):
    flat=flatten(hi)
    keys=['greeting','welcome','status.green','status.amber','status.red','status.learning','status.unknown','elder.q1','elder.q2','elder.reminder','elder.taken','elder.countdown','elder.helpReady','elder.unknown','elder.saved','elder.yes','elder.no','elder.unlock','elder.confirmTaken','elder.selectDose','elder.noWater','disclaimer','emergency','checkText','routineText','familyMode.scheduledReminder','familyMode.confirmDose','familyMode.doseTaken','familyMode.chooseDose']
    values=[(key,flat[key]) for key in keys]+[(f'number.{i}',word) for i,word in enumerate(['शून्य','एक','दो','तीन','चार','पाँच','छह','सात','आठ','नौ','दस'])]
    values += [('vault.historical',flat['vault.historical']),('checkin.start','जाँच शुरू करने के लिए उपकरण जोड़ें।'),('checkin.sit','आराम से बैठिए और स्थिर रहिए।'),('checkin.feet','दोनों नंगे पैर प्लेट पर रखिए।'),('checkin.handles','दोनों हैंडल पकड़िए।'),('checkin.finger','उँगली सेंसर पर रखिए और स्थिर रहिए।'),('checkin.stand','अब धीरे से खड़े होइए।'),('choose.hi','नमस्ते। हिंदी चुनें।')]
    assert len(values)==48
    out=ROOT/'public/audio/hi';out.mkdir(parents=True,exist_ok=True)
    def fetch(item):
        key,text=item;name=key.replace('.','-')+'.mp3';path=out/name
        if not path.exists():
            url='https://translate.google.com/translate_tts?'+urllib.parse.urlencode({'ie':'UTF-8','client':'tw-ob','tl':'hi','q':text})
            content=request(url)
            if len(content)<1000 or content.startswith(b'<'):raise ValueError('Invalid audio response')
            path.write_bytes(content)
        data=path.read_bytes();return {'key':key,'text':text,'url':'/audio/hi/'+name,'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest()}
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:clips=list(pool.map(fetch,values))
    write(ROOT/'src/voice/clips.hi.json',clips);write(out/'manifest.json',{'language':'hi','source':'pre-generated synthetic Google Hindi TTS','status':'needs listening review','clips':clips});print('Hindi audio',len(clips),sum(c['bytes'] for c in clips),'bytes',flush=True)

if __name__=='__main__':
    en,hi=prepare_sources()
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
        futures=[pool.submit(translate,lang,en) for lang in LANGS]+[pool.submit(audio,hi)]
        for future in concurrent.futures.as_completed(futures):future.result()

