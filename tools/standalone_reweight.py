import sys
import os
import ROOT
import imp
import subprocess
import argparse
import math
import json
from collections import defaultdict

def GetConfigFile(filename):
    with open(filename) as jsonfile:
        cfg = json.load(jsonfile)

    for p in cfg['parameters']:
        for k in cfg['parameter_defaults']:
            if k not in p:
                p[k] = cfg['parameter_defaults'][k]
    return cfg


class StandaloneReweight:

    def __init__(self, rw_pack,_mode="production"):
        self.target_dir = os.path.abspath(rw_pack)
        self.cfg = GetConfigFile(os.path.join(self.target_dir, 'config.json'))
        # self.module = module
        # self.cards = cards_dir
        self.Npars = len(self.cfg['parameters'])
        self.N = 1 + self.Npars * 2 + (self.Npars * self.Npars - self.Npars) / 2
        self.mode = _mode

        print '>> %i parameters, %i reweight points' % (self.Npars, self.N)
        self.InitModules()

        rw_me = self.mods[0]
        ## The following code adapted from Madgraph, rweight_interface.py: L1770
        self.all_pdgs = [[pdg for pdg in pdgs if pdg!=0] for pdgs in rw_me.get_pdg_order()]
        self.all_prefix = [''.join(j).strip().lower() for j in rw_me.get_prefix()]
        prefix_set = set(self.all_prefix)

        # Prepare the helicity dict
        self.hel_dict = {}
        for prefix in prefix_set:
            if hasattr(rw_me, '%sprocess_nhel' % prefix):
                nhel = getattr(rw_me, '%sprocess_nhel' % prefix).nhel
                self.hel_dict[prefix] = {}
                for i, onehel in enumerate(zip(*nhel)):
                    self.hel_dict[prefix][tuple(onehel)] = i + 1

        self.sorted_pdgs = []
        for pdglist in self.all_pdgs:
            self.sorted_pdgs.append(self.SortPDGs(pdglist))

        print '>> StandaloneReweight class initialized'
        print '>> Accepted PDG lists:'
        for pdgs in self.all_pdgs:
            print '   - %s' % pdgs
        # print self.hel_dict
        # print self.all_pdgs
        # print self.sorted_pdgs

    def InitModules(self):
        iwd = os.getcwd()

        subproc_dir = os.path.join(self.target_dir, 'rwgt/rw_me/SubProcesses')

        if not os.path.isdir(os.path.join(subproc_dir, 'rwdir_0')):
            os.chdir(subproc_dir)
            for i in xrange(self.N):
                os.mkdir('rwdir_%i' % i)
                subprocess.check_call(['cp', 'allmatrix2py.so', 'rwdir_%i/allmatrix2py.so' % i])
            os.chdir(iwd)
        else:
            print '>> Reusing working directory %s' % self.target_dir

        sys.path.append(subproc_dir)
        self.mods = []

        os.chdir(subproc_dir)

        for i in xrange(self.N):
            sys.path[-1] = '%s/rwdir_%i' % (subproc_dir, i)
            self.mods.append(imp.load_module('allmatrix2py', *imp.find_module('allmatrix2py')))
            del sys.modules['allmatrix2py']
            self.mods[-1].initialise('%s/param_card_%i.dat' % (self.target_dir, i))

        # Remove last item in list to enable loading of multiple modules
        sys.path.pop()
        
        os.chdir(iwd)

    def SortPDGs(self, pdgs):
        if self.mode == "decay": return pdgs[:1]+sorted(pdgs[1:])
        else: return sorted(pdgs[:2]) + sorted(pdgs[2:])

    def invert_momenta(self, p):
            """ fortran/C-python do not order table in the same order"""
            new_p = []
            for i in range(len(p[0])):
                new_p.append([0] * len(p))
            for i, onep in enumerate(p):
                for j, x in enumerate(onep):
                    new_p[j][i] = x
            return new_p

    def zboost(self, part, pboost=[]):
            """Both momenta should be in the same frame.
               The boost perform correspond to the boost required to set pboost at
               rest (only z boost applied).
            """
            E = pboost[0]
            pz = pboost[3]

            #beta = pz/E
            gamma = E / math.sqrt(E**2-pz**2)
            gammabeta = pz  / math.sqrt(E**2-pz**2)

            out =  [gamma * part[0] - gammabeta * part[3],
                                part[1],
                                part[2],
                                gamma * part[3] - gammabeta * part[0]]

            if abs(out[3]) < 1e-6 * out[0]:
                out[3] = 0
            return out

    def ComputeWeights(self, parts, pdgs, hels, stats, alphas, dohelicity=True, verb=False):
        assert len(parts) == len(pdgs) == len(hels) == len(stats)
        res = [1.0] * self.N

        init_pdg_dict = defaultdict(list)
        fnal_pdg_dict = defaultdict(list)

        nParts = len(parts)
        selected_pdgs = []
        for ip in xrange(nParts):
            if stats[ip] not in [-1, 1]:
                continue
            selected_pdgs.append(pdgs[ip])
            if stats[ip] == -1:
                init_pdg_dict[pdgs[ip]].append(ip)
            if stats[ip] == +1:
                fnal_pdg_dict[pdgs[ip]].append(ip)

        #n_initParts = len(init_pdg_dict.keys())
        n_initParts = 0 
        for v in init_pdg_dict.values(): n_initParts += len(v)

        evt_sorted_pdgs = self.SortPDGs(selected_pdgs)

        try:
            idx = self.sorted_pdgs.index(evt_sorted_pdgs)
        except ValueError:
            if verb: print '>> Event with PDGs %s does not match any known process' % pdgs
            #return res
            return False

        target_pdgs = self.all_pdgs[idx]

        reorder_pids = []
        for ip in xrange(len(target_pdgs)):
            target = target_pdgs[ip]
            if ip < n_initParts:
                reorder_pids.append(init_pdg_dict[target].pop(0))
            else:
                reorder_pids.append(fnal_pdg_dict[target].pop(0))
        if verb:
            print '>> Event layout is %s, matching target layout %s => ordering is %s' % (selected_pdgs, target_pdgs, reorder_pids)

        final_pdgs = []
        final_parts = []
        final_hels = []
        for ip in reorder_pids:
            final_parts.append(parts[ip])
            final_pdgs.append(pdgs[ip])
            final_hels.append(hels[ip])

        com_final_parts = []
        if n_initParts == 1: pboost = [final_parts[0][i] for i in xrange(4)]
        else: pboost = [final_parts[0][i] + final_parts[1][i] for i in xrange(4)]
        for part in final_parts:
            com_final_parts.append(self.zboost(part, pboost))

        final_parts_i = self.invert_momenta(com_final_parts)

        nhel = -1  # means sum over all helicity

        if dohelicity:
            hel_dict = self.hel_dict[self.all_prefix[idx]]
            t_final_hels = tuple(final_hels)
            if t_final_hels in hel_dict:
                nhel = hel_dict[t_final_hels]
                if verb:
                    print '>> Selected nhel=%i, from dict %s' % (nhel, self.all_prefix[idx])
            else:
                print '>> Helicity configuration %s was not found in dict, using -1' % final_hels
        scale2 = 0.
        val_ref = 1.0
        for iw in xrange(self.N):
            val = self.mods[iw].smatrixhel(final_pdgs, final_parts_i, alphas, scale2, nhel)
            if iw == 0:
                val_ref = val
            res[iw] = val / val_ref
        return res


if __name__ == '___main___':
    parser = argparse.ArgumentParser()
    parser.add_argument('--module', default='.')
    parser.add_argument('--cards', default='rw_config')
    parser.add_argument('--config', default='test.json')
    parser.add_argument('--helicity', type=int, default=1)
    parser.add_argument('-i', '--input', default='input.lhe')
    parser.add_argument('-o', '--output', default='output.lhe')
    args = parser.parse_args()

    iwd = os.getcwd()


    ROOT.gROOT.ProcessLine('#include "LHEF.h"')

    rw = StandaloneReweight(args.config, args.module, args.cards)

    # // Create Reader and Writer object
    reader = ROOT.LHEF.Reader(args.input)
    writer = ROOT.LHEF.Writer(args.output)
    # # // Copy header and init blocks and write them out.
    # //  if ( reader.outsideBlock.length() ) std::cerr << reader.outsideBlock;
    # print reader.headerBlock

    writer.headerBlock().write(str(reader.headerBlock), len(str(reader.headerBlock)))
    writer.initComments().write(str(reader.initComments), len(str(reader.initComments)))
    writer.heprup = reader.heprup
    writer.heprup.weightgroup.clear()
    writer.heprup.weightinfo.clear()

    weightgroup = ROOT.LHEF.WeightGroup()
    # weightgroup.attributes['name'] ="mg_reweighting"
    # weightgroup.attributes['weight_name_strategy'] = "includeIdInWeightName"
    writer.heprup.weightgroup.push_back(weightgroup)

    for iw in xrange(rw.N):
        weightinfo = ROOT.LHEF.WeightInfo()
        weightinfo.name = 'rw%.4i' % iw
        weightinfo.inGroup = 0
        weightinfo.isrwgt = True
        weightinfo.contents = 'from param_card_%i.dat' % iw
        writer.heprup.weightinfo.push_back(weightinfo)


    writer.init()
    neve = 0
    # // Read each event and write them out again.
    while reader.readEvent():
        ++neve
        # if reader.outsideBlock.length() ) std::cout << reader.outsideBlock;
        writer.eventComments().write(str(reader.eventComments), len(str(reader.eventComments)))
        writer.hepeup = reader.hepeup
        writer.hepeup.namedweights.clear()
        writer.hepeup.weights.clear()

        parts = []
        pdgs = []
        hels = []
        stats = []
        nParts = writer.hepeup.NUP
        for ip in xrange(nParts):
            # Put in EPxPyPz format
            parts.append([writer.hepeup.PUP[ip][3], writer.hepeup.PUP[ip][0], writer.hepeup.PUP[ip][1], writer.hepeup.PUP[ip][2]])
            pdgs.append(int(writer.hepeup.IDUP[ip]))
            stats.append(int(writer.hepeup.ISTUP[ip]))
            hels.append(round(writer.hepeup.SPINUP[ip]))
        # print hels

        res = rw.ComputeWeights(parts, pdgs, hels, stats, writer.hepeup.AQCDUP, bool(args.helicity))

        for iw, wt in enumerate(res):
            weight = ROOT.LHEF.Weight()
            weight.name = 'rw%.4i' % iw
            weight.iswgt = True
            weight.weights.push_back(wt * writer.hepeup.XWGTUP)
            writer.hepeup.namedweights.push_back(weight)

        writer.hepeup.heprup = writer.heprup
        writer.writeEvent()

# sys.exit(0)

