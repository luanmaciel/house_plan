import json, os
here = os.path.dirname(os.path.abspath(__file__))
GEO = os.environ.get("HOUSE_PLAN_GEO", os.path.join(os.path.dirname(here), "inputs", "geo.json"))  # formato no README
geo = json.load(open(GEO, encoding="utf-8"))
rm = geo["rooms"]
# sala em L: o geo.json traz "sala_top", "sala_bot" e "hall" como retângulos separados (ver README)
W, H = geo["W"], geo["H"]
PX = 100

def A(room, dx, dy): return round(rm[room][0] + dx, 3), round(rm[room][1] + dy, 3)
ITEMS = []   # mesma lista, em dicts, para tools/plantas.py
def item(id_, label, room, allow, dx, dy, w, h, c, op, extra=""):
    x, y = A(room, dx, dy)
    ITEMS.append(dict(id=id_, label=label, room=room, x=x, y=y, w=w, h=h, c=c, op=op,
                      fixed="fixed" in extra, dash="dash" in extra, night="night" in extra))
    return f' {{id:"{id_}",label:"{label}",room:"{room}",allow:{json.dumps(allow)},x:{x},y:{y},w:{w},h:{h},c:"{c}",op:{op}{extra}}}'

items = [
 item("box","box 1,66x0,90","banho",["banho"],0,0.81,1.66,0.9,"sage",.25),
 item("chuveiro","chuveiro","banho",["banho"],0.15,0.96,0.3,0.3,"wood",.3),
 item("banco","banco","banho",["banho"],0,1.28,0.3,0.4,"wood",.3),
 item("pia","pia 0,60x0,45","banho",["banho"],0,0.13,0.45,0.6,"muted",.15),
 item("vaso","vaso 0,38x0,68","nicho",["nicho","banho"],0.15,0.05,0.4,0.75,"red",.15),
 item("armario","armario existente","q1alc",["q1alc"],0,0,0.86,1.87,"wood",.3,",fixed:true"),
 item("cama","queen 1,58x1,98","q1",["q1"],1.03,0,1.58,1.98,"bed",.5),
 item("criado1","criado","q1",["q1"],0.58,0,0.4,0.4,"muted",.15),
 item("criado2","criado","q1",["q1"],2.66,0,0.4,0.4,"muted",.15),
 item("armexist","armario existente (correr)","q2",["q2"],0,0.88,0.50,1.90,"wood",.3,",fixed:true"),
 item("bicama","bicama 1,88x0,88","q2",["q2"],1.15,1.9,1.88,0.88,"bed",.5),
 item("aux","auxiliar puxada","q2",["q2"],1.15,1,1.8,0.88,"bed",.25,",dash:true,night:true"),
 item("mesa","mesa 1,00x0,50","q2",["q2"],2.63,0,1,0.5,"wood",.3),
 item("cadeira","cadeira","q2",["q2"],2.99,0.5,0.45,0.45,"muted",.1,",dash:true"),
 item("sofa","sofa 2,10x0,90","sala_bot",["sala_bot","sala_top"],0,1.26,0.9,2.1,"bed",.5),
 item("rack","rack/TV 1,80x0,40","sala_bot",["sala_bot","sala_top"],2.33,1.36,0.4,1.8,"wood",.3),
 item("jantar","mesa jantar 6 lug. 1,60x0,90","sala_top",["sala_top","sala_bot"],1.08,0.5,1.6,0.9,"wood",.3),
 item("cadj1","cad.","sala_top",["sala_top","sala_bot"],1.3,0.05,0.45,0.45,"muted",.1,",dash:true"),
 item("cadj2","cad.","sala_top",["sala_top","sala_bot"],2.1,0.05,0.45,0.45,"muted",.1,",dash:true"),
 item("cadj3","cad.","sala_top",["sala_top","sala_bot"],1.3,1.4,0.45,0.45,"muted",.1,",dash:true"),
 item("cadj4","cad.","sala_top",["sala_top","sala_bot"],2.1,1.4,0.45,0.45,"muted",.1,",dash:true"),
 item("cadj5","cad.","sala_top",["sala_top","sala_bot"],0.63,0.73,0.45,0.45,"muted",.1,",dash:true"),
 item("cadj6","cad.","sala_top",["sala_top","sala_bot"],2.68,0.73,0.45,0.45,"muted",.1,",dash:true"),
 item("bancada","bancada existente 0,60","cozinha",["cozinha"],1.76,0.392,0.6,3.2,"wood",.25,",fixed:true"),
 item("piac","pia","cozinha",["cozinha"],1.76,2.242,0.6,0.55,"muted",.15,",dash:true,fixed:true"),
 item("fogao","fogao + exaustor","cozinha",["cozinha"],1.76,0.942,0.6,0.55,"muted",.15,",dash:true,fixed:true"),
 item("gelad","geladeira 0,70","cozinha",["cozinha"],0.0,0.9,0.7,0.7,"muted",.2),
 item("cafe","mesa de cafe 0,80x0,50","cozinha",["cozinha"],-0.0,1.8,0.5,0.8,"wood",.3),
 item("cadcafe","cad.","cozinha",["cozinha"],0.55,1.95,0.45,0.45,"muted",.1,",dash:true"),
 item("tanque","tanque","lavanderia",["lavanderia"],1.76,1.5,0.6,0.55,"muted",.2),
 item("maquina","lavadora + secadora (torre) 0,60","lavanderia",["lavanderia"],1.76,0.9,0.6,0.6,"muted",.2),
 item("vasolv","vaso","lavabo",["lavabo"],0.15,0.05,0.4,0.68,"red",.15),
 item("pialv","pia","lavabo",["lavabo"],0.73,0.01,0.5,0.4,"muted",.15),
 item("mesaesc","mesa 1,00x0,45","escritorio",["escritorio"],0,0.02,0.45,1,"wood",.3),
 item("camaesc","solteiro 0,88x1,88","escritorio",["escritorio"],0,1.09,0.88,1.88,"bed",.5),
 item("mesav","mesinha","varanda",["varanda"],1.05,0.25,0.6,0.6,"wood",.3),
]

labels = dict(banho="BANHEIRO", q1="QUARTO 1", q2="QUARTO 2", sala_top="SALA", cozinha="COZINHA", lavanderia="LAVANDERIA",
              lavabo="LAVABO", escritorio="QUARTO/ESCRIT.", varanda="VARANDA", entrada="ENTRADA")

html = r'''<meta charset="utf-8"><title>Prancheta de layout</title>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Archivo:wght@700;800&family=Atkinson+Hyperlegible:wght@400;700&family=IBM+Plex+Mono:wght@400;600&display=swap">
<style>
  :root{--bg:#F6F3EC;--surface:#fff;--ink:#2C2620;--muted:#6E6355;--line:#DDD5C7;--wood:#A06B3F;--sage:#5F7355;--red:#B93A2B;--warn:#A8742C;--ok:#4E7A52}
  @media (prefers-color-scheme: dark){:root:not([data-theme="light"]){--bg:#211D17;--surface:#2B2620;--ink:#EFE8DC;--muted:#AA9D8B;--line:#423A2F;--wood:#C99A66;--sage:#9AAE8B;--red:#E07A63;--warn:#D2A257;--ok:#8FB98F}}
  :root[data-theme="dark"]{--bg:#211D17;--surface:#2B2620;--ink:#EFE8DC;--muted:#AA9D8B;--line:#423A2F;--wood:#C99A66;--sage:#9AAE8B;--red:#E07A63;--warn:#D2A257;--ok:#8FB98F}
  *{box-sizing:border-box} body{margin:0;background:var(--bg);color:var(--ink);font-family:"Atkinson Hyperlegible",system-ui,sans-serif;font-size:16px;line-height:1.5;padding:0 16px 64px}
  .wrap{max-width:1400px;margin:0 auto} header{padding:32px 0 10px}
  .eyebrow{font-family:"IBM Plex Mono",monospace;font-size:.72rem;letter-spacing:.14em;text-transform:uppercase;color:var(--wood);margin:0 0 6px}
  h1{font-family:Archivo,sans-serif;font-size:2rem;margin:0 0 6px} h2{font-family:Archivo,sans-serif;font-size:1rem;margin:18px 0 6px}
  .grid{display:grid;grid-template-columns:minmax(0,1fr) 300px;gap:18px} @media(max-width:900px){.grid{grid-template-columns:1fr}}
  .board{background:#fff;border:1px solid var(--line);border-radius:12px;padding:8px;touch-action:none;user-select:none;overflow:auto}
  svg{display:block;height:auto}
  .panel{background:var(--surface);border:1px solid var(--line);border-radius:12px;padding:16px;font-size:.93rem}
  button{font:inherit;font-size:.88rem;padding:7px 12px;border-radius:8px;border:1px solid var(--line);background:var(--bg);color:var(--ink);cursor:pointer;margin:0 6px 6px 0}
  button:focus-visible{outline:3px solid var(--wood);outline-offset:2px}
  label{display:block;margin:6px 0;font-size:.88rem} input[type=range]{width:160px;vertical-align:middle}
  ul{list-style:none;padding:0;margin:0} li{padding:5px 0;border-bottom:1px solid var(--line);font-size:.86rem} li b{font-family:"IBM Plex Mono",monospace;font-weight:600}
  .ok b{color:var(--ok)} .bad b{color:var(--red)} .info b{color:var(--muted)}
  textarea{width:100%;height:150px;font-family:"IBM Plex Mono",monospace;font-size:.72rem;border:1px solid var(--line);border-radius:8px;background:var(--bg);color:var(--ink);padding:8px}
  .hint{color:var(--muted);font-size:.85rem}
</style>
<div class="wrap">
<header>
  <p class="eyebrow">Apartamento inteiro · planta medida no local</p>
  <h1>Prancheta de layout</h1>
  <p class="hint">Arraste os móveis (no celular, com o dedo). Toque num móvel e use "Girar". Cada móvel fica preso no seu cômodo; bancada da cozinha e armários existentes são fixos. Leques = raio das portas de abrir (nada pode ficar ali); tracejado verde = portas de correr (cozinha e varanda). Use o zoom para trabalhar num cômodo de perto. Quando gostar do resultado, "Copiar layout" e valide o texto no simulador.</p>
</header>
<div class="grid">
  <div class="board"><svg id="svg" viewBox="0 0 __VW__ __VH__" role="img" aria-label="Planta do apartamento com móveis arrastáveis"></svg></div>
  <aside class="panel">
    <label>Zoom <input type="range" id="zoom" min="50" max="160" value="80"></label>
    <button id="rot">Girar 90°</button><button id="reset">Voltar ao layout validado</button>
    <label><input type="checkbox" id="aux" checked> mostrar cama auxiliar puxada (só à noite)</label>
    <div id="sel" class="hint">Nenhum móvel selecionado.</div>
    <h2>Checagens</h2><ul id="checks"></ul>
    <h2>Layout em metros</h2>
    <button id="copy">Copiar layout</button><span id="copied" class="hint"></span>
    <textarea id="out" readonly></textarea>
    <p class="hint">Coordenadas relativas ao canto superior esquerdo interno de cada cômodo: [x, y, largura, altura].</p>
  </aside>
</div>
</div>
<script>
const G=__GEO__, PX=__PX__, SNAP=0.05, LABELS=__LABELS__, VW=__VW__;
const COL={wood:"#A06B3F",sage:"#5F7355",red:"#B93A2B",muted:"#6E6355",bed:"#8a8275"};
const R=G.rooms;
const BASE=[
__ITEMS__
];
let items, sel=null, showAux=true;
const clone=a=>JSON.parse(JSON.stringify(a));
function load(){ try{const s=localStorage.getItem("prancheta-v10"); if(s){items=JSON.parse(s); if(items.length===BASE.length) return;}}catch(e){} items=clone(BASE); }
function save(){ try{localStorage.setItem("prancheta-v10",JSON.stringify(items));}catch(e){} }
const svg=document.getElementById("svg");
const px=v=>(v*PX).toFixed(1);
function inRect(it,r){return it.x>=r[0]-1e-6&&it.y>=r[1]-1e-6&&it.x+it.w<=r[0]+r[2]+1e-6&&it.y+it.h<=r[1]+r[3]+1e-6;}
function clampTo(it,x,y){ let best=null;
  for(const k of it.allow){const r=R[k]; if(it.w>r[2]+1e-6||it.h>r[3]+1e-6) continue;
    const cx=Math.min(Math.max(x,r[0]),r[0]+r[2]-it.w), cy=Math.min(Math.max(y,r[1]),r[1]+r[3]-it.h);
    const d=Math.hypot(cx-x,cy-y); if(!best||d<best.d) best={x:cx,y:cy,d};}
  return best||{x:it.x,y:it.y}; }
function overlap(a,b){return a.x<b.x+b.w&&a.x+a.w>b.x&&a.y<b.y+b.h&&a.y+a.h>b.y;}
function inSwing(it,d){ const bx0=Math.min(d.hx,d.hx+d.sx*d.r),bx1=Math.max(d.hx,d.hx+d.sx*d.r),by0=Math.min(d.hy,d.hy+d.sy*d.r),by1=Math.max(d.hy,d.hy+d.sy*d.r);
  if(!(it.x<bx1&&it.x+it.w>bx0&&it.y<by1&&it.y+it.h>by0)) return false;
  const cx=Math.min(Math.max(d.hx,it.x),it.x+it.w), cy=Math.min(Math.max(d.hy,it.y),it.y+it.h); return Math.hypot(cx-d.hx,cy-d.hy)<d.r; }
const byId=id=>items.find(i=>i.id===id);
const active=it=>!(it.night&&!showAux);
const grp=it=>it.room.startsWith("sala")?"sala":(it.room==="nicho"?"banho":(it.room==="q1alc"?"q1":it.room));
function checks(){ const out=[]; const add=(ok,t,v,kind)=>out.push({ok,t:t+(v!==undefined?": "+v.toFixed(2)+" m":""),kind});
  for(const it of items){ if(!active(it)||it.fixed) continue; for(const d of G.doors){ if(d.room!==grp(it)) continue; if(inSwing(it,d)) add(false,it.label+" esta na varredura da porta"); } }
  const solid=items.filter(i=>active(i)&&!i.dash&&!i.fixed);
  for(let i=0;i<solid.length;i++)for(let j=i+1;j<solid.length;j++){const a=solid[i],b=solid[j]; if((a.id==="box"||b.id==="box")&&["chuveiro","banco"].includes(a.id==="box"?b.id:a.id)) continue; if((a.id==="bancada"||b.id==="bancada")&&["fogao"].includes(a.id==="bancada"?b.id:a.id)) continue; if(overlap(a,b)) add(false,a.label+" sobrepoe "+b.label);}
  const box=byId("box"),pia=byId("pia"),vaso=byId("vaso"),ch=byId("chuveiro"),ba=byId("banco");
  add(box.y-R.banho[1]>=0.60,"banheiro: corredor entre box e parede do hall",box.y-R.banho[1]);
  add((R.banho[0]+R.banho[2])-(pia.x+pia.w)>=0.80,"banheiro: frente da pia",(R.banho[0]+R.banho[2])-(pia.x+pia.w));
  add(inRect(vaso,R.nicho),"banheiro: vaso dentro do nicho");
  const bx=[box.x,box.y,box.w,box.h]; add(inRect(ch,bx)&&inRect(ba,bx),"banheiro: chuveiro e banco dentro do box");
  const arm=byId("armario"),cama=byId("cama");
  add(cama.x-(arm.x+arm.w)>=0.65,"quarto 1: frente do armario ate a cama (correr, min 0,65)",cama.x-(arm.x+arm.w));
  add((R.q1[0]+R.q1[2])-(cama.x+cama.w)>=0.60,"quarto 1: passagem lado da janela",(R.q1[0]+R.q1[2])-(cama.x+cama.w));
  add((R.q1[1]+R.q1[3])-(cama.y+cama.h)>=0.60,"quarto 1: pe da cama",(R.q1[1]+R.q1[3])-(cama.y+cama.h));
  const ae=byId("armexist"); let front=9; for(const it of items){ if(it.room!=="q2"||it.id==="armexist"||it.id==="aux"||!active(it)) continue; if(it.y<ae.y+ae.h&&it.y+it.h>ae.y&&it.x>=ae.x+ae.w-1e-6) front=Math.min(front,it.x-(ae.x+ae.w)); }
  add(front>=0.65,"quarto 2: frente do armario existente (correr, min 0,65)",front);
  const mesa=byId("mesa"); let free=(R.q2[1]+R.q2[3])-(mesa.y+mesa.h); for(const it of items){ if(it.room!=="q2"||["mesa","cadeira","aux","armexist"].includes(it.id)||!active(it)) continue; if(it.x<mesa.x+mesa.w&&it.x+it.w>mesa.x&&it.y>=mesa.y+mesa.h) free=Math.min(free,it.y-(mesa.y+mesa.h)); }
  add(free>=0.75,"quarto 2: espaco da cadeira a frente da mesa (min 0,75)",free);
  const aux=byId("aux"); if(showAux&&overlap(aux,byId("cadeira"))) add(true,"quarto 2: a noite a cadeira sobe para a mesa (auxiliar puxada)",undefined,"info");
  const sofa=byId("sofa"),rack=byId("rack"); const gs=Math.max(rack.x-(sofa.x+sofa.w),sofa.x-(rack.x+rack.w),rack.y-(sofa.y+sofa.h),sofa.y-(rack.y+rack.h));
  add(gs>=0.80,"sala: passagem entre sofa e rack (min 0,80)",gs);
  const jt=byId("jantar"); const gj=Math.min(jt.x-R.sala_top[0],(R.sala_top[0]+R.sala_top[2])-(jt.x+jt.w)); add(gj>=0.75,"sala: folga nas cabeceiras da mesa de 6 lugares (min 0,75)",gj);
  const bc=byId("bancada"); let gc=R.cozinha[2]-bc.w; for(const it of items){ if(it.room!=="cozinha"||["bancada","piac","fogao","cadcafe"].includes(it.id)) continue; gc=Math.min(gc,Math.max(it.x-(bc.x+bc.w),bc.x-(it.x+it.w))); }
  add(gc>=0.90,"cozinha: corredor entre a bancada e geladeira/mesa de cafe (min 0,90)",gc);
  const me=byId("mesaesc"),ce=byId("camaesc"); const ge=Math.max(ce.x-(me.x+me.w),me.x-(ce.x+ce.w),ce.y-(me.y+me.h),me.y-(ce.y+ce.h)); const lado=R.escritorio[0]+R.escritorio[2]-Math.max(me.x+me.w,ce.x+ce.w); add(Math.max(ge,lado)>=0.60,"escritorio: passagem livre (entre ou ao lado de mesa e cama, min 0,60)",Math.max(ge,lado));
  return out; }
function render(){ let s='<rect width="100%" height="100%" fill="#fff"/>';
  for(const d of G.doors){const a=[d.hx+d.sx*d.r,d.hy],b=[d.hx,d.hy+d.sy*d.r]; const sw=d.sx*d.sy>0?1:0;
    s+='<path d="M'+px(d.hx)+','+px(d.hy)+' L'+px(a[0])+','+px(a[1])+' A'+px(d.r)+','+px(d.r)+' 0 0 '+sw+' '+px(b[0])+','+px(b[1])+' Z" fill="#A8742C" fill-opacity=".12" stroke="#A8742C" stroke-dasharray="4 3"/>';}
  for(const sl of (G.sliders||[])) s+='<line x1="'+px(sl[0])+'" y1="'+px(sl[1])+'" x2="'+px(sl[2])+'" y2="'+px(sl[3])+'" stroke="#5F7355" stroke-width="3" stroke-dasharray="8 4"/>';
  for(const l of G.lines) s+='<line x1="'+px(l[0])+'" y1="'+px(l[1])+'" x2="'+px(l[2])+'" y2="'+px(l[3])+'" stroke="#1c1a17" stroke-width="1.6"/>';
  for(const k in LABELS){const r=R[k]; if(!r) continue; s+='<text x="'+px(r[0]+0.08)+'" y="'+px(r[1]+r[3]-0.08)+'" font-family="IBM Plex Mono,monospace" font-size="11" fill="#6E6355">'+LABELS[k]+'</text>';}
  for(const it of items){ if(!active(it)) continue; const c=COL[it.c]; const dash=it.dash?' stroke-dasharray="5 4"':''; const st=it===sel?' stroke-width="3"':' stroke-width="1.8"';
    s+='<g class="item" data-id="'+it.id+'" style="cursor:'+(it.fixed?'default':'grab')+'"><rect x="'+px(it.x)+'" y="'+px(it.y)+'" width="'+px(it.w)+'" height="'+px(it.h)+'" fill="'+c+'" fill-opacity="'+it.op+'" stroke="'+c+'"'+st+dash+'/>';
    const vert=it.h>it.w*1.6, tx=px(it.x+0.05), ty=px(it.y+0.16);
    s+=vert?'<text x="'+tx+'" y="'+ty+'" font-family="IBM Plex Mono,monospace" font-size="9" fill="'+c+'" transform="rotate(90 '+tx+' '+ty+')">'+it.label+'</text>':'<text x="'+tx+'" y="'+ty+'" font-family="IBM Plex Mono,monospace" font-size="9" fill="'+c+'">'+it.label+'</text>';
    s+='</g>'; }
  svg.innerHTML=s;
  document.getElementById("checks").innerHTML=checks().map(c=>'<li class="'+(c.kind||(c.ok?'ok':'bad'))+'"><b>'+(c.kind?'i':(c.ok?'OK':'!!'))+'</b> '+c.t+'</li>').join("");
  const o={}; for(const it of items){ if(it.fixed) continue; const r=R[it.room]; o[it.id]=[+(it.x-r[0]).toFixed(2),+(it.y-r[1]).toFixed(2),+it.w.toFixed(2),+it.h.toFixed(2)]; }
  document.getElementById("out").value=JSON.stringify(o);
  document.getElementById("sel").textContent=sel?("Selecionado: "+sel.label):"Nenhum movel selecionado."; save(); }
let drag=null;
function pt(e){const p=svg.createSVGPoint(); p.x=e.clientX; p.y=e.clientY; const q=p.matrixTransform(svg.getScreenCTM().inverse()); return [q.x/PX,q.y/PX];}
svg.addEventListener("pointerdown",e=>{ const g=e.target.closest(".item"); if(!g) return; const it=byId(g.dataset.id); if(it.fixed) return; sel=it; const [x,y]=pt(e); drag={it,dx:x-it.x,dy:y-it.y}; svg.setPointerCapture(e.pointerId); render(); });
svg.addEventListener("pointermove",e=>{ if(!drag) return; const [x,y]=pt(e); const nx=Math.round((x-drag.dx)/SNAP)*SNAP, ny=Math.round((y-drag.dy)/SNAP)*SNAP; const c=clampTo(drag.it,nx,ny); drag.it.x=+c.x.toFixed(3); drag.it.y=+c.y.toFixed(3); render(); });
svg.addEventListener("pointerup",()=>{drag=null;}); svg.addEventListener("pointercancel",()=>{drag=null;});
document.getElementById("rot").onclick=()=>{ if(!sel||sel.fixed) return; const w=sel.w; sel.w=sel.h; sel.h=w; const c=clampTo(sel,sel.x,sel.y); sel.x=c.x; sel.y=c.y; render(); };
document.getElementById("reset").onclick=()=>{ items=clone(BASE); sel=null; render(); };
document.getElementById("aux").onchange=e=>{ showAux=e.target.checked; render(); };
const zoom=document.getElementById("zoom"); function applyZoom(){ svg.style.width=(VW*zoom.value/100)+"px"; } zoom.oninput=applyZoom; applyZoom();
document.getElementById("copy").onclick=async()=>{ const t=document.getElementById("out"); t.select(); try{ await navigator.clipboard.writeText(t.value); document.getElementById("copied").textContent=" copiado"; }catch(e){ document.getElementById("copied").textContent=" selecione e copie o texto"; } };
load(); render();
</script>
'''
geo["rooms"] = rm
if __name__ == "__main__":
  html = (html.replace("__GEO__", json.dumps(geo)).replace("__PX__", str(PX)).replace("__LABELS__", json.dumps(labels))
              .replace("__VW__", str(int(W * PX))).replace("__VH__", str(int(H * PX))).replace("__ITEMS__", ",\n".join(items)))
  out = os.path.join(os.path.dirname(here), "out", "prancheta.html")
  os.makedirs(os.path.dirname(out), exist_ok=True)
  open(out, "w", encoding="utf-8").write(html)
  print("prancheta.html:", len(html) // 1024, "KB", "|", len(items), "itens")
