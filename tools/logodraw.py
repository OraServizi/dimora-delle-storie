"""Logo «che si disegna»: SVG in linea con la chiave tracciata a mano e la scritta che compare dopo."""
import os, re
K3D = '<g class="k3dg"><defs><mask id="__P__k3m" style="mask-type:alpha"><image href="/img/chiave-3d.webp" x="143.42" y="98.12" width="88.33" height="160.79" preserveAspectRatio="none"/></mask><linearGradient id="__P__k3s" x1="0" y1="0" x2="1" y2="0.35"><stop offset="0" stop-color="#fff" stop-opacity="0"/><stop offset=".5" stop-color="#FFF6DD" stop-opacity=".55"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient></defs><image class="k3d" href="/img/chiave-3d.webp" x="143.42" y="98.12" width="88.33" height="160.79" preserveAspectRatio="none"/><g mask="url(#__P__k3m)"><rect class="k3s" x="83.42" y="98.12" width="50" height="160.79" fill="url(#__P__k3s)"/></g></g>'
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_n = [0]

def svg(cls="", start=0.3, label="", with3d=True):
    _n[0] += 1
    s = open(f"{ROOT}/img/logo-chiaro.svg", encoding="utf-8").read()
    s = re.sub(r'<\?xml[^>]*>', '', s)
    s = re.sub(r' width="\d+"| height="\d+"', '', s, count=2)
    attrs = f'class="ldraw {cls}" ' + (f'role="img" aria-label="{label}" ' if label else 'aria-hidden="true" ')
    s = s.replace('<svg ', f'<svg style="--t3:{start+4.2:.2f}s" ' + attrs, 1)
    pre = f"ld{_n[0]}-"
    for idv in set(re.findall(r'id="([^"]+)"', s)):
        s = s.replace(f'id="{idv}"', f'id="{pre}{idv}"').replace(f'url(#{idv})', f'url(#{pre}{idv})').replace(f'href="#{idv}"', f'href="#{pre}{idv}"')
    order = [0, 0.9, 1.1, 1.9, 2.4, 2.6, 2.8, 1.35, 1.6]
    k = [0]
    def gold(m):
        d = start + order[k[0] % len(order)]; k[0] += 1
        return f'<path class="kp" pathLength="1" style="--d:{d:.2f}s" fill="#D4A65A"'
    s = re.sub(r'<path fill="#D4A65A"', gold, s)
    t = [0]
    def ivory(m):
        d = start + 3.0 + t[0] * 0.035; t[0] += 1
        return f'<g class="kt" style="--d:{d:.2f}s" fill="#EFE8DC"'
    s = re.sub(r'<g fill="#EFE8DC"', ivory, s)
    s = s.replace('</svg>', K3D.replace('__P__', pre) + '</svg>', 1) if with3d else s
    return s

CSS = '''
.ldraw{overflow:visible}
.ldraw .kp{fill:rgba(212,166,90,0);stroke:#E9C47E;stroke-width:.55;stroke-linejoin:round;stroke-dasharray:1 1;stroke-dashoffset:1}
.ldraw .kt{opacity:0;transform:translateY(4px);transform-box:fill-box}
.ldraw.go .kp{animation:kDraw 2.2s cubic-bezier(.45,.05,.3,1) var(--d) forwards,kFill 1.4s ease calc(var(--d) + 1.7s) forwards}
.ldraw.go .kt{animation:kText 1.2s ease var(--d) forwards}
@keyframes kDraw{to{stroke-dashoffset:0}}
@keyframes kFill{to{fill:#D4A65A;stroke-width:0}}
@keyframes kText{to{opacity:1;transform:none}}
@media (prefers-reduced-motion:reduce){.ldraw .kp{fill:#D4A65A;stroke:none}.ldraw .kt{opacity:1;transform:none}.ldraw.go .kp,.ldraw.go .kt{animation:none}}
.ldraw .k3dg{opacity:0;transform-box:fill-box;transform-origin:50% 55%}
.ldraw .k3d{filter:drop-shadow(0 1px 1px rgba(0,0,0,.5))}
.ldraw .k3s{opacity:0}
.ldraw.go .k3dg{animation:k3In 1.6s cubic-bezier(.2,.7,.2,1) var(--t3) forwards,k3Lift 2.6s cubic-bezier(.3,.6,.2,1) calc(var(--t3) + .9s) forwards}
.ldraw.go .k3d{animation:k3Shadow 2.6s ease calc(var(--t3) + .9s) forwards}
.ldraw.go .k3s{animation:k3Sheen 1.8s ease-in-out calc(var(--t3) + 1.3s) forwards}
.ldraw.go .kp{animation:kDraw 2.2s cubic-bezier(.45,.05,.3,1) var(--d) forwards,kFill 1.4s ease calc(var(--d) + 1.7s) forwards,kOut .9s ease calc(var(--t3) + .4s) forwards}
@keyframes k3In{from{opacity:0;transform:scale(.97)}to{opacity:1;transform:scale(1)}}
@keyframes k3Lift{0%{transform:scale(1) translateY(0)}60%{transform:scale(1.09) translateY(-1.5%)}100%{transform:scale(1.06) translateY(-1%)}}
@keyframes k3Shadow{to{filter:drop-shadow(0 5px 4px rgba(0,0,0,.6)) drop-shadow(0 0 8px rgba(226,183,106,.25))}}
@keyframes k3Sheen{0%{opacity:0;transform:translateX(0)}15%{opacity:1}85%{opacity:1}100%{opacity:0;transform:translateX(160px)}}
@keyframes kOut{to{opacity:0}}
@media (prefers-reduced-motion:reduce){.ldraw .k3dg{opacity:1}.ldraw .kp{opacity:0}}
'''

JS = '''<script>(function(){var ls=document.querySelectorAll('.ldraw');if(!ls.length)return;
if(!('IntersectionObserver' in window)){ls.forEach(function(l){l.classList.add('go')});return;}
var io=new IntersectionObserver(function(es){es.forEach(function(e){if(e.isIntersecting){e.target.classList.add('go');io.unobserve(e.target);}})},{threshold:.35});
ls.forEach(function(l){io.observe(l)});})();</script>
'''
