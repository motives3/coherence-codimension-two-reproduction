"""Negative integration regressions for the new verifier, not old searches."""
import sys
sys.dont_write_bytecode = True
from pathlib import Path
import copy
from fractions import Fraction as F
import unittest

BASE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE/'certificate'))
import verify_certificates as cli
import global_arithmetic as glob
import continuous_arithmetic as cont
from readonly_run import readonly

class Checks:
    def __init__(self, parent=None, path=None, mutate=None):
        self.parent, self.path, self.mutate = parent, path, mutate
        self.checks = 0
    def require(self, ok, label):
        self.checks += 1
        if not ok:
            raise cli.AcceptanceError(label)
    def read(self, name):
        result = self.parent.read(name)
        if name == self.path:
            result = copy.deepcopy(result)
            self.mutate(result)
        return result

class RejectionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ctx = cli.Context(BASE/'certificate/supplement.zip', BASE/'certificate/INDEX.json')
    @classmethod
    def tearDownClass(cls):
        cls.ctx.zip.close()

    def test_duplicate_json_key_rejected(self):
        with self.assertRaises(cli.AcceptanceError):
            cli.unique_json('{"margin":"1","margin":"2"}')

    def test_absolute_or_parent_input_rejected(self):
        for path in ['../outside.json', 'C:/outside.json', '/outside.json']:
            with self.subTest(path=path), self.assertRaises(cli.AcceptanceError):
                self.ctx.read(path)

    def test_corrupt_anchor_fraction_rejected(self):
        path = glob.OLD+'/global/REFINEMENT_441_865_NORMAL.json'
        def corrupt(d): d['anchor_potential'] = '0'
        with self.assertRaises(cli.AcceptanceError):
            glob.global_entry(Checks(self.ctx, path, corrupt))

    def test_missing_closed_global_cell_rejected(self):
        path = glob.OLD+'/global/ENTRY_NORMAL.json'
        def corrupt(d): d['rows'].pop(127)
        with self.assertRaises(cli.AcceptanceError):
            glob.global_entry(Checks(self.ctx, path, corrupt))

    def test_cover_gap_and_missing_endpoint_rejected(self):
        for rows in [[dict(xlo='0',xhi='1/3'),dict(xlo='1/2',xhi='1')],
                     [dict(xlo='0',xhi='2/3')]]:
            with self.subTest(rows=rows), self.assertRaises(cli.AcceptanceError):
                cont.closed(Checks(),rows,F(0),F(1),'regression cover')

    def test_corrupt_bernstein_coefficient_rejected(self):
        path = cont.NEW+'/local/REFINED_182_NORMAL.json'
        def corrupt(d):
            box = d['rows'][0]['choices'][0]['types']['cross']['tail_certificate']['boxes'][0]
            box['coefficients'][0] = str(F(box['coefficients'][0])+1)
        with self.assertRaises(cli.AcceptanceError):
            cont.tails(Checks(self.ctx,path,corrupt))

    def test_forged_root_intersection_rejected(self):
        d = self.ctx.read(cont.BAND+'/residual/ROOT_INTRINSIC_NORMAL.json')
        profile = d['profiles'][0]
        row = copy.deepcopy(profile['leaves'][0])
        row['tau_contractions'][0]['rhs'] = ['0','0']
        delta = [row['sign']*x for x in cont.PROFILES[profile['profile']]]
        with self.assertRaises(cli.AcceptanceError):
            cont.root_leaf(Checks(),row,delta,'corrupted root')

    def test_readonly_guard_blocks_mutations(self):
        for event,args in [('open',('bad.txt','w',0)),('open',('bad.txt',None,1)),
                           ('os.remove',('bad.txt',)),('subprocess.Popen',()),
                           ('socket.connect',())]:
            with self.subTest(event=event), self.assertRaises(RuntimeError):
                readonly(event,args)
        readonly('open',('input.json','r',0))

if __name__ == '__main__':
    unittest.main(verbosity=2)
