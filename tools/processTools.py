import ROOT
import math
from bitmasks import statusFlags as sf
from constants import *
from stxs import *

class Event:
  def __init__(self,_events,_iev,_options=None):
    self.genWeight = _events['genWeight'][_iev]
    self.STXS_stage0_id = _events['HTXS_stage_0'][_iev]
    self.STXS_stage0 = STXS_stage0_inverted[self.STXS_stage0_id]
    self.STXS_stage1p1_id = _events['HTXS_stage1_1_cat_pTjet30GeV'][_iev]
    self.STXS_stage1p2_id = convert_to_1p2(self.STXS_stage1p1_id,_events['HTXS_Higgs_pt'][_iev])
    self.STXS_stage1p2 = STXS_stage1p2_inverted[self.STXS_stage1p2_id]
    self.Ngen = _events['nGenPart'][_iev]
    self.processEvent = True
    if _options is not None:
      if _options.stage0 != '':
        if self.STXS_stage0_id not in stage0[_options.stage0]: self.processEvent = False
    self.productionWeights = None
    self.transformedProductionWeights = None
    self.validProductionWeights = False
    self.decayWeights = None
    self.transformedDecayWeights = None
    self.validDecayWeights = False
 
  def extractWeights(self,_rwgtScheme,_genParticles,_mode=None,_verb=False,_alphas=0.137,_use_helicity=False):
    partsRW, pdgIdsRW, helicitiesRW, statusRW = [], [], [], []
    for gp in _genParticles:
      if(gp.isIncoming)|(gp.isOutgoing):
        partsRW.append(gp.P4forRW)
        pdgIdsRW.append(gp.pdgId)
        helicitiesRW.append(1) # Dummy: working with sum of helicities
        if gp.isIncoming: statusRW.append(-1)
        else: statusRW.append(1)
    weights = _rwgtScheme.ComputeWeights(partsRW,pdgIdsRW,helicitiesRW,statusRW,_alphas,_use_helicity,_verb)
    if weights:
      if _mode == "production": self.validProductionWeights, self.productionWeights = True, weights
      elif _mode == "decay": self.validDecayWeights, self.decayWeights = True, weights
      else: self.validWeights, self.weights = True, weights
      #if _verb: print "  * weights (%s) = %s"%(_mode,self.weights)

  def transformWeights(self,_mode=None,_verb=False): 
    if _mode == "production": _valid, _weights = self.validProductionWeights, self.productionWeights
    elif _mode == "decay": _valid, _weights = self.validDecayWeights, self.decayWeights
    else: _valid, _weights = self.validWeights, self.weights
    if _valid:
      nPOIs = int((-3 + math.sqrt(9+8*(len(_weights)-1)))/2)
      outWeights = [1.0]*len(_weights)
      for ip in range(0,nPOIs):
        w0 = _weights[0]
        w1 = _weights[ip*2+1]
        w2 = _weights[ip*2+2]
        w1 -= w0
        w2 -= w0
        Ai = 4*w1-w2
        Bii = w2-Ai
        outWeights[ip*2+1] = Ai
        outWeights[ip*2+2] = Bii
      # Cross terms
      crossedOffset = 1 + 2*nPOIs
      crossedCounter = 0
      for ip in range(0,nPOIs):
        for jp in range(ip+1,nPOIs):
          w = _weights[crossedOffset+crossedCounter]
          w0 = _weights[0]
          wi1 = outWeights[ip*2+1]
          wi2 = outWeights[ip*2+2]
          wj1 = outWeights[jp*2+1]
          wj2 = outWeights[jp*2+2]
          w -= (w0+wi1+wi2+wj1+wj2)
          outWeights[crossedOffset+crossedCounter] = w
          crossedCounter += 1
      if _mode == "production": self.transformedProductionWeights = outWeights 
      elif _mode == "decay": self.transformedDecayWeights = outWeights
      else: self.transformedWeights = outWeights
    #if _verb: print "  * transformed weights =", self.transformedWeights

    

class GenParticle:
  # Constructor
  def __init__(self,_events,_iev,_igen,_mode=None):
    _p4 = ROOT.TLorentzVector()
    _p4.SetPtEtaPhiM(_events['GenPart_pt'][_iev][_igen],_events['GenPart_eta'][_iev][_igen],_events['GenPart_phi'][_iev][_igen],_events['GenPart_mass'][_iev][_igen])
    self.P4 = _p4
    self.pdgId = _events['GenPart_pdgId'][_iev][_igen]
    self.status = _events['GenPart_status'][_iev][_igen]
    self.statusFlags = _events['GenPart_statusFlags'][_iev][_igen]
    self.motherIdx = _events['GenPart_genPartIdxMother'][_iev][_igen]
    self.mothermotherIdx = _events['GenPart_genPartIdxMother'][_iev][self.motherIdx]
    self.motherpdgId = _events['GenPart_pdgId'][_iev][self.motherIdx] if self.motherIdx!=-1 else -999
    self.mothermotherpdgId = _events['GenPart_pdgId'][_iev][self.mothermotherIdx] if self.mothermotherIdx!=-1 else -999
    self.isHardProcess = (_events['GenPart_statusFlags'][_iev][_igen]>>sf['isHardProcess'])&0b1
    self.fromHardProcess = (_events['GenPart_statusFlags'][_iev][_igen]>>sf['fromHardProcess'])&0b1 
    self.fromHardProcessBeforeFSR = (_events['GenPart_statusFlags'][_iev][_igen]>>sf['fromHardProcessBeforeFSR'])&0b1 
    self.isIncoming = True if self.status == 21 else False
    # If incoming then extract p4 from incoming partons
    if self.isIncoming:
      if _igen == 0:
        assert self.pdgId == _events['Generator_id1'][_iev]
        pz_1 = _events['Generator_x1'][_iev]*beam_momentum
        E_1 = math.sqrt(mass_pdgId[self.pdgId]**2+pz_1**2)         
        self.P4.SetPxPyPzE(0,0,pz_1,E_1)
      elif _igen == 1: 
        assert self.pdgId == _events['Generator_id2'][_iev]
        pz_2 = -1*_events['Generator_x2'][_iev]*beam_momentum
        E_2 = math.sqrt(mass_pdgId[self.pdgId]**2+pz_2**2)         
        self.P4.SetPxPyPzE(0,0,pz_2,E_2)
      else:
        print " --> [ERROR] Incoming particle (id=%g) not in positions 0 or 1. Keeping p4 from GenParticle"%pdgId
    self.isIntermediate = True if self.status == 22 else False
    self.isOutgoing = True if(self.status == 1)|(self.status == 23) else False
    # CHECK: allowing status == 2 for unstable particles does not introduce unwanted final state
    self.isOutgoing = True if(self.status == 1)|(self.status == 2)|(self.status == 23) else False
    if _mode == "production": 
      if( self.pdgId == 25 )&( self.isIntermediate ): self.isIntermediate, self.isOutgoing = False,True
    elif _mode == "decay":
      if( self.pdgId == 25 )&( self.isIntermediate ): self.isIntermediate, self.isIncoming = False, True
    #if _options is not None:
    #  if( _options.NP == 'production' )&( self.pdgId == 25 )&( self.isIntermediate ): self.isIntermediate, self.isOutgoing = False,True
    #  elif( _options.NP == 'decay' )&( self.pdgId == 25 )&( self.isIntermediate ): self.isIntermediate, self.isIncoming = False, True
    self.fromHiggsDecay = True if self.motherpdgId == 25 else False 
    self.fromNonDirectHiggsDecay = True if self.mothermotherpdgId == 25 else False 
    self.P4forRW = [self.P4.E(),self.P4.Px(),self.P4.Py(),self.P4.Pz()]

class Muon:
  # Constructor
  def __init__(self,_events,_iev,_imu):
    _p4 = ROOT.TLorentzVector()
    _p4.SetPtEtaPhiM(_events['Muon_pt'][_iev][_imu],_events['Muon_eta'][_iev][_imu],_events['Muon_phi'][_iev][_imu],_events['Muon_mass'][_iev][_imu])
    self.P4 = _p4
    self.charge = _events['Muon_charge'][_iev][_imu]
    self.tightID = _events['Muon_tightId'][_iev][_imu]
    self.name = "muon"

class Electron:
  # Constructor
  def __init__(self,_events,_iev,_iel):
    _p4 = ROOT.TLorentzVector()
    _p4.SetPtEtaPhiM(_events['Electron_pt'][_iev][_iel],_events['Electron_eta'][_iev][_iel],_events['Electron_phi'][_iev][_iel],_events['Electron_mass'][_iev][_iel])
    self.P4 = _p4
    self.charge = _events['Electron_charge'][_iev][_iel]
    self.looseID = _events['Electron_mvaFall17V1Iso_WPL'][_iev][_iel]
    self.convVeto = _events['Electron_convVeto'][_iev][_iel]
    self.name = "electron"

class Photon:
  # Constructor
  def __init__(self,_events,_iev,_iph):
    _p4 = ROOT.TLorentzVector()
    _p4.SetPtEtaPhiM(_events['Photon_pt'][_iev][_iph],_events['Photon_eta'][_iev][_iph],_events['Photon_phi'][_iev][_iph],_events['Photon_mass'][_iev][_iph])
    self.P4 = _p4

