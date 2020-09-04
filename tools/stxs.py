from collections import OrderedDict as od

stage0 = {
  "GG2H":[10,11],
  "VBF":[20,21],
  "VH2HQQ":[22,23],
  "QQ2HLNU":[30,31],
  "QQ2HLL":[40,41],
  "GG2HLL":[50,51],
  "TTH":[60,61],
  "BBH":[70,71],
  "TH":[80,81]
}

def convert_to_1p2(_1p1,_pt):
  if _1p1 == 101:
    if _pt < 300.: return 101
    elif _pt < 450.: return 102
    elif _pt < 650.: return 103
    else: return 104
  elif( _1p1 >= 102 )&( _1p1 < 190 ): return _1p1+3
  elif _1p1 == 601:
    if _pt < 60: return 601
    elif _pt < 120: return 602
    elif _pt < 200: return 603
    elif _pt < 300: return 604
    else: return 605
  else: return _1p1

STXS_stage0 = od()
STXS_stage0["GG2H_FWDH"] = 10
STXS_stage0["GG2H"] = 11
STXS_stage0["VBF_FWDH"] = 20
STXS_stage0["VBF"] = 21
STXS_stage0["VH2HQQ_FWDH"] = 22
STXS_stage0["VH2HQQ"] = 23
STXS_stage0["QQ2HLNU_FWDH"] = 30
STXS_stage0["QQ2HLNU"] = 31
STXS_stage0["QQ2HLL_FWDH"] = 40
STXS_stage0["QQ2HLL"] = 41
STXS_stage0["GG2HLL_FWDH"] = 50
STXS_stage0["GG2HLL"] = 51
STXS_stage0["TTH_FWDH"] = 60
STXS_stage0["TTH"] = 61
STXS_stage0["BBH_FWDH"] = 70
STXS_stage0["BBH"] = 71
STXS_stage0["TH_FWDH"] = 80
STXS_stage0["TH"] = 81
STXS_stage0_inverted = {v:k for k,v in STXS_stage0.iteritems()}


STXS_stage1p2 = od()
STXS_stage1p2["UNKNOWN"] = 0
STXS_stage1p2["GG2H_FWDH"] = 100
STXS_stage1p2["GG2H_PTH_200_300"] = 101
STXS_stage1p2["GG2H_PTH_300_450"] = 102
STXS_stage1p2["GG2H_PTH_450_650"] = 103
STXS_stage1p2["GG2H_PTH_GT650"] = 104
STXS_stage1p2["GG2H_0J_PTH_0_10"] = 105
STXS_stage1p2["GG2H_0J_PTH_GT10"] = 106
STXS_stage1p2["GG2H_1J_PTH_0_60"] = 107
STXS_stage1p2["GG2H_1J_PTH_60_120"] = 108
STXS_stage1p2["GG2H_1J_PTH_120_200"] = 109
STXS_stage1p2["GG2H_GE2J_MJJ_0_350_PTH_0_60"] = 110
STXS_stage1p2["GG2H_GE2J_MJJ_0_350_PTH_60_120"] = 111
STXS_stage1p2["GG2H_GE2J_MJJ_0_350_PTH_120_200"] = 112
STXS_stage1p2["GG2H_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_0_25"] = 113
STXS_stage1p2["GG2H_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_GT25"] = 114
STXS_stage1p2["GG2H_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_0_25"] = 115
STXS_stage1p2["GG2H_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_GT25"] = 116
STXS_stage1p2["QQ2HQQ_FWDH"] = 200
STXS_stage1p2["QQ2HQQ_0J"] = 201
STXS_stage1p2["QQ2HQQ_1J"] = 202
STXS_stage1p2["QQ2HQQ_GE2J_MJJ_0_60"] = 203
STXS_stage1p2["QQ2HQQ_GE2J_MJJ_60_120"] = 204
STXS_stage1p2["QQ2HQQ_GE2J_MJJ_120_350"] = 205
STXS_stage1p2["QQ2HQQ_GE2J_MJJ_GT350_PTH_GT200"] = 206
STXS_stage1p2["QQ2HQQ_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_0_25"] = 207
STXS_stage1p2["QQ2HQQ_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_GT25"] = 208
STXS_stage1p2["QQ2HQQ_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_0_25"] = 209
STXS_stage1p2["QQ2HQQ_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_GT25"] = 210
STXS_stage1p2["QQ2HLNU_FWDH"] = 300
STXS_stage1p2["QQ2HLNU_PTV_0_75"] = 301
STXS_stage1p2["QQ2HLNU_PTV_75_150"] = 302
STXS_stage1p2["QQ2HLNU_PTV_150_250_0J"] = 303
STXS_stage1p2["QQ2HLNU_PTV_150_250_GE1J"] = 304
STXS_stage1p2["QQ2HLNU_PTV_GT250"] = 305
STXS_stage1p2["QQ2HLL_FWDH"] = 400
STXS_stage1p2["QQ2HLL_PTV_0_75"] = 401
STXS_stage1p2["QQ2HLL_PTV_75_150"] = 402
STXS_stage1p2["QQ2HLL_PTV_150_250_0J"] = 403
STXS_stage1p2["QQ2HLL_PTV_150_250_GE1J"] = 404
STXS_stage1p2["QQ2HLL_PTV_GT250"] = 405
STXS_stage1p2["GG2HLL_FWDH"] = 500
STXS_stage1p2["GG2HLL_PTV_0_75"] = 501
STXS_stage1p2["GG2HLL_PTV_75_150"] = 502
STXS_stage1p2["GG2HLL_PTV_150_250_0J"] = 503
STXS_stage1p2["GG2HLL_PTV_150_250_GE1J"] = 504
STXS_stage1p2["GG2HLL_PTV_GT250"] = 505
STXS_stage1p2["TTH_FWDH"] = 600
STXS_stage1p2["TTH_PTH_0_60"] = 601
STXS_stage1p2["TTH_PTH_60_120"] = 602
STXS_stage1p2["TTH_PTH_120_200"] = 603
STXS_stage1p2["TTH_PTH_200_300"] = 604
STXS_stage1p2["TTH_PTH_GT300"] = 605
STXS_stage1p2["BBH_FWDH"] = 700
STXS_stage1p2["BBH"] = 701
STXS_stage1p2["TH_FWDH"] = 800
STXS_stage1p2["TH"] = 801
STXS_stage1p2_inverted = {v:k for k,v in STXS_stage1p2.iteritems()}
