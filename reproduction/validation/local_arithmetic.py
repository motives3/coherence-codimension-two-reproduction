"""Independent reconstruction of the adopted local inequalities.

Only Python's standard library is used.  Historical files are JSON inputs;
no historical Python module is imported or executed.  Every saved local
coefficient is reconstructed from its proved input interfaces before it
can be used as a conservative bound.  The continuous and global interfaces
are independently checked by the other modules of this verifier.
"""
from fractions import Fraction as F
from math import isqrt

UNIT = 10**15
OLD = "research/codim2_below200_20261017"
NEW = "research/codim2_residue2_20261018"


def down(x):
    x = F(x)
    return F((x.numerator*UNIT)//x.denominator, UNIT)


def up(x):
    return -down(-F(x))


def sqrt_down(x):
    x = F(x)
    if x < 0:
        raise ValueError("negative rational radicand")
    return F(isqrt(x.numerator*UNIT*UNIT//x.denominator), UNIT)


def sqrt_up(x):
    a = sqrt_down(x)
    return a if a*a == F(x) else a+F(1, UNIT)


class Bound:
    """Rational endpoint intervals, rounded outward after each operation."""
    __slots__ = ("low", "high")

    def __init__(self, value=0, high=None):
        if isinstance(value, Bound):
            self.low, self.high = value.low, value.high
        else:
            self.low = down(value)
            self.high = up(value if high is None else high)
        if self.low > self.high:
            raise ValueError("reversed interval")

    def __add__(self, other):
        b = Bound(other)
        return Bound(self.low+b.low, self.high+b.high)

    __radd__ = __add__

    def __neg__(self):
        return Bound(-self.high, -self.low)

    def __sub__(self, other):
        return self + (-Bound(other))

    def __rsub__(self, other):
        return Bound(other) + (-self)

    def __mul__(self, other):
        b = Bound(other)
        products = [a*c for a in (self.low, self.high)
                    for c in (b.low, b.high)]
        return Bound(min(products), max(products))

    __rmul__ = __mul__

    def __truediv__(self, other):
        b = Bound(other)
        if b.low <= 0 <= b.high:
            raise ValueError("interval denominator contains zero")
        quotients = [a/c for a in (self.low, self.high)
                     for c in (b.low, b.high)]
        return Bound(min(quotients), max(quotients))

    def __rtruediv__(self, other):
        return Bound(other)/self

    def __pow__(self, n):
        if not isinstance(n, int) or n < 0:
            raise ValueError("nonnegative integral power required")
        answer = Bound(1)
        for _ in range(n):
            answer = answer*self
        return answer

    def root(self):
        return Bound(sqrt_down(self.low), sqrt_up(self.high))


def endpoint(record, upper=True):
    return F(record[1 if upper else 0] if isinstance(record, list) else record)


def serial(value):
    if isinstance(value, F):
        return str(value)
    if isinstance(value, Bound):
        return [str(value.low), str(value.high)]
    if isinstance(value, dict):
        return {k: serial(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [serial(v) for v in value]
    return value


def same(ctx, actual, saved, label):
    """Compare a reconstructed coefficient, not a saved success flag."""
    if isinstance(actual, Bound):
        ctx.require(isinstance(saved, list) and len(saved) == 2, label+": interval shape")
        ctx.require(actual.low == F(saved[0]) and actual.high == F(saved[1]),
                    label+": reconstructed interval "+str(serial(actual))+" != "+str(saved))
    elif isinstance(actual, F):
        ctx.require(actual == F(saved), label+": reconstructed rational")
    else:
        ctx.require(actual == saved, label+": reconstructed value")


def dictionary(ctx, actual, saved, label):
    for key, value in actual.items():
        if isinstance(value, (F, Bound)):
            same(ctx, value, saved[key], label+"."+key)


def projection_gap(b, b_squared, phase):
    defect = phase*phase+3*(b+phase)**2
    return ((2/sqrt_up(3))*(1-defect)
            -(4/sqrt_down(3))*(b+b_squared)), defect


def physical_normal(ctx, C, N, total, eta, e, perturbation):
    mass = 1-4*e
    b2 = (total+F(400, 109))*C/N**2
    b = sqrt_up(b2)
    ref, defect = projection_gap(b, b2, eta)
    gm = ref-perturbation
    ctx.require(mass > 0 and defect < 1 and gm > 0, "physical normal reference domain")
    t = min(sqrt_up(2*eta*eta), sqrt_up(2*total*C/(N*N*mass)))
    a = min(1/sqrt_down(mass), 1+t)
    jr = ((F(1, 2)+b)/sqrt_down(3)+F(7, 8)*t+perturbation*a/2)/sqrt_down(mass)
    lr = 1/(2*sqrt_down(3))+F(7, 4)*t+F(7, 8)*t*t+perturbation*a*a/2
    ambient = (F(7, 4)+perturbation)/(2*mass)
    return dict(B=b, B_squared=b2, b_squared=defect, n=sqrt_up(2*b2),
                gm=gm, cm=gm/(2*(1+4*e)), t=t, mean_normal_radius=a,
                J=min(jr, ambient), L=min(lr, ambient),
                J_raw=jr, L_raw=lr, ambient=ambient)


def mass_gap(ctx, C, N, total, eta, e, tp, kap, tau):
    w = 1-4*e
    b2 = total*C/(N*N*w)
    b = sqrt_up(b2)
    ref, defect = projection_gap(b, b2, eta)
    alpha = (1+sqrt_up(3))/4
    parameter = (1+2/w)*tp+kap/2+2*(alpha*kap+tau)/w
    weight = 8*alpha*e/w
    gm = ref-parameter-weight
    ctx.require(w > 0 and defect < 1 and gm > 0, "mass mean complete positivity")
    return dict(Bg=b, Bg_squared=b2, bg_squared=defect, reference_gap=ref,
                parameter=parameter, weight=weight, gm=gm, cm=w*gm/2)


def stress_gap(ctx, C, N, total, eta, e, hc, kap, tau):
    ctx.require(0 <= e < F(1, 4) and 0 <= kap < F(1, 32)
                and 0 <= eta < F(1, 32) and 0 < hc <= F(15, 26),
                "stress coordinates original domain")
    w = 1-4*e
    root_error = kap/(1+sqrt_down(1-kap))
    etav = sqrt_up(1+kap)*eta+root_error
    bv = (sqrt_up(total*C/N**2)+root_error)/sqrt_down(w)
    phase_defect = kap*(1+eta)/sqrt_down(1-kap)
    phase = etav+phase_defect
    ref, defect = projection_gap(bv, bv*bv, phase)
    dv = 2*etav+etav*etav
    pair = F(7, 6)*dv/hc**2+etav*(2+etav)/hc+dv/(2*hc)
    parameter = (1+2/w)*pair+2*tau/w
    weight = 8*((1+sqrt_up(3))/4)*e/w
    gm = ref-parameter-weight
    ctx.require(etav < F(1, 32) and defect < 1 and gm > 0,
                "stress coordinates transformed domain and complete positivity")
    return dict(cm=w*(1-kap)*gm/2, gm=gm, mass=w, metric_lower=w*(1-kap),
                root_error=root_error, eta_v=etav, Bv=bv,
                phase_defect=phase_defect, phase_reference=phase,
                projected_fraction=defect, reference_gap=ref, dp_v=dv,
                pair_perturbation=pair, parameter=parameter, weight=weight)


def finite_normal(ctx, cm, cr, J, L, radius2):
    ctx.require(cm > 0 and cr > 0 and J >= 0 and L >= 0
                and 0 <= radius2 <= F(1, 2), "finite physical normal domain")
    delta = cm-cr
    if delta > 0 and J*J*radius2 <= delta*delta*(1-radius2):
        upper = -cr+(cr+L+J*J/delta)*radius2
        branch = "interior"
    else:
        upper = -cm+(cm+L)*radius2+2*J*sqrt_up(radius2*(1-radius2))
        branch = "boundary"
    return dict(upper=upper, gap=-upper, branch=branch, rho_squared=radius2,
                mixed=J, pure=L)


def candidate(ctx, profile, include_stress):
    N, C, mc = profile["N0"], F(profile["count2"]), F(profile["maxcount"])
    saved = profile["candidate"]
    polar = saved["polar_bounds"]
    total, point = F(polar["total"]), F(polar["point"])
    # The global verifier independently reconstructs both polar coefficients.
    verified_polar = ctx.facts["global"]["polar"][(profile["profile"], N)]
    same(ctx, F(verified_polar["total"]), total, "independent aggregate polar interface")
    same(ctx, F(verified_polar["point"]), point, "independent point polar interface")
    ctx.require(total > 0 and point > 0, "positive certified polar coefficients")
    e, sig = Bound(mc/N), Bound(C/N**2)
    eta_coefficient = Bound(point*C).root().high
    eta = Bound(eta_coefficient/N)
    k0 = (4*Bound(C)*(F(1, 3)+4*e/F(109, 100)+4*sig/F(109, 100)**2)).root()
    k0 = k0+2*N*e**2/(F(1, 15)-e)
    kap = Bound(k0.high/N)
    tau = F(2, 3)*sig
    cont = ctx.facts["continuous"]["by_endpoint"][N][profile["profile"]]
    for name in ("cK", "transverse", "lambda_lower"):
        same(ctx, F(cont[name]), saved["intrinsic"][name], "continuous "+name)
    dp = 2*eta+eta**2+kap*(1+eta)**2
    hc = Bound(max((F(15, 26)-dp).low, F(cont["cross_lower"])))
    upair = eta+kap*(1+eta)
    ctx.require(hc.low > 0 and hc.high <= F(15, 26), "positive cross endpoint floor")
    tp = F(7, 6)*dp/hc**2+upair*(2+upair)/hc+dp/(2*hc)+kap/2
    crossweights = {F(3, 4):(2, 3), F(11, 4):(6, 15), F(1):(4, 4), F(3):(4, 12)}
    lin, quad = crossweights[C]
    wcross = Bound(F(lin, N)+F(quad, N*N))
    wdiag = 8*e+16*e**2
    ambient = ((1+4*e)**2*(3*tp+kap/2)+F(27, 4)*wcross+wdiag/2
               +2*((1+4*e)*((F(7, 10)+tau)*kap+tau)+F(14, 5)*e))
    normal = physical_normal(ctx, C, N, total, eta.high, e.high, ambient.high)
    mass = mass_gap(ctx, C, N, total, eta.high, e.high, tp.high, kap.high, tau.high)
    means = [normal["cm"], mass["cm"]]
    stress = None
    if include_stress:
        stress = stress_gap(ctx, C, N, total, eta.high, e.high, hc.low, kap.high, tau.high)
        means.append(stress["cm"])
    cm = Bound(max(means))
    cr_interval = (1-kap)*F(cont["cK"])
    cr = Bound(cr_interval.low)
    same(ctx, eta_coefficient, saved["eta_coefficient"], "candidate eta numerator")
    same(ctx, k0.high, saved["kappa_coefficient"], "candidate stress numerator")
    same(ctx, cm, saved["cm"], "candidate reconstructed mean gap")
    same(ctx, cr, saved["cr"], "candidate pointwise intrinsic residual")
    dictionary(ctx, mass, saved["mass_mean"], "candidate mass coordinates")
    if stress is not None:
        dictionary(ctx, stress, saved["stress_mean"], "candidate stress coordinates")
    ctx.require(mc/N <= F(1, 120) and eta.high < F(1, 32)
                and kap.high < F(1, 32), "candidate local domain")
    return dict(N=N, C=C, mc=mc, total=total, point=point,
                eta_coefficient=eta_coefficient, eta=eta, k0=k0.high, kap=kap,
                tau=tau, e=e, pm=F(1, 4)-e, pp=F(1, 4)+e, hc=hc,
                ambient=ambient, normal=normal, mass=mass, stress=stress,
                cm=cm, cr=cr, continuous=cont, cK=F(cont["cK"]))


def regional_inputs(ctx, cand, profile, raw):
    N, C = cand["N"], cand["C"]
    U, W = F(raw["uhi"]), F(raw["whi"])
    fine = raw["fine"]
    LU, LP = (F(fine["interface"][x]) for x in ("unit_total", "unit_point"))
    E = F(fine["E_upper"])
    s = Bound(F(13, 4)*U/N).root()
    factor = (1+s)/(1-s)**2
    total = F(13, 4)*Bound(U)+(LU*W)*factor
    point = F(13, 4)*Bound(U)+(LP*W)*factor
    dc = (total.root()+Bound(cand["total"]*C).root()).high
    L1 = F(profile["L1"])
    denom = F(2, 3)-L1/N
    rot2 = Bound(4*dc*dc)/(N*N*denom)
    ctx.require(denom > 0 and rot2.high < 1-F(255, 256)**2,
                "actual closest gauge rotation domain")
    oldrot = (F(512, 511)*Bound(4*dc*dc)/denom).root().high
    eps = (point/N).root()+Bound((oldrot+cand["eta_coefficient"])/N)
    radial_error = F(4, 11)*cand["e"]/(1-4*cand["e"])
    rplus = (1+radial_error).root()
    rmin2 = 1-radial_error
    rmin = rmin2.root()
    angle = Bound(LU*E).root()+(Bound(cand["total"]*C)/rmin).root()
    chi = ((1+s)*rplus/((1-s)*rmin)).root()
    angle_su2 = (1+chi)**2*angle**2/(N*N*denom)
    ctx.require(angle_su2.high < 1-F(255, 256)**2, "angular closest gauge domain")
    angle_rot = (F(512, 511)*(1+chi)**2*angle**2/denom).root().high
    rotation = min(oldrot, angle_rot)
    rawT = (1+s)*(Bound(LP*E/N).root()+Bound(rotation/N)
                 +(Bound(cand["eta_coefficient"])/rmin.root())/N)
    T = Bound(min(eps.high, rawT.high))
    tqc = ((1+s)*(rplus/rmin).root()*angle).high
    qt = Bound(min(dc, tqc)/N)
    ctx.require(T.high < (1-s).low, "positive physical radial multipliers")
    rho = (((1-s)**2-T**2).root()/rplus).low
    R = ((1+s)/rmin).high
    ctx.require(rho > 0 and R >= 1, "physical radial interval")
    return dict(U=U, W=W, LU=LU, LP=LP, E=E, s=s, total=total, point=point,
                dc=dc, oldrot=oldrot, eps=eps, rplus=rplus, rmin2=rmin2,
                rmin=rmin, angle=angle, chi=chi, angle_su2=angle_su2,
                angle_rot=angle_rot, rotation=rotation, T=T, qt=qt,
                tqc=tqc, rho=rho, R=R)


def gamma(eta, kap, rmin, hc, hs):
    geometric = (1/sqrt_down(3)+2*eta+eta*eta)/(rmin*rmin)
    gc, gs = kap+min(F(1), geometric), 1+kap
    jc, js = gc*gc/(2*hc), gs*gs/(2*hs)
    return dict(cross=gc, same=gs, geometric=geometric,
                Jcross=jc, Jsame=js, Jmax=max(jc, js))


def row_mixed(delta, mc, ms, gc, gs, hc, hs, pm, pp, old):
    iso = (sqrt_up(pp)+sqrt_up(1-pm)*delta)**2/hc
    point = (1-pm)*mc*mc/hc
    crossH = min(iso, point)
    cross = sqrt_up(3)*gc*sqrt_up(crossH/hc)/2
    same_term = sqrt_up(pp)*ms*gs/hs
    return dict(Hisotropy=iso, Hpoint=point, Hcross=crossH,
                Lcross_row=cross, Lsame_row=same_term,
                Lrow=cross+same_term, Lmixed=min(cross+same_term, old))


def unsigned(ctx, cand, region, geometry=None):
    eta, kap, hc = cand["eta"], cand["kap"], cand["hc"]
    rplus, rmin, rmin2 = region["rplus"], region["rmin"], region["rmin2"]
    T, qt = region["T"], region["qt"]
    rho, R = Bound(region["rho"]), Bound(region["R"])
    he = F(15, 26)-2*eta-eta**2
    ctx.require(he.low > 0, "Euclidean cross floor")
    mc = (rplus**2-he**2/rplus**2).root()+kap*rplus
    ms = kap*rplus
    if geometry:
        mc = Bound(min(mc.high, Bound(F(geometry["cross_m2_upper"])).root().high))
        ms = Bound(min(ms.high, Bound(F(geometry["same_m2_upper"])).root().high))
    hs = Bound(max(((1-kap)*rmin2).low, F(cand["continuous"]["same_lower"])))
    ctx.require(hs.low > F(15, 26) >= hc.high, "same and cross positive floors")
    gam = gamma(eta.high, kap.high, rmin.low, hc.low, hs.low)
    typed = {}
    for name, m, floor in (("cross", mc, hc), ("same", ms, hs)):
        g = Bound(gam[name])
        d = m+g*T/(2*rho)
        z = 2*d*T/(rho*floor)
        c = d**3/(3*Bound(3).root()*floor**2)
        b = d**4/floor**3*(F(1, 18)+z/(36*Bound(3).root()))
        typed[name] = dict(m=m.high, floor=floor.low, D=d.high, zmax=z.high,
                           C=c.high, B=b.high, L=(m*g/floor).high)
    for key in ("C", "B", "L"):
        ctx.require(typed["cross"][key] >= typed["same"][key], "unsigned typed order "+key)
    pm, pp = cand["pm"], cand["pp"]
    mixweight = F(3, 2)*pp.root()
    ctx.require(mixweight.high < 1, "four-type positive mixing weights")

    def weights(key):
        x, y = (Bound(typed[t][key]) for t in ("cross", "same"))
        return (1-pm)*x+pm*y, mixweight*x+(1-mixweight)*y

    ce, cmix = weights("C")
    be, bmix = weights("B")
    _, lmix = weights("L")
    bp = (3*Bound(typed["cross"]["B"])+Bound(typed["same"]["B"]))/4
    cubic = 2*R/rho**2*ce*T+6*cmix*qt/rho
    quartic = 2*R/rho**3*be*T**2+8*bmix*T*qt/rho**2+6*bp*qt**2/rho**2
    dg = 2*eta+eta**2+kap*rplus**2
    delta = (eta+kap*rplus+eta/rmin.root()
             +Bound(F(2, 3)).root()*dg/(hc*(1/Bound(3).root())).root())
    row = row_mixed(delta.high, typed["cross"]["m"], typed["same"]["m"],
                    gam["cross"], gam["same"], hc.low, hs.low, pm.low, pp.high, lmix.high)
    mixed = 2*Bound(row["Lmixed"])*qt/rho+Bound(gam["Jmax"])*qt**2/rho**2
    M = max(typed[t]["m"]**2/typed[t]["floor"] for t in typed)
    H = ((pp.root()+(1-pm).root()*delta)**2/hc
         +pp*(kap*rplus)**2/hs)
    H = Bound(min(H.high, M))
    MI = Bound(M)
    radial = (H*T+(MI*H).root()*qt)/(rho*rmin)
    a = cubic+mixed+quartic
    loss = (a+(a**2+radial**2).root())/2
    return dict(types=typed, gammas=gam, row_mixed=row, row_transport_delta=delta,
                row_isotropy_H=H, row_pair_M=MI, angular_cubic=cubic,
                angular_mixed=mixed, angular_quartic=quartic, angular_A=a,
                radial_B=radial, loss=loss, T=T, qt=qt,
                radial_lower=region["rho"], radial_upper=region["R"])


def audit_row(ctx, cand, profile, raw, saved, geometry=None):
    inputs = regional_inputs(ctx, cand, profile, raw)
    for name, value in (("total", inputs["total"]), ("point", inputs["point"]),
                        ("d_coefficient", inputs["dc"]), ("rotation", inputs["oldrot"]),
                        ("epsilon", inputs["eps"]), ("candidate_radius", inputs["rplus"])):
        same(ctx, value, saved[name], "region "+name)
    dictionary(ctx, cand["normal"], saved["mean_normal_bounds"], "physical normal")
    dictionary(ctx, cand["mass"], saved["mass_conjugated_mean"], "physical mass mean")
    same(ctx, cand["ambient"], saved["hessian_perturbation"], "ambient mean perturbation")
    normal = finite_normal(ctx, cand["cm"].low, cand["cr"].low,
                           cand["normal"]["J"], cand["normal"]["L"],
                           inputs["dc"]**2/(2*cand["N"]**2))
    dictionary(ctx, normal, saved["normal_result"], "finite normal")
    same(ctx, normal["branch"], saved["normal_result"]["branch"], "finite normal branch")
    tail = unsigned(ctx, cand, inputs, geometry)
    rt = saved["radial_tangent"]
    for key in ("loss", "angular_cubic", "angular_mixed", "angular_quartic",
                "angular_A", "radial_B", "row_transport_delta", "row_isotropy_H",
                "row_pair_M", "radial_lower", "radial_upper"):
        same(ctx, tail[key], rt[key], "complete unsigned "+key)
    for family in ("types",):
        for name, coefficients in tail[family].items():
            dictionary(ctx, coefficients, rt[family][name], "unsigned "+family+"."+name)
    dictionary(ctx, tail["gammas"], rt["gammas"], "complex fiber gamma")
    dictionary(ctx, tail["row_mixed"], rt["row_mixed"], "complete row mixed")
    transfer = dict(tangent_point=inputs["T"], tangent_q=inputs["qt"],
                    tangent_coefficient=inputs["tqc"], angle_B=inputs["angle"],
                    chi=inputs["chi"], angle_rot=inputs["angle_rot"],
                    selected_rot=inputs["rotation"], angle_su2=inputs["angle_su2"])
    dictionary(ctx, transfer, rt, "actual angular transport")
    conservative_margin = (Bound(cand["cr"].low)
                           -Bound(cand["cr"].low-normal["gap"])-tail["loss"])
    same(ctx, conservative_margin, saved["margin"], "complete original unsigned margin")
    return inputs, normal, tail


def stationary(ctx, cand, region, typed, geometry):
    N = cand["N"]
    eta, kap = cand["eta_coefficient"]/N, cand["k0"]/N
    e = cand["mc"]/N
    pm, pp = F(1, 4)-e, F(1, 4)+e
    rmin = sqrt_down(1-F(4, 11)*e/(1-4*e))
    rplus = region["rplus"].high
    mc, ms = typed["cross"]["m"], typed["same"]["m"]
    hc, hs = typed["cross"]["floor"], typed["same"]["floor"]
    dg = 2*eta+eta*eta+kap*rplus*rplus
    qlo = max(F(0), (1-kap)**2*rmin*rmin/(1/sqrt_down(3)+dg)**2-1/(rmin*rmin))
    qhi = min(mc*mc/(hc*hc), (1+kap)**2*rplus*rplus/(hc*hc)-1/(rplus*rplus))
    qs = ms*ms/(hs*hs)
    qlo, qhi, qs = max(qlo, geometry["cross_q_lower"]), min(qhi, geometry["cross_q_upper"]), min(qs, geometry["same_q_upper"])
    ctx.require(0 <= qlo <= qhi and qs >= 0, "intersection of complete physical fiber ratios")
    a3 = (1-pm)*mc**3/(hc*hc)+pp*ms**3/(hs*hs)
    options = []
    for c in (F(2), (qlo+qhi)/2):
        stress = c*F(7, 10)*min(kap*rplus, ms)
        cross = (1-pm)*max(abs(qlo-c), abs(qhi-c))*mc
        same_term = pp*max(c, abs(qs-c))*ms
        a1 = stress+cross+same_term
        options.append(dict(center=c, stationarity=stress, cross_deviation=cross,
                            same_deviation=same_term, A1=a1, A3=a3, Prow=(a1+a3)/8))
    best = min(options, key=lambda x:x["Prow"]).copy()
    best["Prow"] = min(best["Prow"], geometry["Prow_upper"])
    return dict(qlo=qlo, qhi=qhi, qsame=qs, candidates=options, selected=best)


def signed_choice(ctx, cand, region, normal, typed, gammas, mixed, radial,
                  geometry, weight, saved, oldloss):
    N, e = cand["N"], cand["mc"]/cand["N"]
    pm, pp = F(1, 4)-e, F(1, 4)+e
    rho, R, T, qt = region["rho"], region["R"], region["T"].high, region["qt"].high
    qd = region["dc"]/N
    rmin = sqrt_down(1-F(4, 11)*e/(1-4*e))
    values = {}
    for name in ("cross", "same"):
        m, h = typed[name]["m"], typed[name]["floor"]
        g = up(gammas[name])
        v = g*T/(2*rho)
        D = up(m+v)
        Z = up(2*D*T/(rho*h))
        certificate = saved["types"][name]["tail_certificate"]
        same(ctx, Z, certificate["z"], "signed actual scalar radius binding")
        same(ctx, weight, certificate["alpha"], "signed actual weight binding")
        # All coefficients and all 32 Bernstein boxes have been independently
        # checked by the continuous verifier, before this module is called.
        Q = F(certificate["Q"])
        c3 = 1/(3*sqrt_down(3))
        same(ctx, c3, certificate["c3"], "signed scalar cubic cap")
        ctx.require(Z > 0 and Q >= 0, "complete scalar tail positive radius/quartic")
        base = c3*m**3/h**2
        extra = c3*(3*m*m*v+3*m*v*v+v**3)/h**2
        values[name] = dict(D=D, z=Z, Q=Q, Cbase=base,
                            Cextra=extra+(1-weight)*base, Cfull=base+extra,
                            Bsigned=D**4*Q/h**3)
        dictionary(ctx, values[name], saved["types"][name], "complete signed type "+name)
    mixer = F(3, 2)*sqrt_up(pp)
    ctx.require(mixer < 1, "signed positive type weights")

    def weights(key):
        x, y = values["cross"][key], values["same"][key]
        ctx.require(x >= y >= 0, "signed frozen typed order "+key)
        return (1-pm)*x+pm*y, mixer*x+(1-mixer)*y

    ce, _ = weights("Cextra")
    _, cmix = weights("Cfull")
    be, bmix = weights("Bsigned")
    weights("Cbase")
    bp = (3*values["cross"]["Bsigned"]+values["same"]["Bsigned"])/4
    row = stationary(ctx, cand, region, typed, geometry)
    dictionary(ctx, {k:row[k] for k in ("qlo", "qhi", "qsame")}, saved["row"], "signed stationary ratios")
    for got, old in zip(row["candidates"], saved["row"]["candidates"]):
        dictionary(ctx, got, old, "signed nonzero stationary harmonic")
    dictionary(ctx, row["selected"], saved["row"]["selected"], "selected stationary bound")
    cubic = 2*weight*row["selected"]["Prow"]*T/rho**2+2*R*ce*T/rho**2+6*cmix*qt/rho
    quartic = 2*R*be*T*T/rho**3+8*bmix*T*qt/rho**2+6*bp*qt*qt/rho**2
    rms = sqrt_up((1-pm)*values["cross"]["Cbase"]**2+pm*values["same"]["Cbase"]**2)
    radial_weight = 2*weight*rms*T*qd/(rho**2*rmin)
    A, B = cubic+mixed+quartic, radial+radial_weight
    loss = (A+sqrt_up(A*A+B*B))/2
    selected = min(oldloss, loss)
    answer = dict(alpha=weight, signed_margin=normal["gap"]-loss,
                  selected_margin=normal["gap"]-selected, gap=normal["gap"],
                  signed_loss=loss, old_loss=oldloss, cubic=cubic, quartic=quartic,
                  angular_mixed=mixed, radial_weight=radial_weight, A=A, B=B)
    dictionary(ctx, answer, saved, "complete signed alternative")
    same(ctx, "compact_signed" if loss < oldloss else "old_unsigned",
         saved["selected"], "complete bound branch")
    return answer


def refine(ctx, cand, region, normal, tail, saved):
    whole = ctx.facts["continuous"]
    generic, sharp = whole["generic_projected"][182], whole["sharp"][182]
    geometry = {key:(max if key == "cross_q_lower" else min)(F(generic[key]), F(sharp[key]))
                for key in ("cross_m2_upper", "same_m2_upper", "cross_q_lower",
                            "cross_q_upper", "same_q_upper")}
    geometry["Prow_upper"] = F(sharp["Prow_upper"])
    dictionary(ctx, geometry, saved["geometry"], "whole-domain selected geometry")
    typed = {name:dict(value) for name, value in tail["types"].items()}
    for name, key in (("cross", "cross_m2_upper"), ("same", "same_m2_upper")):
        typed[name]["m"] = min(typed[name]["m"], sqrt_up(geometry[key]))
    mc, ms = typed["cross"]["m"], typed["same"]["m"]
    hc, hs = typed["cross"]["floor"], typed["same"]["floor"]
    kap = cand["k0"]/182
    intrinsic = (1-kap)*cand["cK"]
    lam = (1+sqrt_up(3))/4
    spectral = lam*(1+kap)-intrinsic
    ctx.require(lam >= F(1, 4) and (4*lam-1)**2 >= 3,
                "spectral lambda upper covers the full reciprocal domain")
    ctx.require(intrinsic > 0 and spectral >= 0, "physical pointwise spectral row domain")
    H = min(tail["row_isotropy_H"].high, spectral)
    Hc = min(tail["row_mixed"]["Hcross"], spectral)
    M = tail["row_pair_M"].high
    row = dict(Hspectral=spectral, row_H=H, cross_H=Hc, lambda_upper=lam,
               kappa_upper=kap, intrinsic_residual_lower=intrinsic,
               old_row_H=tail["row_isotropy_H"].high, old_cross_H=tail["row_mixed"]["Hcross"])
    dictionary(ctx, row, saved["spectral_row"], "full physical spectral coupling")
    same(ctx, True, saved["spectral_row"]["physical_pointwise_M_unchanged"], "pair coefficient is not a row coefficient")
    gc, gs = tail["gammas"]["cross"], tail["gammas"]["same"]
    pp = F(1, 4)+cand["mc"]/182
    lr = sqrt_up(3)*gc*sqrt_up(Hc/hc)/2+sqrt_up(pp)*ms*gs/hs
    lm = min(tail["row_mixed"]["Lmixed"], lr)
    T, qt, rho = region["T"].high, region["qt"].high, region["rho"]
    e = cand["mc"]/182
    rmin = sqrt_down(1-F(4, 11)*e/(1-4*e))
    mixed = 2*lm*qt/rho+tail["gammas"]["Jmax"]*qt*qt/rho**2
    radial = (H*T+sqrt_up(M*H)*qt)/(rho*rmin)
    ctx.require(mixed <= tail["angular_mixed"].high and radial <= tail["radial_B"].high,
                "both replacements improve complete nonnegative rows")
    dictionary(ctx, dict(cross_m=mc, same_m=ms, Lrow=lr, Lmixed=lm,
                        new_angular_mixed=mixed, new_radial_B=radial,
                        pointwise_M_retained=M), saved, "refined physical rows")
    choices = []
    for weight, record in zip((F(1, 4), F(1, 2), F(3, 4), F(1)), saved["choices"]):
        choices.append(signed_choice(ctx, cand, region, normal, typed, tail["gammas"],
                                     mixed, radial, geometry, weight, record,
                                     tail["loss"].high))
    best = max(choices, key=lambda c:c["selected_margin"])
    # Every adopted region selects this freshly reconstructed complete bound.
    # The earlier diagnostic fallback is not a premise for strictness.
    same(ctx, "new_complete_signed_bound", saved["selected_branch"], "adopted complete branch")
    same(ctx, best["alpha"], saved["selected_alpha"], "adopted complete sign weight")
    same(ctx, best["selected_margin"], saved["margin"], "reconstructed final exact margin")
    same(ctx, down(best["selected_margin"]), saved["margin_lower"], "reconstructed downward margin")
    ctx.require(best["selected_margin"] > F(1, 10000), "strict refined region")
    return down(best["selected_margin"])


def verify(ctx):
    ctx.require(ctx.facts.get("global", {}).get("regional_fine_verified") is True
                and ctx.facts.get("global", {}).get("count_verified") is True,
                "independently verified global/fine/count prerequisites")
    continuous = ctx.facts["continuous"]
    ctx.require(continuous["tails_checked"] == 480, "independently audited all signed scalar certificates")
    source = ctx.read(OLD+"/local/PROFILE_180.json")
    stresses = ctx.read(NEW+"/curvature/STRESS_SAVED_NORMAL.json")
    frozen = ctx.read(NEW+"/local/FROZEN_FULL_182.json")
    refined = ctx.read(NEW+"/local/REFINED_182_NORMAL.json")
    profiles = {p["profile"]:p for p in source["profiles"]}
    selected = []
    worst = None
    summary = {}
    for name in ("odd_3_4", "odd_11_4", "r2_3"):
        profile = profiles[name]
        if name == "r2_3":
            ctx.trace = []
        cand = candidate(ctx, profile, False)
        stress = None
        stress_rows = {}
        if name == "r2_3":
            stress_record = next(p for p in stresses["profiles"] if p["profile"] == name)
            stress = stress_gap(ctx, cand["C"], 180, cand["total"],
                                cand["eta_coefficient"]/180, cand["mc"]/180,
                                cand["hc"].low, cand["k0"]/180, F(2, 3)*cand["C"]/180**2)
            dictionary(ctx, stress, stress_record["stress_mean"], "C3 reconstructed stress mean")
            stress_rows = {(r["u_index"], r["w_index"]):r for r in stress_record["rows"]}
            common_guards = list(ctx.trace)
            ctx.trace = None
        margins = []
        for row in profile["rows"]:
            key = row["u_index"], row["w_index"]
            is_worst = name == "r2_3" and key == (17, 23)
            if is_worst:
                ctx.trace = list(common_guards)
            inputs, normal, tail = audit_row(ctx, cand, profile, row, row)
            if stress is not None:
                chosen_cm = max(cand["cm"].low, stress["cm"])
                normal = finite_normal(ctx, chosen_cm, cand["cr"].low,
                                       cand["normal"]["J"], cand["normal"]["L"],
                                       inputs["dc"]**2/(2*180**2))
                stored = stress_rows[key]
                dictionary(ctx, normal, stored["normal"], "C3 reconstructed adopted normal")
                same(ctx, normal["branch"], stored["normal"]["branch"], "C3 physical normal branch")
                margin = normal["gap"]-tail["loss"].high
                same(ctx, margin, stored["margin"], "C3 complete exact margin")
                if key == (17, 23):
                    worst = dict(profile=name, N=180, u_index=17, w_index=23,
                                 original_source=OLD+"/local/PROFILE_180.json",
                                 adopted_source=NEW+"/curvature/STRESS_SAVED_NORMAL.json",
                                 candidate_inputs=dict(C=cand["C"], maxcount=cand["mc"],
                                     polar_total=cand["total"], polar_point=cand["point"],
                                     eta_coefficient=cand["eta_coefficient"], kappa_coefficient=cand["k0"],
                                     intrinsic_cK=cand["cK"], cross_floor=cand["hc"]),
                                 regional_inputs=inputs, full_stress_mean=stress,
                                 selected_cm=chosen_cm, physical_cr=cand["cr"].low,
                                 ambient_perturbation=cand["ambient"],
                                 full_physical_normal=cand["normal"],
                                 selected_normal=normal, complete_unsigned=tail,
                                 exact_margin=margin, downward_margin=down(margin),
                                 required_margin=F(1, 10000))
            else:
                margin = (Bound(cand["cr"].low)
                          -Bound(cand["cr"].low-normal["gap"])-tail["loss"]).low
            ctx.require(margin > F(1, 10000), "strict adopted "+name+" region "+str(key))
            if is_worst:
                worst["regional_guard_checks"] = list(ctx.trace)
                ctx.trace = None
            margins.append(margin)
            selected.append((name, key, margin))
        summary[name] = dict(regions=len(margins), minimum=str(min(margins)))
    cand = candidate(ctx, frozen, True)
    base_rows = {(r["u_index"], r["w_index"]):r for r in profiles["r2_1"]["rows"]}
    final_rows = {(r["u_index"], r["w_index"]):r for r in refined["rows"]}
    geo = continuous["generic_projected"][182]
    dictionary(ctx, {k:F(geo[k]) for k in ("cross_m2_upper", "same_m2_upper", "cross_q_lower",
                                         "cross_q_upper", "same_q_upper")},
               frozen["candidate"]["exact_geometry"], "base182 independently checked geometry")
    margins = []
    for row in frozen["rows"]:
        key = row["u_index"], row["w_index"]
        inputs, normal, tail = audit_row(ctx, cand, frozen, base_rows[key], row, geo)
        margin = refine(ctx, cand, inputs, normal, tail, final_rows[key])
        margins.append(margin)
        selected.append(("r2_1", key, margin))
    summary["r2_1"] = dict(regions=len(margins), minimum=str(min(margins)))
    ctx.require(len(selected) == 228 and len({(p,k) for p,k,_ in selected}) == 228,
                "all228 adopted regional arithmetic reconstructed")
    ctx.require(worst is not None and worst["exact_margin"] == min(
        x[2] for x in selected if x[0] == "r2_3"), "C3 exact full-cover worst region is17,23")
    ctx.facts["C3_WORST"] = serial(worst)
    ctx.facts["local"] = dict(regions=228, profiles=summary, common_margin="1/10000",
                              independent_arithmetic=True, historical_imports=False)
    return ctx.facts["local"]
