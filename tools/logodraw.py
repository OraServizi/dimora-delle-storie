"""Logo «che si disegna»: SVG in linea con la chiave tracciata a mano e la scritta che compare dopo."""
import os, re
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_n = [0]

def svg(cls="", start=0.3, label=""):
    _n[0] += 1
    s = open(f"{ROOT}/img/logo-chiaro.svg", encoding="utf-8").read()
    s = re.sub(r'<\?xml[^>]*>', '', s)
    s = re.sub(r' width="\d+"| height="\d+"', '', s, count=2)
    attrs = f'class="ldraw {cls}" ' + (f'role="img" aria-label="{label}" ' if label else 'aria-hidden="true" ')
    s = s.replace('<svg ', '<svg ' + attrs, 1)
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
'''

JS = '''<script>(function(){var ls=document.querySelectorAll('.ldraw');if(!ls.length)return;
if(!('IntersectionObserver' in window)){ls.forEach(function(l){l.classList.add('go')});return;}
var io=new IntersectionObserver(function(es){es.forEach(function(e){if(e.isIntersecting){e.target.classList.add('go');io.unobserve(e.target);}})},{threshold:.35});
ls.forEach(function(l){io.observe(l)});})();</script>
'''
