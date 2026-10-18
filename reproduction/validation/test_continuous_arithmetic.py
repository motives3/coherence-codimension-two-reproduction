"""New synthetic regressions for the independent acceptance arithmetic.

These tests do not read certificates, run historical code, or search domains.
"""
import ast
import unittest
from fractions import Fraction as F
from math import comb
import continuous_arithmetic as c


def point(poly,x):
    return sum((a*x**i for i,a in enumerate(poly)),F(0))


def exact_expression(source,x,t):
    def visit(n):
        if isinstance(n,ast.Expression):return visit(n.body)
        if isinstance(n,ast.Constant):return F(n.value)
        if isinstance(n,ast.Name):return {'x':x,'t':t}[n.id]
        if isinstance(n,ast.UnaryOp):return -visit(n.operand) if isinstance(n.op,ast.USub) else visit(n.operand)
        a,b=visit(n.left),visit(n.right)
        if isinstance(n.op,ast.Add):return a+b
        if isinstance(n.op,ast.Sub):return a-b
        if isinstance(n.op,ast.Mult):return a*b
        if isinstance(n.op,ast.Div):return a/b
        if isinstance(n.op,ast.Pow):return a**int(b)
        raise ValueError('unsupported test formula')
    return visit(ast.parse(source,mode='eval'))


class ArithmeticTests(unittest.TestCase):
    def test_signed_interval_corners(self):
        pairs=[(F(-7,13),F(4,9)),(F(1,7),F(5,8)),(F(-5,3),F(-1,11))]
        for a,b in pairs:
            A=c.Interval(a,b)
            self.assertLessEqual(A.lo,a);self.assertGreaterEqual(A.hi,b)
            for d,e in pairs:
                B=c.Interval(d,e)
                for result,values in [(A+B,[x+y for x in (a,b) for y in (d,e)]),
                                      (A*B,[x*y for x in (a,b) for y in (d,e)])]:
                    self.assertLessEqual(result.lo,min(values));self.assertGreaterEqual(result.hi,max(values))
                if d*e>0:
                    result=A/B;values=[x/y for x in (a,b) for y in (d,e)]
                    self.assertLessEqual(result.lo,min(values));self.assertGreaterEqual(result.hi,max(values))

    def test_square_root_directed_witnesses(self):
        for x in (F(0),F(1,9),F(2),F(3),F(81,4)):
            out=c.Interval(x).sqrt()
            self.assertLessEqual(out.lo*out.lo,x);self.assertGreaterEqual(out.hi*out.hi,x)
        with self.assertRaises(ValueError):c.Interval(-1,2).sqrt()
        with self.assertRaises(ValueError):c.Interval(1)/c.Interval(-1,1)
        with self.assertRaises(ValueError):c.ExactInterval(1)/c.ExactInterval(0,1)

    def test_exact_interval_negative_denominator(self):
        out=c.ExactInterval(-2,3)/c.ExactInterval(-5,-2)
        self.assertEqual((out.lo,out.hi),(F(-3,2),F(1)))

    def test_closed_cover_rejects_gap_and_overlap(self):
        class Ctx:
            @staticmethod
            def require(ok,label):
                if not ok:raise ValueError(label)
        good=[{'xlo':'0','xhi':'1/2'},{'xlo':'1/2','xhi':'1'}]
        c.closed(Ctx(),good,F(0),F(1),'test')
        for midpoint in ('1/3','2/3'):
            bad=[good[0],{'xlo':midpoint,'xhi':'1'}]
            with self.assertRaises(ValueError):c.closed(Ctx(),bad,F(0),F(1),'test')

    def test_bernstein_reconstructs_polynomial(self):
        power=[F(2,7),F(-3),F(5,9),F(0),F(-8,11),F(1),F(4,13)]
        a,b=F(3,16),F(5,16);bs=c.bernstein(power,a,b);n=len(bs)-1
        for s in (F(0),F(1,7),F(2,3),F(1)):
            reconstructed=sum((bs[k]*comb(n,k)*s**k*(1-s)**(n-k) for k in range(n+1)),F(0))
            self.assertEqual(reconstructed,point(power,a+(b-a)*s))

    def test_partial_polynomial_product_identity(self):
        for z in (F(1,19),F(3,5),F(7,4)):
            for alpha in (F(1,4),F(1,2),F(1)):
                power,c3=c.partial_power(z,alpha)
                for t in (F(0),F(2,7),F(4,5),F(1)):
                    A=1-t*t
                    H=A*(5*t*t-1)/8+3*z*t*A*A/8+z*z*A**3/16
                    U=A*A/8+(t-t**3)/(2*z)-c3/z
                    self.assertEqual(point(power,t),alpha*H+(1-alpha)*U)

    def test_sharp_formulas_match_generic_projector(self):
        # Rational points obtained from lines through (x,t)=(1/2,1)
        # on 8*x*x+t*t=3. The near-zero point is inside the saved domain.
        for k in (F(5),F(153,28)):
            s=-(2*k+8)/(k*k+8);x=abs(F(1,2)+s);t=abs(1+k*s)
            self.assertEqual(8*x*x+t*t,3)
            lam=(1+t)/4;p=[F(1,4)-x/2]*2+[F(1,4)+x/2]*2
            ell=[(1-lam-v)/((1-lam)*(lam-2*v)) for v in p]
            diag=[ell[a]*(1-ell[a]*(lam-p[a])) for a in range(4)];tr=sum(diag)
            t2=[diag[a]**2+sum((ell[a]**2*ell[b]**2*p[a]*p[b] for b in range(4) if a!=b),F(0)) for a in range(4)]
            radii=[(3*lam-2+2*v)/(6*v*(2*lam-1)) for v in p]
            norms=[2*t2[a]/(p[a]*tr*tr) for a in range(4)]
            for key,(a,b) in {'aa':(0,1),'ab':(0,2),'ba':(2,0),'bb':(2,3),'same_a':(0,0),'same_b':(2,2)}.items():
                stress=diag[a]/(p[a]*tr) if a==b else ell[a]*ell[b]/tr
                m2=norms[b]-stress*stress/radii[a];q=m2/(stress*stress)
                self.assertEqual(exact_expression(c.SHARP[key][0],x,t),m2)
                self.assertEqual(exact_expression(c.SHARP[key][1],x,t),q)


if __name__=='__main__':unittest.main()
