"""Independent fixed-domain arithmetic acceptance for the N>=180 supplement.

No historical implementation is imported. The saved leaves are witnesses:
their arithmetic is recomputed on the specified domains, without subdivision,
root searches, optimization, or writing to the archive. Analytic identities
are those stated in the paper; this module checks their rational enclosures.
"""
from fractions import Fraction as F
from math import comb, isqrt
from itertools import combinations
import ast
import sys

OLD = 'research/codim2_endpoint200_20261017'
BAND = 'research/codim2_below200_20261017'
NEW = 'research/codim2_residue2_20261018'
GRID = 10**15
PROFILES = {
    'odd_3_4': (F(-1,4),F(-1,4),F(-1,4),F(3,4)),
    'odd_11_4': (F(-5,4),F(-1,4),F(3,4),F(3,4)),
    'r2_1': (F(-1,2),F(-1,2),F(1,2),F(1,2)),
    'r2_3': (F(-3,2),F(1,2),F(1,2),F(1,2)),
}
ENVELOPE_KEYS = ('cross_m2_upper','same_m2_upper','cross_q_lower','cross_q_upper','same_q_upper')


def insist(ok, label):
    if not ok:
        raise ValueError('continuous arithmetic: '+label)


def ceil_ratio(a,b):
    return -((-a)//b)


def floor_grid(x,scale=GRID):
    x=F(x)
    return F((x.numerator*scale)//x.denominator,scale)


def ceil_grid(x,scale=GRID):
    x=F(x)
    return F(ceil_ratio(x.numerator*scale,x.denominator),scale)


class Interval:
    """Independent integer-endpoint outward interval arithmetic on a fixed grid."""
    __slots__=('a','b')

    def __init__(self,lo=0,hi=None):
        if isinstance(lo,Interval) and hi is None:
            self.a,self.b=lo.a,lo.b
        else:
            lo,hi=F(lo),F(lo if hi is None else hi)
            self.a=(lo.numerator*GRID)//lo.denominator
            self.b=ceil_ratio(hi.numerator*GRID,hi.denominator)
            insist(self.a<=self.b,'ordered interval')

    @classmethod
    def integers(cls,a,b):
        insist(a<=b,'ordered integer endpoints')
        out=object.__new__(cls);out.a,out.b=a,b
        return out

    @property
    def lo(self): return F(self.a,GRID)
    @property
    def hi(self): return F(self.b,GRID)
    def __add__(self,other):
        other=Interval(other)
        return self.integers(self.a+other.a,self.b+other.b)
    __radd__=__add__
    def __neg__(self):return self.integers(-self.b,-self.a)
    def __sub__(self,other):return self+-Interval(other)
    def __rsub__(self,other):return Interval(other)+-self
    def __mul__(self,other):
        other=Interval(other)
        products=[x*y for x in (self.a,self.b) for y in (other.a,other.b)]
        return self.integers(min(products)//GRID,ceil_ratio(max(products),GRID))
    __rmul__=__mul__
    def __truediv__(self,other):
        other=Interval(other)
        insist(other.a>0 or other.b<0,'division excludes zero')
        # Each endpoint quotient is bounded directly with signed integer division.
        lows=[];highs=[]
        for a in (self.a,self.b):
            for b in (other.a,other.b):
                num,den=a*GRID,b
                if den<0:num,den=-num,-den
                lows.append(num//den);highs.append(ceil_ratio(num,den))
        return self.integers(min(lows),max(highs))
    def __rtruediv__(self,other):return Interval(other)/self
    def __pow__(self,n):
        insist(type(n) is int and n>=0,'nonnegative integer power')
        value=Interval(1)
        for _ in range(n):value=value*self
        return value
    def sqrt(self):
        insist(self.a>=0,'nonnegative square root')
        lo=isqrt(self.a*GRID);hi=isqrt(self.b*GRID)
        if hi*hi<self.b*GRID:hi+=1
        return self.integers(lo,hi)


class ExactInterval:
    """Unrounded rational endpoints for the separately saved overlap formula."""
    __slots__=('lo','hi')
    def __init__(self,lo=0,hi=None):
        if isinstance(lo,ExactInterval) and hi is None:self.lo,self.hi=lo.lo,lo.hi
        else:self.lo,self.hi=F(lo),F(lo if hi is None else hi)
        insist(self.lo<=self.hi,'ordered exact interval')
    def __add__(self,v):v=ExactInterval(v);return ExactInterval(self.lo+v.lo,self.hi+v.hi)
    __radd__=__add__
    def __neg__(self):return ExactInterval(-self.hi,-self.lo)
    def __sub__(self,v):return self+-ExactInterval(v)
    def __rsub__(self,v):return ExactInterval(v)+-self
    def __mul__(self,v):
        v=ExactInterval(v);q=[a*b for a in (self.lo,self.hi) for b in (v.lo,v.hi)]
        return ExactInterval(min(q),max(q))
    __rmul__=__mul__
    def __truediv__(self,v):
        v=ExactInterval(v);insist(v.lo>0 or v.hi<0,'exact denominator excludes zero')
        return self*ExactInterval(1/v.hi,1/v.lo)
    def __rtruediv__(self,v):return ExactInterval(v)/self


def pair(ctx,record,computed,label):
    ctx.require(isinstance(record,list) and len(record)==2,label+': pair schema')
    a,b=map(F,record)
    ctx.require(a<=computed.lo<=computed.hi<=b,label+': saved interval encloses independent evaluation')


def closed(ctx,rows,start,end,label,keys=('xlo','xhi')):
    ctx.require(bool(rows),label+': nonempty cover')
    previous=F(start)
    for row in rows:
        a,b=(F(row[k]) for k in keys)
        ctx.require(a==previous and a<b,label+': closed adjacency')
        previous=b
    ctx.require(previous==end,label+': exact final endpoint')


def progress(label):
    print('continuous arithmetic: '+label,file=sys.stderr,flush=True)


def root_leaf(ctx,row,delta,label):
    lo,hi=F(row['xlo']),F(row['xhi'])
    x=Interval(lo,hi);C=sum(d*d for d in delta)
    alpha=(1+Interval(3).sqrt())/4;h0=alpha-F(1,2)
    initial=F(2,3)*C*Interval(hi)**2
    tau=Interval.integers(0,initial.b)
    steps=row['tau_contractions']
    ctx.require(len(steps)==3,label+': three saved root intersections')
    for step in steps:
        pair(ctx,step['before'],tau,label+': root before')
        h=h0-tau
        W=3+1/h-1/(4*h**2);D=2+1/(4*h0*h)
        denominators=[h-2*d*x for d in delta]
        ctx.require(h.lo>0 and W.lo>0 and D.lo>0 and all(v.lo>0 for v in denominators),
                    label+': root identity denominator/sign guards')
        rhs=x**2*W*sum((d*d/v for d,v in zip(delta,denominators)),Interval(0))/D
        pair(ctx,step['rhs'],rhs,label+': independently evaluated root right side')
        tau=Interval.integers(max(tau.a,rhs.a),min(tau.b,rhs.b))
        pair(ctx,step['after'],tau,label+': root intersection')
    lam=alpha-tau
    pair(ctx,row['lambda_interval'],lam,label+': eigenvalue enclosure')
    masses=[F(1,4)+d*x for d in delta]
    ctx.require((1-lam).lo>0 and all((lam-2*p).lo>0 for p in masses),
                label+': positive stress factor denominators')
    ell=[(1-lam-p)/((1-lam)*(lam-2*p)) for p in masses]
    diag=[e*(1-e*(lam-p)) for e,p in zip(ell,masses)]
    trace=sum(diag,Interval(0))
    ctx.require(all(v.lo>0 for v in masses+ell+diag+[trace]),label+': positive masses/stress/trace')
    stress_norm=[d/(p*trace) for d,p in zip(diag,masses)]
    vertices=row['vertices']
    ctx.require(len(vertices)==4 and {v['a'] for v in vertices}==set(range(4)),label+': all four vertices')
    gaps=[]
    for saved in vertices:
        a=saved['a'];others=[b for b in range(4) if b!=a]
        overlaps={b:ell[a]*ell[b]/trace for b in others}
        squares={b:masses[b]**2*(stress_norm[b]-overlaps[b]**2/stress_norm[a]) for b in others}
        area=(2*sum((squares[b]*squares[c] for b,c in combinations(others,2)),Interval(0))-
              sum((squares[b]**2 for b in others),Interval(0)))/4
        determinant=area*sum((1/(masses[b]*masses[c]*overlaps[b]*overlaps[c])
                              for b,c in combinations(others,2)),Interval(0))
        discriminant=1/(ell[a]**2)-4*determinant
        ctx.require(discriminant.hi>=0,label+': true-root discriminant has nonnegative upper bound')
        radical=Interval(discriminant.hi).sqrt()
        gap=lam-(1/ell[a]+radical)/2
        pair(ctx,saved['determinant'],determinant,label+': determinant')
        pair(ctx,saved['discriminant'],discriminant,label+': discriminant')
        ctx.require(F(saved['root_upper'])>=radical.hi,label+': discriminant root upper witness')
        ctx.require(0<F(saved['gap_lower'])<=gap.lo,label+': intrinsic transverse lower bound')
        gaps.append(F(saved['gap_lower']))
    ctx.require(F(row['gap_lower'])==min(gaps),label+': minimum over physical vertices')


def roots(ctx):
    aggregate={n:{name:{'transverse':None,'lambda_lower':None} for name in PROFILES} for n in (180,182)}
    generic_sources={-1:[],1:[]};total=0
    for prefix,start,end,N0 in [(OLD,F(0),F(1,200),200),(BAND,F(1,200),F(1,180),180)]:
        data=ctx.read(prefix+'/residual/ROOT_INTRINSIC_NORMAL.json')
        ctx.require(data['N0']==N0,'root source endpoint')
        if N0==180:ctx.require(list(map(F,data['x_domain']))==[start,end],'root extension exact domain')
        ps=data['profiles'];ctx.require(len(ps)==4 and {p['profile'] for p in ps}==set(PROFILES),'root all count profiles')
        this_count=0;mins=[]
        for p in ps:
            name=p['profile'];delta0=PROFILES[name];C=sum(d*d for d in delta0)
            ctx.require(F(p['count2'])==C,name+': exact count square')
            leaves=p['leaves'];this_count+=len(leaves)
            ctx.require({r['sign'] for r in leaves}=={-1,1},name+': both signs')
            for sign in (-1,1):
                signed=[r for r in leaves if r['sign']==sign]
                closed(ctx,signed,start,end,name+': root closed signed cover')
                for i,row in enumerate(signed):
                    root_leaf(ctx,row,[sign*d for d in delta0],name+': root leaf '+str(i))
                    if name=='r2_1':generic_sources[sign].append({k:row[k] for k in ('xlo','xhi','lambda_interval')})
            minimum=min(F(r['gap_lower']) for r in leaves)
            ctx.require(F(p['minimum_gap'])==minimum,name+': root profile minimum')
            mins.append(minimum)
            for n in aggregate:
                selected=leaves if N0==200 else [r for r in leaves if F(r['xlo'])<=F(1,n)]
                ctx.require(bool(selected),name+': selected endpoint leaf set')
                values={'transverse':min(F(r['gap_lower']) for r in selected),
                        'lambda_lower':min(F(r['lambda_interval'][0]) for r in selected)}
                for key,value in values.items():
                    old=aggregate[n][name][key]
                    aggregate[n][name][key]=value if old is None else min(old,value)
            progress(str(N0)+' root '+name+': '+str(len(leaves))+' fixed leaves accepted')
        ctx.require(data['leaf_boxes']==this_count and F(data['minimum_gap'])==min(mins),'root global counters/minimum')
        total+=this_count
        del data,ps
    for values in aggregate.values():
        for p in values.values():p['cK']=min(p['transverse'],p['lambda_lower'])
    for sign in (-1,1):closed(ctx,generic_sources[sign],F(0),F(1,180),'joined root input for fibers')
    return aggregate,generic_sources,total


def overlap_row(ctx,row,delta,label):
    lo,hi=map(F,row['x']);x=ExactInterval(lo,hi);C=sum(d*d for d in delta)
    scale=10**12;r=isqrt(3*scale*scale)
    alpha=(1+ExactInterval(F(r,scale),F(r+1,scale)))/4
    lam=ExactInterval(alpha.lo-F(2,3)*C*hi*hi,alpha.hi)
    masses=[F(1,4)+d*x for d in delta]
    ctx.require((1-lam).lo>0 and all(p.lo>0 and (lam-2*p).lo>0 for p in masses),label+': mass/stress domains')
    ell=[(1-lam-p)/((1-lam)*(lam-2*p)) for p in masses]
    diagonal=[v*(1-v*(lam-p)) for v,p in zip(ell,masses)]
    trace=sum(diagonal,ExactInterval(0))
    ctx.require(all(v.lo>0 for v in ell+diagonal+[trace]),label+': positive stress diagonal and trace')
    cross=[ell[a]*ell[b]/trace for a,b in combinations(range(4),2)]
    same=[v/(p*trace) for v,p in zip(diagonal,masses)]
    for kind,items in [('cross',cross),('same',same)]:
        lower=floor_grid(min(v.lo for v in items),scale);upper=ceil_grid(max(v.hi for v in items),scale)
        ctx.require(0<F(row[kind+'_lower'])<=lower and F(row[kind+'_upper'])>=upper,label+': '+kind+' enclosure')
    ctx.require(F(row['stress_trace'][0])<=floor_grid(trace.lo,scale) and
                F(row['stress_trace'][1])>=ceil_grid(trace.hi,scale),label+': trace enclosure')


def overlaps(ctx,aggregate):
    total=0
    for prefix,start,end,N0 in [(OLD,F(0),F(1,200),200),(BAND,F(1,200),F(1,180),180)]:
        data=ctx.read(prefix+'/candidate/OVERLAPS_NORMAL.json')
        ctx.require(data['N0']==N0 and data['bins']==256,'overlap fixed cover endpoint/bins')
        if N0==180:ctx.require(list(map(F,data['x_domain']))==[start,end],'overlap extension domain')
        ps=data['profiles'];ctx.require(len(ps)==4 and {p['profile'] for p in ps}==set(PROFILES),'overlap all profiles')
        for p in ps:
            name=p['profile'];ctx.require(F(p['count2'])==sum(d*d for d in PROFILES[name]),name+': overlap count')
            rows=p['rows'];ctx.require(len(rows)==512 and {r['sign'] for r in rows}=={-1,1},name+': overlap signs/count')
            for sign in (-1,1):
                selected=[r for r in rows if r['sign']==sign]
                ctx.require(len(selected)==256,name+': all signed overlap bins')
                for j,row in enumerate(selected):
                    expected=[start+(end-start)*F(j,256),start+(end-start)*F(j+1,256)]
                    ctx.require(row['index']==j and list(map(F,row['x']))==expected,name+': exact overlap closed bin')
                    overlap_row(ctx,row,[sign*d for d in PROFILES[name]],name+': overlap '+str(j))
            for key in ('cross_lower','cross_upper','same_lower','same_upper'):
                extremum=min if key.endswith('lower') else max
                ctx.require(F(p[key])==extremum(F(r[key]) for r in rows),name+': stored overlap global extremum')
                for n in aggregate:
                    selected=rows if N0==200 else [r for r in rows if F(r['x'][0])<=F(1,n)]
                    value=extremum(F(r[key]) for r in selected)
                    old=aggregate[n][name].get(key)
                    aggregate[n][name][key]=value if old is None else extremum(old,value)
            total+=len(rows)
        ctx.require(data['closed_boxes']==2048,'overlap source closed-box total')
        progress(str(N0)+' overlap: 2048 fixed boxes accepted')
    return total


def projected_row(ctx,row,ll,lh,label):
    x=Interval(F(row['xlo']),F(row['xhi']));lam=Interval(ll,lh);sign=row['sign']
    p=[F(1,4)+sign*d*x for d in PROFILES['r2_1']]
    ctx.require(all(v.lo>0 and (lam-2*v).lo>0 for v in p) and
                (1-lam).lo>0 and (2*lam-1).lo>0,label+': physical projector domains')
    ell=[(1-lam-v)/((1-lam)*(lam-2*v)) for v in p]
    diag=[ell[a]*(1-ell[a]*(lam-p[a])) for a in range(4)]
    trace=sum(diag,Interval(0))
    ctx.require(all(v.lo>0 for v in ell+diag+[trace]),label+': positive projector stress')
    t2=[diag[a]**2+sum((ell[a]**2*ell[b]**2*p[a]*p[b] for b in range(4) if b!=a),Interval(0)) for a in range(4)]
    radius=[(3*lam-2+2*v)/(6*v*(2*lam-1)) for v in p]
    k2=[2*t2[a]/(p[a]*trace**2) for a in range(4)]
    ctx.require(all(v.lo>0 for v in radius+k2),label+': positive physical squared norms')
    pairs=row['pairs'];ctx.require(len(pairs)==16 and {(v['a'],v['b']) for v in pairs}=={(a,b) for a in range(4) for b in range(4)},label+': all ordered fibers')
    for value in pairs:
        a,b=value['a'],value['b']
        stress=ell[a]*ell[b]/trace if a!=b else diag[a]/(p[a]*trace)
        ctx.require(stress.lo>0,label+': positive correct same/cross stress')
        m=k2[b]-stress**2/radius[a];q=k2[b]/stress**2-1/radius[a]
        ctx.require(m.hi>=0 and q.hi>=0,label+': nonnegative projected upper bounds')
        pair(ctx,value['stress'],stress,label+': physical overlap')
        for key,v in [('m2',m),('q',q)]:
            lo,hi=map(F,value[key])
            ctx.require(0<=lo<=max(F(0),v.lo) and hi>=v.hi,label+': projected '+key)
    cross=[v for v in pairs if v['a']!=v['b']];same=[v for v in pairs if v['a']==v['b']]
    expected={'cross_m2_upper':max(F(v['m2'][1]) for v in cross),'same_m2_upper':max(F(v['m2'][1]) for v in same),
              'cross_q_lower':min(F(v['q'][0]) for v in cross),'cross_q_upper':max(F(v['q'][1]) for v in cross),
              'same_q_upper':max(F(v['q'][1]) for v in same)}
    for key,value in expected.items():ctx.require(F(row[key])==value,label+': projected maximum/minimum '+key)


def envelope(rows,n,keys=ENVELOPE_KEYS):
    chosen=[r for r in rows if F(r['xlo'])<=F(1,n)]
    return {k:(min if k.endswith('lower') else max)(F(r[k]) for r in chosen) for k in keys}


def projected(ctx,sources):
    data=ctx.read(NEW+'/mixed/EXACT_PROJECTED_R2_1.json');rows=data['rows']
    ctx.require(len(rows)==1024 and data['cells']==1024 and data['bins']==512,'generic projected complete grid')
    for sign in (-1,1):
        group=[r for r in rows if r['sign']==sign]
        ctx.require(len(group)==512,'generic projected both signs')
        closed(ctx,group,F(0),F(1,180),'generic projected cover')
        leaves=sources[sign];pos=0
        for j,row in enumerate(group):
            lo,hi=F(j,180*512),F(j+1,180*512)
            ctx.require((F(row['xlo']),F(row['xhi']))==(lo,hi),'generic fixed projected bin')
            while pos<len(leaves) and F(leaves[pos]['xhi'])<lo:pos+=1
            selected=[];end=pos
            while end<len(leaves) and F(leaves[end]['xlo'])<=hi:selected.append(leaves[end]);end+=1
            ctx.require(bool(selected) and F(selected[0]['xlo'])<=lo and F(selected[-1]['xhi'])>=hi,'root leaves cover whole generic bin')
            ll=min(F(r['lambda_interval'][0]) for r in selected);lh=max(F(r['lambda_interval'][1]) for r in selected)
            ctx.require(list(map(F,row['lambda_interval']))==[ll,lh] and row['source_leaves']==len(selected),'generic root-leaf binding')
            projected_row(ctx,row,ll,lh,'generic projected '+str(sign)+':'+str(j))
    return {n:envelope(rows,n) for n in (180,182)}


# These rational identities are fixed mathematical inputs from the two-pair
# projector calculation, not executable expressions supplied by an archive.
SHARP = {
 'aa':('-2*(4*t*x+20*x**2+8*x-3)/((2*x-1)*(44*x**2+12*x-9))',
       '2*(2*x-1)*(8*x**2-3)*(4*t*x+20*x**2+8*x-3)/((2*x+1)**2*(44*x**2+12*x-9))'),
 'ab':('2*(-32*t*x**3-12*t*x**2+6*t*x+16*x**4+56*x**3-36*x**2-24*x+9)/((2*x+1)*(8*x**2-3)*(44*x**2+12*x-9))',
       '-2*(-32*t*x**3-12*t*x**2+6*t*x+16*x**4+56*x**3-36*x**2-24*x+9)/((2*x+1)*(44*x**2+12*x-9))'),
 'ba':('-2*(32*t*x**3-12*t*x**2-6*t*x+16*x**4-56*x**3-36*x**2+24*x+9)/((2*x-1)*(8*x**2-3)*(44*x**2-12*x-9))',
       '2*(32*t*x**3-12*t*x**2-6*t*x+16*x**4-56*x**3-36*x**2+24*x+9)/((2*x-1)*(44*x**2-12*x-9))'),
 'bb':('2*(-4*t*x+20*x**2-8*x-3)/((2*x+1)*(44*x**2-12*x-9))',
       '-2*(2*x+1)*(8*x**2-3)*(-4*t*x+20*x**2-8*x-3)/((2*x-1)**2*(44*x**2-12*x-9))'),
 'same_a':('8*x**2*(4*t*x+20*x**2+8*x-3)/((2*x-1)*(8*x**2-3)*(44*x**2+12*x-9))',
           '8*x**2*(-32*t*x**2+104*x**3-36*x**2-42*x+9)/(9*(2*x-1)*(2*x+1)*(44*x**2+12*x-9))'),
 'same_b':('-8*x**2*(-4*t*x+20*x**2-8*x-3)/((2*x+1)*(8*x**2-3)*(44*x**2-12*x-9))',
           '-8*x**2*(32*t*x**2+104*x**3+36*x**2-42*x-9)/(9*(2*x-1)*(2*x+1)*(44*x**2-12*x-9))'),
}


def mathematical_expression(node,x,t):
    if isinstance(node,ast.Expression):return mathematical_expression(node.body,x,t)
    if isinstance(node,ast.Constant):
        insist(type(node.value) is int,'integer formula coefficient');return Interval(node.value)
    if isinstance(node,ast.Name):
        insist(node.id in ('x','t'),'fixed formula symbol');return x if node.id=='x' else t
    if isinstance(node,ast.UnaryOp):
        value=mathematical_expression(node.operand,x,t)
        if isinstance(node.op,ast.USub):return -value
        if isinstance(node.op,ast.UAdd):return value
    if isinstance(node,ast.BinOp):
        left=mathematical_expression(node.left,x,t)
        if isinstance(node.op,ast.Pow):
            insist(isinstance(node.right,ast.Constant) and type(node.right.value) is int and 0<=node.right.value<=8,'fixed polynomial exponent')
            return left**node.right.value
        right=mathematical_expression(node.right,x,t)
        if isinstance(node.op,ast.Add):return left+right
        if isinstance(node.op,ast.Sub):return left-right
        if isinstance(node.op,ast.Mult):return left*right
        if isinstance(node.op,ast.Div):return left/right
    raise ValueError('unsupported fixed mathematical expression')


def sharp(ctx):
    data=ctx.read(NEW+'/mixed/SHARP_FIBERS.json');rows=data['rows']
    ctx.require(len(rows)==512 and data['bins']==512 and data['N0']==180,'sharp fiber fixed grid')
    forms={k:[ast.parse(s,mode='eval') for s in expressions] for k,expressions in SHARP.items()}
    closed(ctx,rows,F(0),F(1,180),'sharp fiber cover')
    for j,row in enumerate(rows):
        lo,hi=F(j,180*512),F(j+1,180*512)
        ctx.require((F(row['xlo']),F(row['xhi']))==(lo,hi),'sharp exact bin')
        x=Interval(lo,hi);t=(3-8*x**2).sqrt()
        ctx.require(t.lo>0,'sharp positive algebraic root')
        pair(ctx,row['t_interval'],t,'sharp t root enclosure')
        saved=row['pairs'];ctx.require(set(saved)==set(SHARP),'all six sharp ordered types')
        for key,expressions in forms.items():
            for field,expression in zip(('m_squared','q'),expressions):
                value=mathematical_expression(expression,x,t);a,b=map(F,saved[key][field])
                ctx.require(value.hi>=0 and 0<=a<=max(F(0),value.lo) and b>=value.hi,'sharp projected '+key+':'+field)
        cross=[saved[k] for k in ('aa','ab','ba','bb')];same=[saved[k] for k in ('same_a','same_b')]
        values={'cross_m2_upper':max(F(v['m_squared'][1]) for v in cross),'same_m2_upper':max(F(v['m_squared'][1]) for v in same),
                'cross_q_lower':min(F(v['q'][0]) for v in cross),'cross_q_upper':max(F(v['q'][1]) for v in cross),
                'same_q_upper':max(F(v['q'][1]) for v in same)}
        for key,value in values.items():ctx.require(F(row[key])==value,'sharp fiber extrema '+key)
    stationary=ctx.read(NEW+'/mixed/SHARP_STATIONARY.json')['rows']
    ctx.require(len(stationary)==512,'stationary all512 rows')
    closed(ctx,stationary,F(0),F(1,180),'stationary closed cover')
    for fiber,row in zip(rows,stationary):
        ctx.require((row['xlo'],row['xhi'])==(fiber['xlo'],fiber['xhi']),'stationary same-bin correlation')
        x=Interval(F(fiber['xlo']),F(fiber['xhi']));t=Interval(*map(F,fiber['t_interval']));lam=(1+t)/4
        a,b=F(1,4)-x/2,F(1,4)+x/2
        ctx.require(set(row['centers'])=={'a','b'},'stationary both centers')
        for center,sc,mc,sk,p,r in [('a','aa','ab','same_a',a,b),('b','bb','ba','same_b',b,a)]:
            def bounds(which,key):return Interval(*map(F,fiber['pairs'][which][key]))
            qs,qc,qm=bounds(sk,'q'),bounds(sc,'q'),bounds(mc,'q')
            ms,mco,mm=bounds(sk,'m_squared').sqrt(),bounds(sc,'m_squared').sqrt(),bounds(mc,'m_squared').sqrt()
            ctx.require(p.lo>0 and r.lo>0 and (lam-p).lo>0,'stationary positive weights')
            qdiff=qc-qm;diff=max(abs(qdiff.lo),abs(qdiff.hi))
            first=p*diff*mco+(p*qs+qm*(lam-p))*ms
            third=p*qs*ms+p*qc*mco+2*r*qm*mm
            out=(first+third)/8;s=row['centers'][center]
            for key,value in [('F1',first),('F3',third),('Prow',out)]:pair(ctx,s[key],value,'stationary '+center+':'+key)
            ctx.require(F(s['cross_ratio_difference_upper'])>=diff,'stationary exact ratio-difference upper')
        ctx.require(F(row['Prow_upper'])==max(F(c['Prow'][1]) for c in row['centers'].values()),'stationary maximum both centers')
    return {n:{**envelope(rows,n),'Prow_upper':envelope(stationary,n,('Prow_upper',))['Prow_upper']} for n in (180,182)}


def padd(a,b):
    value=[F(0)]*max(len(a),len(b))
    for i,x in enumerate(a):value[i]+=x
    for i,x in enumerate(b):value[i]+=x
    return value


def pmul(a,b):
    value=[F(0)]*(len(a)+len(b)-1)
    for i,x in enumerate(a):
        for j,y in enumerate(b):value[i+j]+=x*y
    return value


def pscale(a,c):return [F(c)*x for x in a]


def partial_power(z,alpha):
    """Expand the analytic polynomial from products, independently of stored coefficients."""
    A=[F(1),F(0),F(-1)];A2=pmul(A,A);A3=pmul(A2,A)
    H=padd(pscale(pmul(A,[-1,0,5]),F(1,8)),
           padd(pscale(pmul([0,1],A2),3*z/8),pscale(A3,z*z/16)))
    root3=Interval(3).sqrt().lo;c3=1/(3*root3)
    unsigned=padd(pscale(A2,F(1,8)),[-c3/z,1/(2*z),0,-1/(2*z)])
    return padd(pscale(H,alpha),pscale(unsigned,1-alpha)),c3


def bernstein(power,a,b):
    """Polynomial composition t=a+(b-a)s followed by power-to-Bernstein conversion."""
    shifted=[F(0)];power_of_linear=[F(1)]
    for coefficient in power:
        shifted=padd(shifted,pscale(power_of_linear,coefficient))
        power_of_linear=pmul(power_of_linear,[a,b-a])
    degree=len(power)-1
    return [sum((shifted[k]*F(comb(i,k),comb(degree,k)) for k in range(i+1)),F(0)) for i in range(degree+1)]


def tails(ctx):
    data=ctx.read(NEW+'/local/REFINED_182_NORMAL.json');seen=set();count=0
    for row in data['rows']:
        identity=(row['u_index'],row['w_index'])
        ctx.require(identity not in seen,'unique adopted tail region');seen.add(identity)
        choices=row['choices'];ctx.require(len(choices)==4 and {F(c['alpha']) for c in choices}=={F(1,4),F(1,2),F(3,4),F(1)},'four whole signed alternatives')
        for choice in choices:
            ctx.require(set(choice['types'])=={'cross','same'},'both complete scalar tail types')
            for name,value in choice['types'].items():
                saved=value['tail_certificate'];z,alpha=F(saved['z']),F(saved['alpha'])
                ctx.require(z>0 and 0<=alpha<=1 and alpha==F(choice['alpha']) and z==F(value['z']),
                            'partial signed tail domain and type binding')
                power,c3=partial_power(z,alpha)
                ctx.require(F(saved['c3'])==c3 and len(power)==7,'independent degree-six polynomial and cubic bound')
                boxes=saved['boxes'];ctx.require(len(boxes)==saved['bins']==32,'all32 Bernstein intervals')
                coefficients=[]
                for j,box in enumerate(boxes):
                    a,b=F(j,32),F(j+1,32)
                    ctx.require(F(box['a'])==a and F(box['b'])==b,'closed scalar Bernstein grid')
                    expected=bernstein(power,a,b)
                    ctx.require(list(map(F,box['coefficients']))==expected,'recomputed complete Bernstein coefficients')
                    ctx.require(F(box['upper'])==max(expected),'Bernstein box upper')
                    coefficients.extend(expected)
                Q=max(coefficients)
                ctx.require(Q>=0 and F(saved['Q'])==Q and F(value['Q'])==Q,'recomputed complete nonnegative tail Q')
                count+=1
    ctx.require(len(seen)==60 and count==480,'all adopted scalar tail certificates')
    progress('480 complete degree-six tail certificates accepted')
    return count


def verify(ctx):
    aggregate,sources,leaves=roots(ctx)
    overlap_count=overlaps(ctx,aggregate)
    generic=projected(ctx,sources);progress('1024 generic projected fibers accepted')
    sharp_bounds=sharp(ctx);progress('512 sharp fiber and stationary bins accepted')
    tail_count=tails(ctx)
    ctx.facts['continuous']={'by_endpoint':aggregate,'generic_projected':generic,'sharp':sharp_bounds,
                             'tails_checked':tail_count}
    return {'status':'PASS','fixed_root_leaves_recomputed':leaves,'closed_overlap_boxes_recomputed':overlap_count,
            'generic_projected_boxes_recomputed':1024,'sharp_fiber_boxes_recomputed':512,
            'stationary_boxes_recomputed':512,'tail_certificates_recomputed':tail_count,
            'bernstein_boxes_recomputed':32*tail_count,'reciprocal_domain':['0','1/180'],
            'frozen_endpoints':[180,182],'adaptive_splitting':False,'root_search':False,
            'optimization':False,'historical_modules_imported':False}
