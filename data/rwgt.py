from collections import OrderedDict as od


rwgt_modules_production = {
  "gg_H_plusjj_SMEFT":{
    "name":"/afs/cern.ch/work/j/jlangfor/eft/Jun20/EFT2Obs/rw_gg_H_plusjj_SMEFT"
  },
  "pp_Hll_SMEFT":{
    "name":"/afs/cern.ch/work/j/jlangfor/eft/Jun20/EFT2Obs/rw_pp_Hll_j_SMEFT",
  }
}

rwgt_modules_decay = {
  "H_4l_SMEFT":{
    #"name":"/afs/cern.ch/work/j/jlangfor/eft/Jun20/EFT2Obs/rw_H_4l_inctau_SMEFT"
    "name":"/eos/home-j/jlangfor/eft/reweighting_modules/rw_H_4l_inctau_SMEFT"
  }
}

# Map which relates EFT Wilson coefficients to position in reweighting scheme
rwgtParamMap = od()
rwgtParamMap['sm'] = 0
rwgtParamMap['cHBox'] = 1
rwgtParamMap['cHDD'] = 3
rwgtParamMap['cHG'] = 5
rwgtParamMap['cHW'] = 7
rwgtParamMap['cHB'] = 9
rwgtParamMap['cHWB'] = 11
rwgtParamMap['cuGAbs'] = 13
rwgtParamMap['cHl1'] = 15
rwgtParamMap['cHl3'] = 17
rwgtParamMap['cHe'] = 19
rwgtParamMap['cHq1'] = 21
rwgtParamMap['cHq3'] = 23
rwgtParamMap['cHu'] = 25
rwgtParamMap['cHd'] = 27
rwgtParamMap['cll1'] = 29
