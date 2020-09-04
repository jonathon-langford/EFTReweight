das_samples = {
  "VHToGG_madgraph_2018":"/VHToGG_M125_13TeV_amcatnloFXFX_madspin_pythia8/RunIIAutumn18NanoAODv6-Nano25Oct2019_102X_upgrade2018_realistic_v20-v1/NANOAODSIM",
  "GluGluHToZZTo4L_powheg2_2018":"/GluGluHToZZTo4L_M125_13TeV_powheg2_JHUGenV7011_pythia8/RunIIAutumn18NanoAODv6-Nano25Oct2019_102X_upgrade2018_realistic_v20-v1/NANOAODSIM"
}

# Variables required for reweighting
nanoAODGenVars = ['genWeight',
               'HTXS_stage_0','HTXS_stage1_1_cat_pTjet30GeV','HTXS_Higgs_pt','HTXS_njets30', #STXS variables
               'nGenPart','GenPart_genPartIdxMother','GenPart_statusFlags','GenPart_status','GenPart_pdgId','GenPart_pt','GenPart_eta','GenPart_phi','GenPart_mass', #Gen part variables
               'Generator_id1','Generator_id2','Generator_x1','Generator_x2' # Colling parton variables
]

# Reconstruction level variables
nanoAODRecoVars = [
               #'nMuon', 'Muon_charge', 'Muon_pt', 'Muon_eta', 'Muon_phi', 'Muon_mass', 'Muon_tightId', # Muon variables
               #'nElectron', 'Electron_charge', 'Electron_pt', 'Electron_eta', 'Electron_phi', 'Electron_mass', 'Electron_mvaFall17V1Iso_WPL', 'Electron_convVeto', # Electron variables
               #'nPhoton', 'Photon_pt', 'Photon_eta', 'Photon_phi', 'Photon_mass' # Photon variables
]

