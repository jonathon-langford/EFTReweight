# Script to reweight nanoAOD sample
import uproot as upr
import ROOT
import numpy as np
import pandas as pd
import json
from Utilities.General.cmssw_das_client import get_data as das_query
import os, sys
import re
from optparse import OptionParser
from collections import OrderedDict as od

# Standalone reweighting tool
from tools.standalone_reweight import *

# Processing tools
from tools.processTools import *

# Data
from data.nanoAOD import *
from data.rwgt import *
#from data.stxs import *

def get_options():
  parser = OptionParser()
  parser.add_option('--process', dest='process', default='VHToGG_madgraph_2018', help="Signal process")
  parser.add_option('--nEvents', dest='nEvents', default=100, type='int',help="Number of events to process")
  parser.add_option('--nBlocks', dest='nBlocks', default=1, type='int',help="Number of event blocks (nEvents) to process")
  parser.add_option('--NP', dest='NP', default='both', help="New physics specified in production/decay/both")
  parser.add_option('--rwgtModuleProduction', dest='rwgtModuleProduction', default='', help="Reweighting module for production: must match signal process")
  parser.add_option('--rwgtModuleDecay', dest='rwgtModuleDecay', default='', help="Reweighting module for decay: must match signal process")
  parser.add_option('--allowNonDirectDecay', dest='allowNonDirectDecay', default=False, action="store_true", help="Allow non direct decay e.g. H->ZZ->4l")
  parser.add_option('--stage0', dest='stage0', default='', help="Limit events to STXS stage 0 bin")
  parser.add_option('--applySelection', dest='applySelection', default=False, action="store_true", help="Apply event selection")
  parser.add_option('--outputROOT', dest='outputROOT', default='./output/output.root', help="Output ROOT file name")
  parser.add_option('--verb', dest='verb', default=False, action="store_true", help="Verbose output")
  return parser.parse_args()
(opt,args) = get_options()

# Check reweighting modules exist
if opt.NP not in ['production','decay','both']:
  print " [ERROR] NP must be in [production,decay,both]. Leaving"
  sys.exit(1)
if( opt.NP == "both" )|( opt.NP == "production" ):
  if opt.rwgtModuleProduction not in rwgt_modules_production: 
    print " [ERROR] rwgtModuleProduction (%s) not in allowed reweighting modules. Use one of the following: %s"%(opt.rwgtModuleProduction,rwgt_modules_production.keys())
if( opt.NP == "both" )|( opt.NP == "decay" ):
  if opt.rwgtModuleDecay not in rwgt_modules_decay: 
    print " [ERROR] rwgtModuleDecay (%s) not in allowed reweighting modules. Use one of the following: %s"%(opt.rwgtModuleDecay,rwgt_modules_decay.keys())

# Load reweight modules
rwgt = {'production':None,'decay':None}
if(opt.NP == "production")|(opt.NP == "both"): rwgt['production'] = StandaloneReweight(rwgt_modules_production[opt.rwgtModuleProduction]['name'])
if(opt.NP == "decay")|(opt.NP == "both"): rwgt['decay'] = StandaloneReweight(rwgt_modules_decay[opt.rwgtModuleDecay]['name'],_mode="decay")
modes = []
for k, v in rwgt.iteritems(): 
  if v is not None: modes.append(k)

# Define histograms
fout = ROOT.TFile(opt.outputROOT,"RECREATE")
histVars = od()
for mode in modes: histVars['valid%sWeights'%mode.capitalize()] = [2,0,2]
histVars['STXS_stage1p2_id'] = [1000,0,1000]
histVars['pTH'] = [40,0,400]
scalingVars = od()
scalingVars['STXS_stage1p2_id'] = [1000,0,1000]
# For all events: inclusing those in which the reweighting has not worked
histsAllEvents = od()
for hv, binning in histVars.iteritems(): histsAllEvents[hv] = ROOT.TH1F("%s_allEvents"%hv,"",binning[0],binning[1],binning[2])
# For events in which reweighting has worked
hists = od()
for param in rwgtParamMap:
  for hv, binning in histVars.iteritems(): 
    for mode in modes:
      k = "%s_%s_%s"%(hv,param,mode[0])
      hists[k] = ROOT.TH1F(k,"",binning[0],binning[1],binning[2])
# For working out scaling functions
hists_lin = od()
for param in rwgtParamMap:
  if param == "sm": continue
  for sv, binning in scalingVars.iteritems(): 
    for mode in modes:
      k = "%s_%s_%s_lin"%(sv,param,mode[0])
      hists_lin[k] = ROOT.TH1F(k,"",binning[0],binning[1],binning[2])
hists_sq = od()
for param in rwgtParamMap:
  if param == "sm": continue
  for sv, binning in scalingVars.iteritems(): 
    for mode in modes:
      k = "%s_%s_%s_sq"%(sv,param,mode[0])
      hists_sq[k] = ROOT.TH1F(k,"",binning[0],binning[1],binning[2])
hists_cross = od()
for iparam in range(1,len(rwgtParamMap.keys())):
  for jparam in range(iparam+1,len(rwgtParamMap.keys())):
    ip = rwgtParamMap.keys()[iparam]
    jp = rwgtParamMap.keys()[jparam]
    for sv, binning in scalingVars.iteritems(): 
      for mode in modes:
        k = "%s_%s_%s_%s_cross"%(sv,ip,jp,mode[0])
        hists_cross[k] = ROOT.TH1F(k,"",binning[0],binning[1],binning[2])

# Open sample
das_sample = das_samples[opt.process]
# Create list of files
files = []
for fdata in das_query("file dataset=%s"%das_sample, cmd="dasgoclient --dasmaps=./")['data']: files.append("root://cms-xrd-global.cern.ch/%s"%fdata['file'][0]['name'])

# TODO: add loop over files
f_upr = upr.open(files[0])
t_upr = f_upr['Events']

# Loop over event blocks
for nb in range(0,opt.nBlocks):
  events = {}
  estart, estop = opt.nEvents*nb, opt.nEvents*(nb+1)
  for v in nanoAODGenVars: events[v] = t_upr.array(v,entrystart=estart,entrystop=estop)

  # Loop over events
  Nev = opt.nEvents if opt.nEvents < len(events[nanoAODGenVars[0]]) else len(events[nanoAODGenVars[0]])
  for iev in range(0,Nev):
    ev_id = opt.nEvents*nb+iev
    if ev_id % 1000 == 0: print " --> Block %g: finished event %g"%(nb,ev_id)
    ev = Event(events,iev,opt)
    if not ev.processEvent: continue

    # Print event contents
    if opt.verb:
      print "\n~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"
      print "Processing event: %g"%ev_id

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # Reweighting:
    for mode in modes:
      # Extract gen particles from hard process for reweighting (depending on mode)
      gps = []
      for igen in range(0,ev.Ngen):
        gp = GenParticle(events,iev,igen,_mode=mode)
        # For new physics in production
        if mode == "production":
          if( gp.isHardProcess )&( gp.isIncoming ): gps.append(gp)
          elif( gp.isHardProcess )&( gp.isOutgoing ): 
            # Remove Higgs decay products as looking at production
            if gp.fromHiggsDecay: continue
            if gp.fromNonDirectHiggsDecay: continue
            gps.append(gp)
        # For new physics in decay
        elif mode == "decay":
          if( gp.isHardProcess )&( gp.pdgId == 25 )&( gp.isIncoming ): gps.append(gp)
          elif( gp.isHardProcess )&( gp.isOutgoing ):
            if opt.allowNonDirectDecay:
              if( gp.fromHiggsDecay )|( gp.fromNonDirectHiggsDecay ): gps.append(gp)
            else:
              if gp.fromHiggsDecay: gps.append(gp)
        # Else: add all gen particles
        else: gps.append(gp)

      # Print gen particles..
      if opt.verb:
        print "  --> Reweighting: %s"%mode
        print "        --> Incoming particles:"
        for igp in gps:
          if igp.isIncoming:
            print "            * pdgId = %-4g, (px,py,pz,E) = (%-6.1f,%-6.1f,%-6.1f,%-6.1f) GeV, mother pdgId = %-4g, mother mother pdgId = %-.4g"%(igp.pdgId,igp.P4.Px(),igp.P4.Py(),igp.P4.Pz(),igp.P4.E(),igp.motherpdgId,igp.mothermotherpdgId)
        print "        --> Outgoing particles:"
        for igp in gps:
          if igp.isOutgoing:
            print "            * pdgId = %-4g, (pt,eta,phi,E) = (%-6.1f GeV, %-6.1f, %-6.1f, %-6.1f GeV), mother idx = %-4g, mother pdgId = %-4g, mother mother pdgId = %-.4g"%(igp.pdgId,igp.P4.Pt(),igp.P4.Eta(),igp.P4.Phi(),igp.P4.E(),igp.motherIdx,igp.motherpdgId,igp.mothermotherpdgId)

      # Do reweighting
      ev.extractWeights(rwgt[mode],gps,_mode=mode,_verb=False)
      ev.transformWeights(_mode=mode,_verb=False)

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # Extract particles
    higgs = None
    for gp in gps:
      if gp.pdgId == 25: higgs = gp
    if higgs is None:
      print " [ERROR] No gen higgs in event. Skipping..."
      continue
    ev.pTH = higgs.P4.Pt()

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # Event selection
    # Add some selection
    #eventPass = True
    #if opt.applySelection:
      # Add selection e.g.
      #if ev.PTH < 100: eventPass = False
    #if not eventPass: continue

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # Fill histograms
    for hv in histVars: histsAllEvents[hv].Fill( getattr(ev,hv),ev.genWeight )
    for mode in modes:
      _valid = ev.validProductionWeights if mode == "production" else ev.validDecayWeights
      if _valid:
        _weights = ev.productionWeights if mode == "production" else ev.decayWeights
        _transformedWeights = ev.transformedProductionWeights if mode == "production" else ev.transformedDecayWeights
        for param, paramIdx in rwgtParamMap.iteritems():
          for hv in histVars:
            k = "%s_%s_%s"%(hv,param,mode[0])
            hists[k].Fill( getattr(ev,hv), ev.genWeight*_weights[paramIdx+1] )
          for sv in scalingVars:
            klin = "%s_%s_%s_lin"%(sv,param,mode[0])
            ksq = "%s_%s_%s_sq"%(sv,param,mode[0])
            if param == "sm": continue
            hists_lin[klin].Fill( getattr(ev,sv), ev.genWeight*_transformedWeights[paramIdx] )
            hists_sq[ksq].Fill( getattr(ev,sv), ev.genWeight*_transformedWeights[paramIdx+1] )
        # For cross terms
        crossedOffset = 1+int(-3 + math.sqrt(9+8*(len(_weights)-1)))
        crossedCounter = 0
        for iparam in range(1,len(rwgtParamMap.keys())):
          for jparam in range(iparam+1,len(rwgtParamMap.keys())):
            ip = rwgtParamMap.keys()[iparam]
            jp = rwgtParamMap.keys()[jparam]
            for sv in scalingVars:
              kcross = "%s_%s_%s_%s_cross"%(sv,ip,jp,mode[0])
              hists_cross[kcross].Fill( getattr(ev,sv), ev.genWeight*_transformedWeights[crossedOffset+crossedCounter])
            crossedCounter += 1
    
fout.Write()
fout.Close() 
