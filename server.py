"""Local companion for Remember LARA. Requires Ollama and a locally available model.
Start: python server.py. Model name via LARA_MODEL environment variable.
No cloud API key is required, but model installation is a separate user step.
"""
import json, os, urllib.request, urllib.error, urllib.parse, time, threading, math
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from pathlib import Path

MODEL=os.environ.get('LARA_MODEL','qwen3:1.7b')
OLLAMA=os.environ.get('OLLAMA_HOST','http://127.0.0.1:11434').rstrip('/')
ROOT=Path(__file__).parent/'app/src/main/assets'
# City-center coordinates are only approximations, not precise user locations.
CITIES={
 '서울':(126.9780,37.5665),'부산':(129.0756,35.1796),'인천':(126.7052,37.4563),
 '수원':(127.0286,37.2636),'대전':(127.3845,36.3504),'대구':(128.6014,35.8714),
 '광주':(126.8514,35.1595),'울산':(129.3114,35.5384),'세종':(127.2890,36.4801),
 '춘천':(127.7298,37.8813),'강릉':(128.8761,37.7519),'전주':(127.1480,35.8242),
 '청주':(127.4890,36.6424),'천안':(127.1522,36.8151),'포항':(129.3435,36.0190),
 '창원':(128.6811,35.2279),'성남':(127.1378,37.4200),'용인':(127.1775,37.2411),
 '제주':(126.5312,33.4996),'안양':(126.9568,37.3943),'안산':(126.8309,37.3219),
 '김해':(128.8894,35.2285),'김포':(126.7156,37.6153),'평택':(127.1127,36.9921)
}
ROUTE_CACHE={}
ROUTE_LOCK=threading.Lock()
LAST_ROUTE_CALL=[0.0]
def calculate_route(start, end):
    if start not in CITIES or end not in CITIES:
        return {'ok':False,'error':'지원하지 않는 도시입니다. 지원 도시: '+', '.join(CITIES)}
    if start==end:
        return {'ok':False,'error':'같은 도시 안의 상세 출발지·도착지는 아직 조회할 수 없습니다.'}
    key=(start,end)
    if key in ROUTE_CACHE and time.time()-ROUTE_CACHE[key]['at'] < 43200:
        return ROUTE_CACHE[key]['result']
    a=CITIES[start];b=CITIES[end]
    url=('https://routing.openstreetmap.de/routed-car/route/v1/driving/'
         +f'{a[0]},{a[1]};{b[0]},{b[1]}?overview=full&geometries=geojson&steps=false')
    # Volunteer-hosted demo routing: cap total request frequency at <=1/s.
    with ROUTE_LOCK:
        wait=max(0,1.1-(time.monotonic()-LAST_ROUTE_CALL[0]))
        if wait:time.sleep(wait)
        LAST_ROUTE_CALL[0]=time.monotonic()
        req=urllib.request.Request(url,headers={'User-Agent':'Remember-LARA-Contest-Prototype/0.2 (student demonstration; OpenStreetMap attribution)'})
        with urllib.request.urlopen(req,timeout=16) as resp: data=json.load(resp)
    routes=data.get('routes') or []
    if data.get('code')!='Ok' or not routes:raise ValueError('온라인 도로 경로 결과 없음')
    r=routes[0]
    result={'ok':True,'origin':start,'destination':end,'km':round(r['distance']/1000,1),
            'minutes':round(r['duration']/60), 'source':'OpenStreetMap / OSRM',
            'note':'도시 중심 기준 대략적 경로이며 실시간 교통·출발 위치를 반영하지 않습니다.'}
    ROUTE_CACHE[key]={'at':time.time(),'result':result,'coordinates':r.get('geometry',{}).get('coordinates',[])}
    return result



# Public OSM data is best-effort, not live opening-hours or charger-availability data.
STATION_CACHE={}
def nearby_stations(origin, destination, kind, available_km):
    if kind not in ('fuel','charging_station'):
        return {'ok':False,'error':'지원하지 않는 시설 유형입니다.'}
    if origin not in CITIES or destination not in CITIES:
        return {'ok':False,'error':'출발지/목적지 도시를 먼저 설정해 주세요.'}
    route=calculate_route(origin,destination)
    if not route['ok']:return route
    coords=ROUTE_CACHE[(origin,destination)].get('coordinates') or []
    if len(coords)<2:return {'ok':False,'error':'경로 좌표를 확인할 수 없습니다.'}
    # Only sample the route within a conservative portion of the remaining
    # *simulated* range. Real road distances to POIs are checked separately.
    limit=max(0,min(float(available_km)*0.75,route['km']*0.9,230))
    if limit<10:return {'ok':False,'error':'예상 주행가능거리가 부족합니다. 가까운 안전한 장소를 확인해 주세요.'}
    cumulative=[0.0]
    for a,b in zip(coords,coords[1:]):
        la,lb=math.radians(a[1]),math.radians(b[1]);dlat=lb-la;dlon=math.radians(b[0]-a[0]);h=math.sin(dlat/2)**2+math.cos(la)*math.cos(lb)*math.sin(dlon/2)**2
        cumulative.append(cumulative[-1]+6371*2*math.asin(min(1,math.sqrt(h))))
    route_len=cumulative[-1]
    # Use <= 5 sample points, 4km radii. This is a demonstration search and
    # does not guarantee all stations along the route are discovered.
    samples=[]
    for target in [min(limit*frac,route_len-0.1) for frac in (.12,.28,.48,.67,.85)]:
        ix=next((i for i,d in enumerate(cumulative) if d>=target),len(coords)-1)
        samples.append(coords[ix])
    query='[out:json][timeout:20];(' + ''.join(
        f'node(around:4000,{lat:.6f},{lon:.6f})["amenity"="{kind}"];way(around:4000,{lat:.6f},{lon:.6f})["amenity"="{kind}"];'
        for lon,lat in samples) + ');out center 35;'
    key=(origin,destination,kind,round(float(available_km)/20))
    cached=STATION_CACHE.get(key)
    if cached and time.time()-cached['time']<1200:return cached['result']
    http=urllib.request.Request('https://overpass.kumi.systems/api/interpreter',data=query.encode('utf-8'),headers={'User-Agent':'RememberLARA-student-demo/0.3','Content-Type':'text/plain'})
    with urllib.request.urlopen(http,timeout=28) as response:payload=json.load(response)
    rows=[];seen=set()
    for element in payload.get('elements',[]):
        tags=element.get('tags') or {}
        center=element.get('center') or element
        lon,lat=center.get('lon'),center.get('lat')
        if lon is None or lat is None:continue
        uid=str(element['type'])+str(element['id'])
        if uid in seen:continue
        seen.add(uid)
        rows.append({'id':uid,'name':tags.get('name') or ('전기차 충전소' if kind=='charging_station' else '주유소'), 'lon':lon,'lat':lat,'operator':tags.get('operator',''), 'address':(tags.get('addr:street') or ''), 'verifiedOpen':False})
    # Select candidates by rough geographic closeness to points; true detour
    # and reachability are NOT implied by this shortlist.
    def distance_to_path(r):
        return min(6371*2*math.asin(min(1,math.sqrt(math.sin(math.radians(r['lat']-lat)/2)**2+math.cos(math.radians(lat))*math.cos(math.radians(r['lat']))*math.sin(math.radians(r['lon']-lon)/2)**2))) for lon,lat in samples)
    rows.sort(key=distance_to_path)
    result={'ok':True,'source':'OpenStreetMap/Overpass','stations':rows[:8], 'warning':'실시간 영업 여부, 충전기 빈자리, 실제 접근 가능 여부는 확인되지 않았습니다. 경유 전 지도에서 확인하세요.'}
    STATION_CACHE[key]={'time':time.time(),'result':result}
    return result

class Handler(BaseHTTPRequestHandler):
    def _send(self, code, data, kind='application/json'):
        payload=data if isinstance(data,bytes) else json.dumps(data,ensure_ascii=False).encode()
        self.send_response(code); self.send_header('Content-Type',kind+'; charset=utf-8');self.send_header('Access-Control-Allow-Origin','http://127.0.0.1:8765');self.send_header('Access-Control-Allow-Methods','GET, POST, OPTIONS');self.send_header('Access-Control-Allow-Headers','Content-Type');self.send_header('Content-Length',str(len(payload)));self.end_headers();self.wfile.write(payload)
    def do_OPTIONS(self):self._send(200,{})
    def do_GET(self):
        if self.path in ('/','/index.html'):return self._send(200,(ROOT/'index.html').read_bytes(),'text/html')
        if self.path.startswith('/stations?'):
            try:
                q=urllib.parse.parse_qs(urllib.parse.urlsplit(self.path).query)
                pick=lambda name,default='':q.get(name,[default])[0].strip()
                result=nearby_stations(pick('origin'),pick('destination'),pick('kind','fuel'),float(pick('range','0')))
                return self._send(200 if result.get('ok') else 422,result)
            except Exception as exc:
                print('LARA stations error:',repr(exc),flush=True)
                return self._send(503,{'ok':False,'error':'주유소·충전소 조회에 실패했어요. 실제 경유지로 설정하지 않았습니다.'})
        if self.path.startswith('/route?'):
            try:
                p=urllib.parse.parse_qs(urllib.parse.urlsplit(self.path).query)
                start=p.get('origin',[''])[0].strip();end=p.get('destination',[''])[0].strip()
                result=calculate_route(start,end)
                return self._send(200 if result['ok'] else 422,result)
            except Exception as exc:
                print('LARA route error:',repr(exc),flush=True)
                return self._send(503,{'ok':False,'error':'현재 온라인 도로 조회가 불가능합니다. 임의 거리로 답하지 않습니다.'})
        if self.path=='/health':
            try:
                with urllib.request.urlopen(OLLAMA+'/api/tags',timeout=3) as r: tags=json.load(r)
                ready=any(m.get('name','').split(':')[0]==MODEL.split(':')[0] for m in tags.get('models',[]))
                return self._send(200,{'ready':ready,'model':MODEL,'available':[m.get('name') for m in tags.get('models',[])]})
            except Exception as exc:return self._send(503,{'ready':False,'error':str(exc)})
        self._send(404,{'error':'not found'})
    def do_POST(self):
        if self.path!='/chat':return self._send(404,{'error':'not found'})
        try:
            n=int(self.headers.get('Content-Length','0'))
            if not 0<n<=100_000:return self._send(413,{'error':'payload too large'})
            data=json.loads(self.rfile.read(n));passenger=bool(data.get('passenger'));mem=[] if passenger else [str(x)[:350] for x in data.get('memories',[])[:30]]
            prompt=('너는 차량용 AI 동승자 라라(LARA)다. 한국어로 자연스럽고 짧게 공감한다. 존댓말을 사용한다. 사용자의 구체적 질문에 직접 답한다. 똑같은 안내문을 반복하지 않는다. 연애 감정이나 사랑 고백을 하지 않고, 사람이거나 실제 동승자라고 주장하지 않는다. 질문이 불명확하면 짧게 확인한다. '
              '모르는 사건을 지어내지 않는다. 개인 기억은 반드시 승인된 정보만 활용한다. '
              '운전자의 주의를 빼앗는 긴 대화는 피한다. 내비게이션/차량 상태는 시뮬레이션이므로 실제라고 주장하지 않는다. '
              '위험한 운전 조작을 제안하지 않는다. 정서적 대화에서 상담 전문가인 척하지 않는다. '
              '대화로 새 기억을 자동 저장했다고 말하지 않는다. 화면 승인 후 저장만 가능하다. '
              f'대화 성향: {str(data.get("style","listen"))[:20]}. 동승자 모드: {passenger}. '
              f'운전자 승인 기억(동승자 모드일 경우 없음): {json.dumps(mem,ensure_ascii=False)}. '
              f'차량 모의 정보: 주행가능거리 {str(data.get("range",160))[:10]}km, 목적지 {str(data.get("destination","집"))[:80]}.')
            history=[]
            for h in data.get('history',[])[-16:]:
                if h.get('role') in ('user','assistant'):history.append({'role':h['role'],'content':str(h.get('content',''))[:1200]})
            req=json.dumps({'model':MODEL,'messages':[{'role':'system','content':prompt}]+history,'stream':False,'think':False,'options':{'num_predict':380,'temperature':0.6}},ensure_ascii=False).encode()
            http=urllib.request.Request(OLLAMA+'/api/chat',data=req,headers={'Content-Type':'application/json'})
            with urllib.request.urlopen(http,timeout=240) as r:resp=json.load(r)
            result=str(resp.get('message',{}).get('content','')).strip()
            # Models that emit an internal reasoning block must not read it aloud.
            import re
            result=re.sub(r'<think>.*?</think>', '', result, flags=re.S).strip()
            if not result:return self._send(502,{'error':'모델이 빈 답변을 반환했습니다. 추론 모드 또는 출력 설정을 확인하세요.'})
            self._send(200,{'reply':result})
        except Exception as e:
            print('LARA chat error:',repr(e),flush=True)
            self._send(502,{'error':str(e)})

if __name__=='__main__':
    bind='0.0.0.0' if os.environ.get('LARA_LAN')=='1' else '127.0.0.1'
    print(f'LARA running on {bind}:8765 / Ollama model: {MODEL}',flush=True)
    if bind=='0.0.0.0':print('WARNING: local network access enabled. Use trusted private Wi-Fi only; do not forward the port.',flush=True)
    ThreadingHTTPServer((bind,8765),Handler).serve_forever()
