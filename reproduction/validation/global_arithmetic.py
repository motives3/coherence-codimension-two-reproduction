"""Independent fixed-domain global, counting, fine and polar acceptance.

Only Fraction and integer square roots are used. Saved cells/stages are
the proposed proof witness: no optimization, adaptive subdivision or
threshold search is performed. No producer module is imported.
"""
from fractions import Fraction as F
from math import isqrt

OLD='research/codim2_below200_20261017'
NEW='research/codim2_residue2_20261018'
CR,CM,OP,EMAX=F(13,4),F(81,10),F(23,10),F(293,500)
RAW=(F(19739570097,6400000000),F(375,58),F(1123,200))
PROFILES={'odd_3_4':(F(1,2),F(3,4),F(3,4),F(3,2),(-1,-1,-1,3),4),
 'odd_11_4':(F(1,2),F(11,4),F(5,4),F(3),(-5,-1,3,3),4),
 'r2_1':(F(11,19),F(1),F(1,2),F(2),(-1,-1,1,1),2),
 'r2_3':(F(11,19),F(3),F(3,2),F(3),(-3,1,1,1),2)}

def down(x,s=10**10):
 x=F(x)
 if x<0: raise ValueError('negative square root')
 return F(isqrt(x.numerator*s*s//x.denominator),s)

def up(x,s=10**10):
 x=F(x); q=down(x,s)
 return q if q*q==x else q+F(1,s)

def floor(x,s=10**8):
 x=F(x);return F(x.numerator*s//x.denominator,s)

def ceil(x,s=10**8):
 x=F(x);return F(-(-x.numerator*s//x.denominator),s)

def energy(n,M,U,W):
 k=CR/F(n)
 if not(0<=U<=M and 0<=W<=M and k*M<1):raise ValueError('energy domain')
 if W==0:return F(0)
 def at(u,w):return w/(1-up(k*u))**2
 split=M-W
 answer=at(min(U,split),W)
 if U>split:
  stationary=k*M*M
  answer=max(answer,M/(1-k*M) if split<=stationary<=U else
             at(split,W) if stationary<split else at(U,M-U))
 return answer

def moment(z,U):
 A,B,J=RAW; bound=min(CM*z,(A+B+up((A-B)**2+J*J))*z/2)
 U=min(U,z)
 if 2*U<=z and J*J*(z-2*U)**2>=4*(B-A)**2*U*(z-U):
  bound=min(bound,A*U+B*(z-U)+J*up(U*(z-U)))
 return bound

def spherical(polar,scatter):
 if scatter>=2:return F(4,3)
 g=polar-F(1,3);cos=1-scatter+scatter*scatter/8
 if g>=cos or g>=1:return F(4,3)
 if g< -1:raise ValueError('spherical cap domain')
 sine=up(2*scatter*(1-scatter/8))*(1-scatter/4)
 return min(F(4,3),ceil(g*cos+up(1-g*g)*sine+F(1,3)))

def shared(n,c,q,p,M,U,W,E,bins):
 a=F(4,3)/(n*p);b=up(4*c/(n*(1+q)))
 dm=c/(n*n*p);dp=dm*(1+up(6)/(1+q)); rows=[]
 for j in range(bins):
  lo,hi=M*j/bins,M*(j+1)/bins;u,w=min(U,hi),min(W,M-lo)
  en=min(E,energy(n,M,u,w));mo=moment(hi,u)
  pol=a*up(mo)+dp*en;mean=a*up(mo)+dm*en
  lin=pol+b*up(en);sc=2*c*en/(n*(1+q));sph=spherical(pol,sc)
  rows.append(dict(zlo=lo,zhi=hi,radial_upper=u,angular_upper=w,
    energy_upper=en,moment_upper=mo,cross=ceil(min(lin,sph)),
    linear_cross=ceil(lin),spherical_cross=sph,scatter_upper=sc,
    polar=ceil(pol),mean=ceil(mean)))
 return dict(energy_upper=E,cross=max(r['cross'] for r in rows),
    polar=max(r['polar'] for r in rows),mean=max(r['mean'] for r in rows),
    bins=bins,ledger=rows)

def eq(ctx,saved,value,name):
 """Bind each rederived scalar; booleans/metadata cannot stand in for arithmetic."""
 if isinstance(value,dict):
  ctx.require(isinstance(saved,dict),name+': object')
  for k,v in value.items():
   ctx.require(k in saved,name+': key '+k);eq(ctx,saved[k],v,name+'/'+k)
 elif isinstance(value,(tuple,list)):
  ctx.require(isinstance(saved,list) and len(saved)==len(value),name+': length')
  for i,(s,v) in enumerate(zip(saved,value)):eq(ctx,s,v,name+'/'+str(i))
 else:
  ctx.require(F(saved)==value,name+': rederived rational')

def stage(n,c,E,M,U,W,mc):
 p=F(1,4)-mc/n;pp=F(1,4)+mc/n;S=c*E/n
 q=down(1-S/(p*n));tf=2/(1+q);T=tf*S
 if q<=0:raise ValueError('positive mean guard')
 a=F(4,3)*up(CM)/(n*p);b=up(4*c/(n*(1+q)))
 d=c*(1+up(6)/(1+q))/(n*n*p)
 cap_shared=ceil(up(M)*up(a*a+b*b)+b*up(CR/n)*M/(2*(1-F(103,1000)))+d*E)
 s=up(CR*U/n)
 if s>=1:raise ValueError('radial guard')
 B=b/(1-s);wstar=M*B*B/(a*a+B*B)
 rectangle=up(M*(a*a+B*B)) if wstar<=W else a*up(M-W)+B*up(W)
 cap_rectangle=ceil(rectangle+d*E)
 sh=shared(n,c,q,p,M,U,W,E,64)
 cap=min(cap_shared,cap_rectangle,sh['cross']);rm=up(CM*M)
 G=min(sh['polar'],ceil(F(4,3)*(rm+F(3,4)*S)/(p*n)+up(6)*S/(p*n*(1+q))))
 hw=down(1-S/2);hc=up((F(2,3)+cap)/2)
 bb,kk=F(577351,10**6),F(348075,10**6)
 if not(hw>bb and hc<1):raise ValueError('overlap guard')
 kw=floor((hw-bb)**2*(F(3,4)+kk*hw)/(4*(1+hw)))
 kc=floor((1-hc)*(F(3,4)+kk*hc)/(4*(hc+bb)**2))
 mu=floor(2*(F(1,3)-(OP+S)/n-pp*T/(2*(1+q))))
 beta=2*p*kw+mu*kc
 if min(kw,kc,mu,beta)<=0:raise ValueError('covariance guard')
 return dict(c=c,S=S,q=q,tf=tf,T=T,G=G,cap=cap,hw=hw,hc=hc,kw=kw,
   kc=kc,mu=mu,beta=beta,p=p,pp=pp,rootmoment=rm,cap_shared=cap_shared,
   cap_rectangle=cap_rectangle,budget=sh)

def fine(ctx,r,profile):
 n=F(180);M=F(profile['M']);U,W=F(r['uhi']),F(r['whi']);mc=F(profile['maxcount'])
 saved=r['fine'];ctx.require(saved['N0']==180 and saved['seed']==31,'fine fixed domain')
 eq(ctx,saved,dict(uhi=U,whi=W,M=M,maxcount=mc),'fine domain')
 E=min(EMAX,energy(n,M,U,W));eq(ctx,saved['E_upper'],E,'regional energy')
 c=F(31)
 for entry in saved['bootstrap']:
  z=stage(n,c,E,M,U,W,mc);eq(ctx,entry,z,'regional bootstrap')
  nxt=F(entry['next'])
  ctx.require(nxt.denominator==1 and 0<nxt<c and z['beta']>1/nxt,'valid saved forward step')
  c=nxt
 z=stage(n,c,E,M,U,W,mc);eq(ctx,saved['final'],z,'regional final')
 p,pp,q,S,G=[z[k] for k in ('p','pp','q','S','G')]
 bb,kk=F(577351,10**6),F(348075,10**6)
 hm=up((F(2,3)+min(F(4,3)*(z['rootmoment']+F(3,4)*S)/(p*n),z['budget']['mean']))/2)
 ctx.require(hm<1 and G<F(1,12),'mean and polar guards')
 km=floor((1-hm)*(F(3,4)+kk*hm)/(4*(hm+bb)**2))
 gamma=floor(1/(4*z['hc']**3)-2*F(349,1000))
 ctx.require(km>0 and (9+4*F(349,1000))**2>108,'mean and scalar curvature')
 bj=2*p*z['kw']+z['mu']*max(gamma,0)/8
 pol=ceil(max(F(3,4)/(1+down(1-F(3,4)*G))**2,F(3,8)/(1-F(3,4)*G)))
 tau=F(201,200);AQ=pp*pol*tau/(p*p)
 AS=z['tf']+pp*pol*(1+1/(tau-1))*6*S/(p*p*n*(1+q)**2)
 fs=saved['final'];theta=F(fs['blend'])
 ctx.require(0<=theta<=1 and (theta==0 or gamma>0),'valid conditional Jensen blend')
 cq=(1-theta)*z['kc']+theta*km;cs=(1-theta)*z['beta']+theta*bj
 ctx.require(min(cq,cs)>0,'mixed covariance')
 bloch=ceil(max(AQ/cq,AS/cs));phase=F(fs['phase'])
 ctx.require(phase in (F(127,128),F(63,64),F(31,32)),'allowed phase floor')
 ctx.require(max(bloch*E/n,z['tf']*S,pol*G*G)<4*(1-phase*phase),'three independent phase guards')
 cv=1/(2*(1+phase));pc=up(cv*pol)
 point=ceil((up(cv*z['tf']/z['beta']+pc*pc/(p*p*n*z['kc']))+
       pc*up(6)/(p*(1+q))*up(E/n**3)/z['beta'])**2)
 eq(ctx,fs,dict(mean_cross=km,gamma=gamma,mix_Q=cq,mix_S=cs,polar=pol,AQ=AQ,AS=AS),'fine polar')
 for b in fs['blend_candidates']:
  t=F(b['theta']);ctx.require(0<=t<=1 and (t==0 or gamma>0),'candidate blend valid')
  qb=(1-t)*z['kc']+t*km;sb=(1-t)*z['beta']+t*bj
  eq(ctx,b,dict(Q=qb,S=sb,Bloch=max(AQ/qb,AS/sb)),'complete blend')
 interface=dict(S=c,Bloch=bloch,unit_total=ceil(cv*bloch),unit_point=point)
 eq(ctx,saved['interface'],interface,'regional simultaneous physical interface')
 return interface

def candidate(ctx,saved,n,C,mc,deltas):
 s=10**12;e=mc/n;sig=up(C,s)/n;b=F(109,100);k=F(8,3)/b;q=1-4*e/b
 ctx.require(e<=F(1,120) and q>0,'candidate domain')
 entries=[F(32,3)*(abs(x*x+4*x*y+y*y)+4*abs((x+y)*x*y)/(b*n))/(b*b*n*n*q*q)
          for i,x in enumerate(deltas) for j,y in enumerate(deltas) if i!=j]
 f=up(sum(x*x for x in entries),s)*n/down(C,s)
 ec=F(3,4)*up(2,s)*k+F(3,4)*f;zc=up(3,s)*(k+f)/4
 p=down(1-ec*sig,s);ctx.require(p>0,'candidate polar floor')
 rp=ec*ec*sig/(2*(1+p)**2);ri=ec*zc*sig/(p*(1+p));R=F(13,16)*f+rp+ri
 cr=F(4,11)/((1-4*e)*(1+F(499,500)));ph=F(501,500)/(2*(1+F(999,1000)))
 pts=[cr*cr*x*x/C+ph*(up(3-4*x*x/C,s)/b+R)**2 for x in deltas]
 totalbloch=up(8,s)/b+up(F(15,16),s)*f+2*rp/down(3,s)+2*ri
 result=dict(N0=n,count=C,maxcount=mc,e=e,sigma_upper=sig,gram_remainder=f,
  polar_floor=p,point=max(pts),total=(F(1,4)+e)*(cr*cr+ph*totalbloch**2),
  point_columns=pts,profile=deltas,gram_entry_upper=entries,polar_E_coefficient=ec,
  polar_z_coefficient=zc,point_Bloch_remainder=R,total_Bloch=totalbloch,radial=cr,
  polar_square_remainder=rp,polar_inverse_remainder=ri)
 eq(ctx,saved,result,'candidate polar arithmetic')
 return result

class Q:
 """Small independent fixed-denominator enclosure for counting witnesses."""
 scale=10**15
 def __init__(self,x=0,bounds=None):
  if bounds is not None:self.l,self.h=map(F,bounds)
  elif isinstance(x,Q):self.l,self.h=x.l,x.h
  else:self.l,self.h=floor(x,self.scale),ceil(x,self.scale)
 def __add__(self,y):
  y=Q(y);return Q(bounds=(self.l+y.l,self.h+y.h))
 __radd__=__add__
 def __neg__(self):return Q(bounds=(-self.h,-self.l))
 def __sub__(self,y):return self+-Q(y)
 def __rsub__(self,y):return Q(y)+-self
 def __mul__(self,y):
  y=Q(y);v=[a*b for a in (self.l,self.h) for b in (y.l,y.h)]
  return Q(bounds=(floor(min(v),self.scale),ceil(max(v),self.scale)))
 __rmul__=__mul__
 def __truediv__(self,y):
  y=Q(y)
  if y.l<=0<=y.h:raise ValueError('count interval zero denominator')
  v=[a/b for a in (self.l,self.h) for b in (y.l,y.h)]
  return Q(bounds=(floor(min(v),self.scale),ceil(max(v),self.scale)))
 def __rtruediv__(self,y):return Q(y)/self
 def __pow__(self,k):
  z=Q(1)
  for _ in range(k):z=z*self
  return z
 def sqrt(self):return Q(bounds=(down(self.l,self.scale),up(self.h,self.scale)))

def count_box(M,i,j):
 U=M*(i+1)/60;W=M*(j+1)/60;V=M-M*i/60-M*j/60
 radial=Q(CR*U/180).sqrt();rho=1/(1-radial)**2
 mo=RAW[0]*Q(U)+RAW[1]*Q(V)+RAW[2]*Q(U*V).sqrt()
 S=31*Q(W)*rho/180
 return (mo.sqrt()+F(13,10)*S).h

def global_entry(ctx):
 d=ctx.read(OLD+'/global/ENTRY_NORMAL.json');a=ctx.read(OLD+'/global/REFINEMENT_441_865_NORMAL.json')
 n=F(180);M=F(11,19);al,kl,ell=F(77,250),F(87,250),F(9999,10000)
 for cond,name in [((1+8*al)**2<12,'radial scalar'),((9+4*kl)**2<108,'moment scalar'),
  (M/(al*n*n)<1-ell*ell,'radial mean'),(al*(1+ell)>2/CR,'radial coefficient'),
  (CR*M/n<F(103,1000)**2,'point radius'),(M/(1-CR*M/n)<EMAX,'global energy'),
  (F(2,3)*(4/kl+2*CR/3)*M<OP*OP,'operator error'),
  (RAW[0]==F(3,8)*CR*(F(1,3)+OP/n)*(2+F(103,1000))**2+F(3,8)*CR,'raw A'),
  (RAW[1]==F(9,4)/kl,'raw B'),(RAW[2]**2>F(81,16)*2*CR/(3*kl),'raw J'),
  ((CM-RAW[0])*(CM-RAW[1])>RAW[2]**2/4 and CM>max(RAW[:2]),'moment PSD')]:
  ctx.require(cond,name)
 K,eta,cap=F(441,100),F(8,25),F(173,200)
 bb,kk=F(577351,10**6),F(348075,10**6)
 ctx.require(3*bb*bb>1 and (9+4*kk)**2<108,'scalar directed constants')
 h0,h1=down(cap,10**12),up(cap,10**12)
 cover=4*(1-h1)*(F(3,4)+kk*h1)/(9*(h1+bb)**2)
 member=(h0-bb)**2*(F(3,4)+kk*h0)/(1+h1)
 ratio=2/(1+down(1-F(3,4)*eta*eta,10**12))
 dis=2/(1+down(1-eta*eta/2,10**12))
 ctx.require(ratio*K*EMAX/n<cover and dis*K*EMAX/n<F(1,50),'all-column coverage and disjointness')
 ctx.require(member>0 and 4*K/member<255<264,'same-partition scatter')
 eq(ctx,a,dict(K=K,eta=eta,cap=cap,membership_lower=member,coverage_right=cover,
   coverage_left=ratio*K*EMAX/n,disjointness_left=dis*K*EMAX/n,scatter_upper=4*K/member),'new anchors')
 potentials=[]
 for key,mass,countlimit in [('rows',M,F(5)),('odd_rows',F(1,2),F(19,4))]:
  rows=d[key];ctx.require(len(rows)==256,'fixed closed global cover')
  for j,r in enumerate(rows):
   lo,hi=mass*j/256,mass*(j+1)/256;rad=up(CR*hi/n,10**12)
   lam=n/4-up(F(3,4)*CM*hi,10**12)
   ctx.require(rad<1 and lam>0,'global cell denominator')
   en=min(mass/(1-CR*mass/n),(mass-lo)/(1-rad)**2)
   eq(ctx,r,dict(index=j,zlo=lo,zhi=hi,radial_upper=rad,lambda_lower=lam,energy_upper=en),'global closed cell')
   pot=n/(K*lam)+(24/eta**2+48)*en/lam**2
   ctx.require(pot<1,'actual anchor probability potential')
   count=up(CM*hi,10**12)+F(13,10)*264*en/n
   ctx.require(count*count<countlimit,'integer profile exclusion')
   if key=='rows':potentials.append(pot)
 eq(ctx,a['anchor_potential'],max(potentials),'anchor exact maximum')
 return dict(global_closed_bins=512,anchor_potential=str(max(potentials)))

def uniform(ctx):
 d=ctx.read(OLD+'/fine/SEED_NORMAL.json');n=F(180);M=F(11,19)
 E=min(EMAX,energy(n,M,M,M));eq(ctx,d['energy_used'],E,'uniform energy')
 p,pp=F(1,4)-F(3,2)/n,F(1,4)+F(3,2)/n
 c=F(264);bb,kk=F(577351,10**6),F(348075,10**6)
 ctx.require(len(d['rows'])==9,'fixed finite seed stages')
 for r in d['rows']:
  S=c*E/n;q=down(1-S/(p*n));T=2*S/(1+q)
  ctx.require(q>0,'uniform mean guard')
  sh=shared(n,c,q,p,M,M,M,E,128);hw=down(1-S/2);hc=up((F(2,3)+sh['cross'])/2)
  ctx.require(hw>bb and hc<1,'uniform overlap guards')
  kw=floor((hw-bb)**2*(F(3,4)+kk*hw)/(4*(1+hw)))
  kc=floor((1-hc)*(F(3,4)+kk*hc)/(4*(hc+bb)**2))
  mu=floor(2*(F(1,3)-(OP+S)/n-pp*T/(2*(1+q))));beta=2*p*kw+mu*kc
  ctx.require(min(kw,kc,mu,beta)>0,'uniform covariance guards')
  nxt=F(r['next']);eq(ctx,r,dict(c=c,S=S,q=q,T=T,hw=hw,hc=hc,kw=kw,kc=kc,mu=mu,beta=beta,shared=sh),'fixed seed stage')
  if r.get('terminal'):
   ctx.require(c==31 and nxt>=c,'seed terminal record')
  else:
   ctx.require(nxt<c and beta>1/nxt,'certified forward implication');c=nxt
 ctx.require(c==31 and d['seed']==31,'global fine seed31')

def verify(ctx):
 result=global_entry(ctx);uniform(ctx)
 saved=ctx.read(OLD+'/local/PROFILE_180.json')
 ctx.require(len(saved['profiles'])==4 and {p['profile'] for p in saved['profiles']}==set(PROFILES),'four distinct required profile records')
 facts={};nregions=excluded=covered=0
 for p in saved['profiles']:
  name=p['profile'];M,C,mc,L1,ints,den=PROFILES[name];delta=[F(x,den) for x in ints]
  eq(ctx,p,dict(M=M,count2=C,maxcount=mc,L1=L1,N0=180,bins=60),'profile definition')
  facts[(name,180)]=candidate(ctx,p['candidate']['polar_bounds'],180,C,mc,delta)
  got=set();excluded_set=set();covered_set=set()
  for row in p['rows']:
   i,j=row['u_index'],row['w_index'];ctx.require(i not in got and 0<=j<60-i,'unique local strip');got.add(i)
   eq(ctx,row,dict(ulo=M*i/60,uhi=M*(i+1)/60,wlo=M*j/60,whi=M*(j+1)/60,dominated_cells=j+1),'local region')
   eq(ctx,row['count_upper'],count_box(M,i,j),'top-cell count envelope')
   ctx.require([a[0] for a in row['excluded_above']]==list(range(59-i,j,-1)),'entire excluded upper strip')
   for k,bound in row['excluded_above']:
    q=count_box(M,i,k);eq(ctx,bound,q,'rederived count exclusion');ctx.require(q*q<C,'strict exclusion');excluded_set.add((i,k))
   covered_set.update((i,k) for k in range(j+1));fine(ctx,row,p);nregions+=1
  for row in p['fully_excluded_rows']:
   i=row['u_index'];ctx.require(i not in got and 0<=i<60,'disjoint full exclusion');got.add(i)
   ctx.require([a[0] for a in row['excluded']]==list(range(59-i,-1,-1)),'entire excluded strip')
   for k,bound in row['excluded']:
    q=count_box(M,i,k);eq(ctx,bound,q,'rederived full count exclusion');ctx.require(q*q<C,'strict full exclusion');excluded_set.add((i,k))
  ctx.require(got==set(range(60)) and not covered_set&excluded_set and
   covered_set|excluded_set=={(i,j) for i in range(60) for j in range(60-i)},'closed triangular mathematical coverage')
  ctx.require(len(excluded_set)==p['excluded_cells'] and len(covered_set)==p['dominated_cells'],'coverage counts')
  excluded+=len(excluded_set);covered+=len(covered_set)
 frozen=ctx.read(NEW+'/local/FROZEN_FULL_182.json');M,C,mc,L1,ints,den=PROFILES['r2_1']
 facts[('r2_1',182)]=candidate(ctx,frozen['candidate']['polar_bounds'],182,C,mc,[F(x,den) for x in ints])
 ctx.require((nregions,excluded,covered)==(228,2039,5281),'adopted complete main cover')
 ctx.facts['global']=dict(polar=facts,regional_fine_verified=True,count_verified=True)
 result.update(local_regions=nregions,excluded_cells=excluded,covered_cells=covered,
  closed_cells=excluded+covered,polar_profiles_verified=5,
  scope='Recomputed fixed global/fine/count/polar arithmetic and guards; no search')
 return result
