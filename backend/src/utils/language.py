from collections import defaultdict
from enum import StrEnum
from fasttext import FastText


class LanguageCode(StrEnum):
    aa = "aa"
    aa_DJ = "aa-DJ"
    aa_ER = "aa-ER"
    ab = "ab"
    af = "af"
    af_NA = "af-NA"
    ak = "ak"
    am = "am"
    an = "an"
    ar = "ar"
    ar_AE = "ar-AE"
    ar_BH = "ar-BH"
    ar_DJ = "ar-DJ"
    ar_DZ = "ar-DZ"
    ar_EG = "ar-EG"
    ar_EH = "ar-EH"
    ar_ER = "ar-ER"
    ar_IL = "ar-IL"
    ar_IQ = "ar-IQ"
    ar_JO = "ar-JO"
    ar_KM = "ar-KM"
    ar_KW = "ar-KW"
    ar_LB = "ar-LB"
    ar_LY = "ar-LY"
    ar_MA = "ar-MA"
    ar_MR = "ar-MR"
    ar_OM = "ar-OM"
    ar_PS = "ar-PS"
    ar_QA = "ar-QA"
    ar_SA = "ar-SA"
    ar_SD = "ar-SD"
    ar_SO = "ar-SO"
    ar_SS = "ar-SS"
    ar_SY = "ar-SY"
    ar_TD = "ar-TD"
    ar_TN = "ar-TN"
    ar_YE = "ar-YE"
    as_ = "as"
    az = "az"
    az_Arab = "az-Arab"
    az_Arab_IQ = "az-Arab-IQ"
    az_Arab_TR = "az-Arab-TR"
    az_Cyrl = "az-Cyrl"
    az_Latn = "az-Latn"
    ba = "ba"
    be = "be"
    be_tarask = "be-tarask"
    bg = "bg"
    bg_BG = "bg-BG"
    bm = "bm"
    bm_Nkoo = "bm-Nkoo"
    bn = "bn"
    bn_IN = "bn-IN"
    bo = "bo"
    bo_IN = "bo-IN"
    br = "br"
    bs = "bs"
    bs_Cyrl = "bs-Cyrl"
    bs_Latn = "bs-Latn"
    ca = "ca"
    ca_AD = "ca-AD"
    ca_ES = "ca-ES"
    ca_FR = "ca-FR"
    ca_IT = "ca-IT"
    ce = "ce"
    co = "co"
    cs = "cs"
    cs_CZ = "cs-CZ"
    cv = "cv"
    cy = "cy"
    da = "da"
    da_DK = "da-DK"
    da_GL = "da-GL"
    de = "de"
    de_AT = "de-AT"
    de_BE = "de-BE"
    de_CH = "de-CH"
    de_DE = "de-DE"
    de_IT = "de-IT"
    de_LI = "de-LI"
    de_LU = "de-LU"
    dv = "dv"
    dz = "dz"
    ee = "ee"
    ee_TG = "ee-TG"
    el = "el"
    el_CY = "el-CY"
    el_GR = "el-GR"
    el_polyton = "el-polyton"
    en = "en"
    en_AE = "en-AE"
    en_AG = "en-AG"
    en_AI = "en-AI"
    en_AS = "en-AS"
    en_AT = "en-AT"
    en_AU = "en-AU"
    en_BB = "en-BB"
    en_BE = "en-BE"
    en_BI = "en-BI"
    en_BM = "en-BM"
    en_BS = "en-BS"
    en_BW = "en-BW"
    en_BZ = "en-BZ"
    en_CA = "en-CA"
    en_CC = "en-CC"
    en_CH = "en-CH"
    en_CK = "en-CK"
    en_CM = "en-CM"
    en_CX = "en-CX"
    en_CY = "en-CY"
    en_CZ = "en-CZ"
    en_DE = "en-DE"
    en_DG = "en-DG"
    en_DK = "en-DK"
    en_DM = "en-DM"
    en_ER = "en-ER"
    en_ES = "en-ES"
    en_FI = "en-FI"
    en_FJ = "en-FJ"
    en_FK = "en-FK"
    en_FM = "en-FM"
    en_FR = "en-FR"
    en_GB = "en-GB"
    en_GD = "en-GD"
    en_GG = "en-GG"
    en_GH = "en-GH"
    en_GI = "en-GI"
    en_GM = "en-GM"
    en_GS = "en-GS"
    en_GU = "en-GU"
    en_GY = "en-GY"
    en_HK = "en-HK"
    en_HU = "en-HU"
    en_ID = "en-ID"
    en_IE = "en-IE"
    en_IL = "en-IL"
    en_IM = "en-IM"
    en_IN = "en-IN"
    en_IO = "en-IO"
    en_IT = "en-IT"
    en_JE = "en-JE"
    en_JM = "en-JM"
    en_KE = "en-KE"
    en_KI = "en-KI"
    en_KN = "en-KN"
    en_KY = "en-KY"
    en_LC = "en-LC"
    en_LR = "en-LR"
    en_LS = "en-LS"
    en_MG = "en-MG"
    en_MH = "en-MH"
    en_MO = "en-MO"
    en_MP = "en-MP"
    en_MS = "en-MS"
    en_MT = "en-MT"
    en_MU = "en-MU"
    en_MV = "en-MV"
    en_MW = "en-MW"
    en_MY = "en-MY"
    en_NA = "en-NA"
    en_NF = "en-NF"
    en_NG = "en-NG"
    en_NL = "en-NL"
    en_NO = "en-NO"
    en_NR = "en-NR"
    en_NU = "en-NU"
    en_NZ = "en-NZ"
    en_PG = "en-PG"
    en_PH = "en-PH"
    en_PK = "en-PK"
    en_PL = "en-PL"
    en_PN = "en-PN"
    en_PR = "en-PR"
    en_PT = "en-PT"
    en_PW = "en-PW"
    en_RO = "en-RO"
    en_RW = "en-RW"
    en_SB = "en-SB"
    en_SC = "en-SC"
    en_SD = "en-SD"
    en_SE = "en-SE"
    en_SG = "en-SG"
    en_SH = "en-SH"
    en_SI = "en-SI"
    en_SK = "en-SK"
    en_SL = "en-SL"
    en_SS = "en-SS"
    en_SX = "en-SX"
    en_SZ = "en-SZ"
    en_TC = "en-TC"
    en_TK = "en-TK"
    en_TO = "en-TO"
    en_TT = "en-TT"
    en_TV = "en-TV"
    en_TZ = "en-TZ"
    en_UG = "en-UG"
    en_UM = "en-UM"
    en_VC = "en-VC"
    en_VG = "en-VG"
    en_VI = "en-VI"
    en_VU = "en-VU"
    en_WS = "en-WS"
    en_ZA = "en-ZA"
    en_ZM = "en-ZM"
    en_ZW = "en-ZW"
    eo = "eo"
    es = "es"
    es_AR = "es-AR"
    es_BO = "es-BO"
    es_BR = "es-BR"
    es_BZ = "es-BZ"
    es_CL = "es-CL"
    es_CO = "es-CO"
    es_CR = "es-CR"
    es_CU = "es-CU"
    es_DO = "es-DO"
    es_EA = "es-EA"
    es_EC = "es-EC"
    es_ES = "es-ES"
    es_GQ = "es-GQ"
    es_GT = "es-GT"
    es_HN = "es-HN"
    es_IC = "es-IC"
    es_MX = "es-MX"
    es_NI = "es-NI"
    es_PA = "es-PA"
    es_PE = "es-PE"
    es_PH = "es-PH"
    es_PR = "es-PR"
    es_PY = "es-PY"
    es_SV = "es-SV"
    es_US = "es-US"
    es_UY = "es-UY"
    es_VE = "es-VE"
    et = "et"
    et_EE = "et-EE"
    eu = "eu"
    fa = "fa"
    fa_AF = "fa-AF"
    fa_IR = "fa-IR"
    ff = "ff"
    ff_Adlm = "ff-Adlm"
    ff_Adlm_BF = "ff-Adlm-BF"
    ff_Adlm_CM = "ff-Adlm-CM"
    ff_Adlm_GH = "ff-Adlm-GH"
    ff_Adlm_GM = "ff-Adlm-GM"
    ff_Adlm_GW = "ff-Adlm-GW"
    ff_Adlm_LR = "ff-Adlm-LR"
    ff_Adlm_MR = "ff-Adlm-MR"
    ff_Adlm_NE = "ff-Adlm-NE"
    ff_Adlm_NG = "ff-Adlm-NG"
    ff_Adlm_SL = "ff-Adlm-SL"
    ff_Adlm_SN = "ff-Adlm-SN"
    ff_Latn = "ff-Latn"
    ff_Latn_BF = "ff-Latn-BF"
    ff_Latn_CM = "ff-Latn-CM"
    ff_Latn_GH = "ff-Latn-GH"
    ff_Latn_GM = "ff-Latn-GM"
    ff_Latn_GN = "ff-Latn-GN"
    ff_Latn_GW = "ff-Latn-GW"
    ff_Latn_LR = "ff-Latn-LR"
    ff_Latn_MR = "ff-Latn-MR"
    ff_Latn_NE = "ff-Latn-NE"
    ff_Latn_NG = "ff-Latn-NG"
    ff_Latn_SL = "ff-Latn-SL"
    fi = "fi"
    fi_FI = "fi-FI"
    fil_PH = "fil-PH"
    fo = "fo"
    fo_DK = "fo-DK"
    fr = "fr"
    fr_BE = "fr-BE"
    fr_BF = "fr-BF"
    fr_BI = "fr-BI"
    fr_BJ = "fr-BJ"
    fr_BL = "fr-BL"
    fr_CA = "fr-CA"
    fr_CD = "fr-CD"
    fr_CF = "fr-CF"
    fr_CG = "fr-CG"
    fr_CH = "fr-CH"
    fr_CI = "fr-CI"
    fr_CM = "fr-CM"
    fr_DJ = "fr-DJ"
    fr_DZ = "fr-DZ"
    fr_FR = "fr-FR"
    fr_GA = "fr-GA"
    fr_GF = "fr-GF"
    fr_GN = "fr-GN"
    fr_GP = "fr-GP"
    fr_GQ = "fr-GQ"
    fr_HT = "fr-HT"
    fr_KM = "fr-KM"
    fr_LU = "fr-LU"
    fr_MA = "fr-MA"
    fr_MC = "fr-MC"
    fr_MF = "fr-MF"
    fr_MG = "fr-MG"
    fr_ML = "fr-ML"
    fr_MQ = "fr-MQ"
    fr_MR = "fr-MR"
    fr_MU = "fr-MU"
    fr_NC = "fr-NC"
    fr_NE = "fr-NE"
    fr_PF = "fr-PF"
    fr_PM = "fr-PM"
    fr_RE = "fr-RE"
    fr_RW = "fr-RW"
    fr_SC = "fr-SC"
    fr_SN = "fr-SN"
    fr_SY = "fr-SY"
    fr_TD = "fr-TD"
    fr_TG = "fr-TG"
    fr_TN = "fr-TN"
    fr_VU = "fr-VU"
    fr_WF = "fr-WF"
    fr_YT = "fr-YT"
    fy = "fy"
    ga = "ga"
    ga_GB = "ga-GB"
    gd = "gd"
    gl = "gl"
    gn = "gn"
    gu = "gu"
    gu_IN = "gu-IN"
    gv = "gv"
    ha = "ha"
    ha_Arab = "ha-Arab"
    ha_Arab_SD = "ha-Arab-SD"
    ha_GH = "ha-GH"
    ha_NE = "ha-NE"
    he = "he"
    he_IL = "he-IL"
    hi = "hi"
    hi_IN = "hi-IN"
    hi_Latn = "hi-Latn"
    hr = "hr"
    hr_BA = "hr-BA"
    hr_HR = "hr-HR"
    ht = "ht"
    hu = "hu"
    hu_HU = "hu-HU"
    hy = "hy"
    ia = "ia"
    id = "id"
    id_ID = "id-ID"
    ie = "ie"
    ig = "ig"
    ii = "ii"
    ik = "ik"
    io = "io"
    is_ = "is"
    it = "it"
    it_CH = "it-CH"
    it_IT = "it-IT"
    it_SM = "it-SM"
    it_VA = "it-VA"
    iu = "iu"
    iu_Latn = "iu-Latn"
    ja = "ja"
    ja_JP = "ja-JP"
    jv = "jv"
    ka = "ka"
    ki = "ki"
    kk = "kk"
    kk_Arab = "kk-Arab"
    kk_Cyrl = "kk-Cyrl"
    kk_KZ = "kk-KZ"
    kl = "kl"
    km = "km"
    kn = "kn"
    kn_IN = "kn-IN"
    ko = "ko"
    ko_CN = "ko-CN"
    ko_KP = "ko-KP"
    ko_KR = "ko-KR"
    ks = "ks"
    ks_Arab = "ks-Arab"
    ks_Deva = "ks-Deva"
    ku = "ku"
    kw = "kw"
    ky = "ky"
    la = "la"
    lb = "lb"
    lg = "lg"
    ln = "ln"
    ln_AO = "ln-AO"
    ln_CF = "ln-CF"
    ln_CG = "ln-CG"
    lo = "lo"
    lt = "lt"
    lt_LT = "lt-LT"
    lu = "lu"
    lv = "lv"
    lv_LV = "lv-LV"
    mg = "mg"
    mi = "mi"
    mk = "mk"
    ml = "ml"
    ml_IN = "ml-IN"
    mn = "mn"
    mn_Mong = "mn-Mong"
    mn_Mong_MN = "mn-Mong-MN"
    mr = "mr"
    mr_IN = "mr-IN"
    ms = "ms"
    ms_Arab = "ms-Arab"
    ms_Arab_BN = "ms-Arab-BN"
    ms_BN = "ms-BN"
    ms_ID = "ms-ID"
    ms_SG = "ms-SG"
    mt = "mt"
    my = "my"
    nb = "nb"
    nb_SJ = "nb-SJ"
    nd = "nd"
    ne = "ne"
    ne_IN = "ne-IN"
    nl = "nl"
    nl_AW = "nl-AW"
    nl_BE = "nl-BE"
    nl_BQ = "nl-BQ"
    nl_CW = "nl-CW"
    nl_NL = "nl-NL"
    nl_SR = "nl-SR"
    nl_SX = "nl-SX"
    nn = "nn"
    no = "no"
    no_NO = "no-NO"
    nr = "nr"
    nv = "nv"
    ny = "ny"
    oc = "oc"
    oc_ES = "oc-ES"
    om = "om"
    om_KE = "om-KE"
    or_ = "or"
    os = "os"
    os_RU = "os-RU"
    pa = "pa"
    pa_IN = "pa-IN"
    pa_Arab = "pa-Arab"
    pa_Guru = "pa-Guru"
    pl = "pl"
    pl_PL = "pl-PL"
    ps = "ps"
    ps_PK = "ps-PK"
    pt = "pt"
    pt_AO = "pt-AO"
    pt_BR = "pt-BR"
    pt_CH = "pt-CH"
    pt_CV = "pt-CV"
    pt_GQ = "pt-GQ"
    pt_GW = "pt-GW"
    pt_LU = "pt-LU"
    pt_MO = "pt-MO"
    pt_MZ = "pt-MZ"
    pt_PT = "pt-PT"
    pt_ST = "pt-ST"
    pt_TL = "pt-TL"
    qu = "qu"
    qu_BO = "qu-BO"
    qu_EC = "qu-EC"
    rm = "rm"
    rn = "rn"
    ro = "ro"
    ro_MD = "ro-MD"
    ro_RO = "ro-RO"
    ru = "ru"
    ru_BY = "ru-BY"
    ru_KG = "ru-KG"
    ru_KZ = "ru-KZ"
    ru_MD = "ru-MD"
    ru_RU = "ru-RU"
    ru_UA = "ru-UA"
    rw = "rw"
    sa = "sa"
    sc = "sc"
    sd = "sd"
    sd_Arab = "sd-Arab"
    sd_Deva = "sd-Deva"
    se = "se"
    se_FI = "se-FI"
    se_SE = "se-SE"
    sg = "sg"
    si = "si"
    sk = "sk"
    sk_SK = "sk-SK"
    sl = "sl"
    sl_SI = "sl-SI"
    sn = "sn"
    so = "so"
    so_DJ = "so-DJ"
    so_ET = "so-ET"
    so_KE = "so-KE"
    sq = "sq"
    sq_MK = "sq-MK"
    sq_XK = "sq-XK"
    sr = "sr"
    sr_RS = "sr-RS"
    sr_Cyrl = "sr-Cyrl"
    sr_Cyrl_BA = "sr-Cyrl-BA"
    sr_Cyrl_ME = "sr-Cyrl-ME"
    sr_Cyrl_XK = "sr-Cyrl-XK"
    sr_Latn = "sr-Latn"
    sr_Latn_BA = "sr-Latn-BA"
    sr_Latn_ME = "sr-Latn-ME"
    sr_Latn_XK = "sr-Latn-XK"
    ss = "ss"
    ss_SZ = "ss-SZ"
    st = "st"
    st_LS = "st-LS"
    su = "su"
    su_Latn = "su-Latn"
    sv = "sv"
    sv_AX = "sv-AX"
    sv_FI = "sv-FI"
    sv_SE = "sv-SE"
    sw = "sw"
    sw_CD = "sw-CD"
    sw_KE = "sw-KE"
    sw_TZ = "sw-TZ"
    sw_UG = "sw-UG"
    ta = "ta"
    ta_IN = "ta-IN"
    ta_LK = "ta-LK"
    ta_MY = "ta-MY"
    ta_SG = "ta-SG"
    te = "te"
    te_IN = "te-IN"
    tg = "tg"
    th = "th"
    th_TH = "th-TH"
    ti = "ti"
    ti_ER = "ti-ER"
    tk = "tk"
    tl = "tl"
    tn = "tn"
    tn_BW = "tn-BW"
    to = "to"
    tr = "tr"
    tr_CY = "tr-CY"
    tr_TR = "tr-TR"
    ts = "ts"
    tt = "tt"
    ug = "ug"
    uk = "uk"
    uk_UA = "uk-UA"
    ur = "ur"
    ur_IN = "ur-IN"
    ur_PK = "ur-PK"
    uz = "uz"
    uz_Arab = "uz-Arab"
    uz_Cyrl = "uz-Cyrl"
    uz_Latn = "uz-Latn"
    ve = "ve"
    vi = "vi"
    vi_VN = "vi-VN"
    vo = "vo"
    wa = "wa"
    wo = "wo"
    xh = "xh"
    yi = "yi"
    yo = "yo"
    yo_BJ = "yo-BJ"
    za = "za"
    zh = "zh"
    zh_CH = "zh-CH"
    zh_TW = "zh-TW"
    zh_Hans = "zh-Hans"
    zh_Hans_HK = "zh-Hans-HK"
    zh_Hans_MO = "zh-Hans-MO"
    zh_Hans_MY = "zh-Hans-MY"
    zh_Hans_SG = "zh-Hans-SG"
    zh_Hant = "zh-Hant"
    zh_Hant_HK = "zh-Hant-HK"
    zh_Hant_MO = "zh-Hant-MO"
    zh_Hant_MY = "zh-Hant-MY"
    zh_Latn = "zh-Latn"
    zu = "zu"
    zu_ZA = "zu-ZA"


LANGUAGES: dict[LanguageCode, str] = {
    LanguageCode.aa: "Afar",
    LanguageCode.aa_DJ: "Afar",
    LanguageCode.aa_ER: "Afar",
    LanguageCode.ab: "Abkhazian",
    LanguageCode.af: "Afrikaans",
    LanguageCode.af_NA: "Afrikaans",
    LanguageCode.ak: "Akan",
    LanguageCode.am: "Amharic",
    LanguageCode.an: "Aragonese",
    LanguageCode.ar: "Arabic",
    LanguageCode.ar_AE: "Arabic",
    LanguageCode.ar_BH: "Arabic",
    LanguageCode.ar_DJ: "Arabic",
    LanguageCode.ar_DZ: "Arabic",
    LanguageCode.ar_EG: "Arabic",
    LanguageCode.ar_EH: "Arabic",
    LanguageCode.ar_ER: "Arabic",
    LanguageCode.ar_IL: "Arabic",
    LanguageCode.ar_IQ: "Arabic",
    LanguageCode.ar_JO: "Arabic",
    LanguageCode.ar_KM: "Arabic",
    LanguageCode.ar_KW: "Arabic",
    LanguageCode.ar_LB: "Arabic",
    LanguageCode.ar_LY: "Arabic",
    LanguageCode.ar_MA: "Arabic",
    LanguageCode.ar_MR: "Arabic",
    LanguageCode.ar_OM: "Arabic",
    LanguageCode.ar_PS: "Arabic",
    LanguageCode.ar_QA: "Arabic",
    LanguageCode.ar_SA: "Arabic",
    LanguageCode.ar_SD: "Arabic",
    LanguageCode.ar_SO: "Arabic",
    LanguageCode.ar_SS: "Arabic",
    LanguageCode.ar_SY: "Arabic",
    LanguageCode.ar_TD: "Arabic",
    LanguageCode.ar_TN: "Arabic",
    LanguageCode.ar_YE: "Arabic",
    LanguageCode.as_: "Assamese",
    LanguageCode.az: "Azerbaijani",
    LanguageCode.az_Arab: "Azerbaijani",
    LanguageCode.az_Arab_IQ: "Azerbaijani",
    LanguageCode.az_Arab_TR: "Azerbaijani",
    LanguageCode.az_Cyrl: "Azerbaijani",
    LanguageCode.az_Latn: "Azerbaijani",
    LanguageCode.ba: "Bashkir",
    LanguageCode.be: "Belarusian",
    LanguageCode.be_tarask: "Belarusian",
    LanguageCode.bg: "Bulgarian",
    LanguageCode.bg_BG: "Bulgarian",
    LanguageCode.bm: "Bambara",
    LanguageCode.bm_Nkoo: "Bambara",
    LanguageCode.bn: "Bengali",
    LanguageCode.bn_IN: "Bengali",
    LanguageCode.bo: "Tibetan",
    LanguageCode.bo_IN: "Tibetan",
    LanguageCode.br: "Breton",
    LanguageCode.bs: "Bosnian",
    LanguageCode.bs_Cyrl: "Bosnian",
    LanguageCode.bs_Latn: "Bosnian",
    LanguageCode.ca: "Catalan",
    LanguageCode.ca_AD: "Catalan",
    LanguageCode.ca_ES: "Catalan",
    LanguageCode.ca_FR: "Catalan",
    LanguageCode.ca_IT: "Catalan",
    LanguageCode.ce: "Chechen",
    LanguageCode.co: "Corsican",
    LanguageCode.cs: "Czech",
    LanguageCode.cs_CZ: "Czech",
    LanguageCode.cv: "Chuvash",
    LanguageCode.cy: "Welsh",
    LanguageCode.da: "Danish",
    LanguageCode.da_DK: "Danish",
    LanguageCode.da_GL: "Danish",
    LanguageCode.de: "German",
    LanguageCode.de_AT: "German",
    LanguageCode.de_BE: "German",
    LanguageCode.de_CH: "German",
    LanguageCode.de_DE: "German",
    LanguageCode.de_IT: "German",
    LanguageCode.de_LI: "German",
    LanguageCode.de_LU: "German",
    LanguageCode.dv: "Divehi",
    LanguageCode.dz: "Dzongkha",
    LanguageCode.ee: "Ewe",
    LanguageCode.ee_TG: "Ewe",
    LanguageCode.el: "Greek",
    LanguageCode.el_CY: "Greek",
    LanguageCode.el_GR: "Greek",
    LanguageCode.el_polyton: "Greek",
    LanguageCode.en: "English",
    LanguageCode.en_AE: "English",
    LanguageCode.en_AG: "English",
    LanguageCode.en_AI: "English",
    LanguageCode.en_AS: "English",
    LanguageCode.en_AT: "English",
    LanguageCode.en_AU: "English",
    LanguageCode.en_BB: "English",
    LanguageCode.en_BE: "English",
    LanguageCode.en_BI: "English",
    LanguageCode.en_BM: "English",
    LanguageCode.en_BS: "English",
    LanguageCode.en_BW: "English",
    LanguageCode.en_BZ: "English",
    LanguageCode.en_CA: "English",
    LanguageCode.en_CC: "English",
    LanguageCode.en_CH: "English",
    LanguageCode.en_CK: "English",
    LanguageCode.en_CM: "English",
    LanguageCode.en_CX: "English",
    LanguageCode.en_CY: "English",
    LanguageCode.en_CZ: "English",
    LanguageCode.en_DE: "English",
    LanguageCode.en_DG: "English",
    LanguageCode.en_DK: "English",
    LanguageCode.en_DM: "English",
    LanguageCode.en_ER: "English",
    LanguageCode.en_ES: "English",
    LanguageCode.en_FI: "English",
    LanguageCode.en_FJ: "English",
    LanguageCode.en_FK: "English",
    LanguageCode.en_FM: "English",
    LanguageCode.en_FR: "English",
    LanguageCode.en_GB: "English",
    LanguageCode.en_GD: "English",
    LanguageCode.en_GG: "English",
    LanguageCode.en_GH: "English",
    LanguageCode.en_GI: "English",
    LanguageCode.en_GM: "English",
    LanguageCode.en_GS: "English",
    LanguageCode.en_GU: "English",
    LanguageCode.en_GY: "English",
    LanguageCode.en_HK: "English",
    LanguageCode.en_HU: "English",
    LanguageCode.en_ID: "English",
    LanguageCode.en_IE: "English",
    LanguageCode.en_IL: "English",
    LanguageCode.en_IM: "English",
    LanguageCode.en_IN: "English",
    LanguageCode.en_IO: "English",
    LanguageCode.en_IT: "English",
    LanguageCode.en_JE: "English",
    LanguageCode.en_JM: "English",
    LanguageCode.en_KE: "English",
    LanguageCode.en_KI: "English",
    LanguageCode.en_KN: "English",
    LanguageCode.en_KY: "English",
    LanguageCode.en_LC: "English",
    LanguageCode.en_LR: "English",
    LanguageCode.en_LS: "English",
    LanguageCode.en_MG: "English",
    LanguageCode.en_MH: "English",
    LanguageCode.en_MO: "English",
    LanguageCode.en_MP: "English",
    LanguageCode.en_MS: "English",
    LanguageCode.en_MT: "English",
    LanguageCode.en_MU: "English",
    LanguageCode.en_MV: "English",
    LanguageCode.en_MW: "English",
    LanguageCode.en_MY: "English",
    LanguageCode.en_NA: "English",
    LanguageCode.en_NF: "English",
    LanguageCode.en_NG: "English",
    LanguageCode.en_NL: "English",
    LanguageCode.en_NO: "English",
    LanguageCode.en_NR: "English",
    LanguageCode.en_NU: "English",
    LanguageCode.en_NZ: "English",
    LanguageCode.en_PG: "English",
    LanguageCode.en_PH: "English",
    LanguageCode.en_PK: "English",
    LanguageCode.en_PL: "English",
    LanguageCode.en_PN: "English",
    LanguageCode.en_PR: "English",
    LanguageCode.en_PT: "English",
    LanguageCode.en_PW: "English",
    LanguageCode.en_RO: "English",
    LanguageCode.en_RW: "English",
    LanguageCode.en_SB: "English",
    LanguageCode.en_SC: "English",
    LanguageCode.en_SD: "English",
    LanguageCode.en_SE: "English",
    LanguageCode.en_SG: "English",
    LanguageCode.en_SH: "English",
    LanguageCode.en_SI: "English",
    LanguageCode.en_SK: "English",
    LanguageCode.en_SL: "English",
    LanguageCode.en_SS: "English",
    LanguageCode.en_SX: "English",
    LanguageCode.en_SZ: "English",
    LanguageCode.en_TC: "English",
    LanguageCode.en_TK: "English",
    LanguageCode.en_TO: "English",
    LanguageCode.en_TT: "English",
    LanguageCode.en_TV: "English",
    LanguageCode.en_TZ: "English",
    LanguageCode.en_UG: "English",
    LanguageCode.en_UM: "English",
    LanguageCode.en_VC: "English",
    LanguageCode.en_VG: "English",
    LanguageCode.en_VI: "English",
    LanguageCode.en_VU: "English",
    LanguageCode.en_WS: "English",
    LanguageCode.en_ZA: "English",
    LanguageCode.en_ZM: "English",
    LanguageCode.en_ZW: "English",
    LanguageCode.eo: "Esperanto",
    LanguageCode.es: "Spanish",
    LanguageCode.es_AR: "Spanish",
    LanguageCode.es_BO: "Spanish",
    LanguageCode.es_BR: "Spanish",
    LanguageCode.es_BZ: "Spanish",
    LanguageCode.es_CL: "Spanish",
    LanguageCode.es_CO: "Spanish",
    LanguageCode.es_CR: "Spanish",
    LanguageCode.es_CU: "Spanish",
    LanguageCode.es_DO: "Spanish",
    LanguageCode.es_EA: "Spanish",
    LanguageCode.es_EC: "Spanish",
    LanguageCode.es_ES: "Spanish",
    LanguageCode.es_GQ: "Spanish",
    LanguageCode.es_GT: "Spanish",
    LanguageCode.es_HN: "Spanish",
    LanguageCode.es_IC: "Spanish",
    LanguageCode.es_MX: "Spanish",
    LanguageCode.es_NI: "Spanish",
    LanguageCode.es_PA: "Spanish",
    LanguageCode.es_PE: "Spanish",
    LanguageCode.es_PH: "Spanish",
    LanguageCode.es_PR: "Spanish",
    LanguageCode.es_PY: "Spanish",
    LanguageCode.es_SV: "Spanish",
    LanguageCode.es_US: "Spanish",
    LanguageCode.es_UY: "Spanish",
    LanguageCode.es_VE: "Spanish",
    LanguageCode.et: "Estonian",
    LanguageCode.et_EE: "Estonian",
    LanguageCode.eu: "Basque",
    LanguageCode.fa: "Persian",
    LanguageCode.fa_AF: "Persian",
    LanguageCode.fa_IR: "Persian",
    LanguageCode.ff: "Fulah",
    LanguageCode.ff_Adlm: "Fulah",
    LanguageCode.ff_Adlm_BF: "Fulah",
    LanguageCode.ff_Adlm_CM: "Fulah",
    LanguageCode.ff_Adlm_GH: "Fulah",
    LanguageCode.ff_Adlm_GM: "Fulah",
    LanguageCode.ff_Adlm_GW: "Fulah",
    LanguageCode.ff_Adlm_LR: "Fulah",
    LanguageCode.ff_Adlm_MR: "Fulah",
    LanguageCode.ff_Adlm_NE: "Fulah",
    LanguageCode.ff_Adlm_NG: "Fulah",
    LanguageCode.ff_Adlm_SL: "Fulah",
    LanguageCode.ff_Adlm_SN: "Fulah",
    LanguageCode.ff_Latn: "Fulah",
    LanguageCode.ff_Latn_BF: "Fulah",
    LanguageCode.ff_Latn_CM: "Fulah",
    LanguageCode.ff_Latn_GH: "Fulah",
    LanguageCode.ff_Latn_GM: "Fulah",
    LanguageCode.ff_Latn_GN: "Fulah",
    LanguageCode.ff_Latn_GW: "Fulah",
    LanguageCode.ff_Latn_LR: "Fulah",
    LanguageCode.ff_Latn_MR: "Fulah",
    LanguageCode.ff_Latn_NE: "Fulah",
    LanguageCode.ff_Latn_NG: "Fulah",
    LanguageCode.ff_Latn_SL: "Fulah",
    LanguageCode.fi: "Finnish",
    LanguageCode.fi_FI: "Finnish",
    LanguageCode.fil_PH: "Filipino",
    LanguageCode.fo: "Faroese",
    LanguageCode.fo_DK: "Faroese",
    LanguageCode.fr: "French",
    LanguageCode.fr_BE: "French",
    LanguageCode.fr_BF: "French",
    LanguageCode.fr_BI: "French",
    LanguageCode.fr_BJ: "French",
    LanguageCode.fr_BL: "French",
    LanguageCode.fr_CA: "French",
    LanguageCode.fr_CD: "French",
    LanguageCode.fr_CF: "French",
    LanguageCode.fr_CG: "French",
    LanguageCode.fr_CH: "French",
    LanguageCode.fr_CI: "French",
    LanguageCode.fr_CM: "French",
    LanguageCode.fr_DJ: "French",
    LanguageCode.fr_DZ: "French",
    LanguageCode.fr_FR: "French",
    LanguageCode.fr_GA: "French",
    LanguageCode.fr_GF: "French",
    LanguageCode.fr_GN: "French",
    LanguageCode.fr_GP: "French",
    LanguageCode.fr_GQ: "French",
    LanguageCode.fr_HT: "French",
    LanguageCode.fr_KM: "French",
    LanguageCode.fr_LU: "French",
    LanguageCode.fr_MA: "French",
    LanguageCode.fr_MC: "French",
    LanguageCode.fr_MF: "French",
    LanguageCode.fr_MG: "French",
    LanguageCode.fr_ML: "French",
    LanguageCode.fr_MQ: "French",
    LanguageCode.fr_MR: "French",
    LanguageCode.fr_MU: "French",
    LanguageCode.fr_NC: "French",
    LanguageCode.fr_NE: "French",
    LanguageCode.fr_PF: "French",
    LanguageCode.fr_PM: "French",
    LanguageCode.fr_RE: "French",
    LanguageCode.fr_RW: "French",
    LanguageCode.fr_SC: "French",
    LanguageCode.fr_SN: "French",
    LanguageCode.fr_SY: "French",
    LanguageCode.fr_TD: "French",
    LanguageCode.fr_TG: "French",
    LanguageCode.fr_TN: "French",
    LanguageCode.fr_VU: "French",
    LanguageCode.fr_WF: "French",
    LanguageCode.fr_YT: "French",
    LanguageCode.fy: "Western Frisian",
    LanguageCode.ga: "Irish",
    LanguageCode.ga_GB: "Irish",
    LanguageCode.gd: "Scottish Gaelic",
    LanguageCode.gl: "Galician",
    LanguageCode.gn: "Guarani",
    LanguageCode.gu: "Gujarati",
    LanguageCode.gu_IN: "Gujarati",
    LanguageCode.gv: "Manx",
    LanguageCode.ha: "Hausa",
    LanguageCode.ha_Arab: "Hausa",
    LanguageCode.ha_Arab_SD: "Hausa",
    LanguageCode.ha_GH: "Hausa",
    LanguageCode.ha_NE: "Hausa",
    LanguageCode.he: "Hebrew",
    LanguageCode.he_IL: "Hebrew",
    LanguageCode.hi: "Hindi",
    LanguageCode.hi_IN: "Hindi",
    LanguageCode.hi_Latn: "Hindi",
    LanguageCode.hr: "Croatian",
    LanguageCode.hr_BA: "Croatian",
    LanguageCode.hr_HR: "Croatian",
    LanguageCode.ht: "Haitian",
    LanguageCode.hu: "Hungarian",
    LanguageCode.hu_HU: "Hungarian",
    LanguageCode.hy: "Armenian",
    LanguageCode.ia: "Interlingua",
    LanguageCode.id: "Indonesian",
    LanguageCode.id_ID: "Indonesian",
    LanguageCode.ie: "Interlingue",
    LanguageCode.ig: "Igbo",
    LanguageCode.ii: "Sichuan Yi",
    LanguageCode.ik: "Inupiaq",
    LanguageCode.io: "Ido",
    LanguageCode.is_: "Icelandic",
    LanguageCode.it: "Italian",
    LanguageCode.it_CH: "Italian",
    LanguageCode.it_IT: "Italian",
    LanguageCode.it_SM: "Italian",
    LanguageCode.it_VA: "Italian",
    LanguageCode.iu: "Inuktitut",
    LanguageCode.iu_Latn: "Inuktitut",
    LanguageCode.ja: "Japanese",
    LanguageCode.ja_JP: "Japanese",
    LanguageCode.jv: "Javanese",
    LanguageCode.ka: "Georgian",
    LanguageCode.ki: "Kikuyu",
    LanguageCode.kk: "Kazakh",
    LanguageCode.kk_Arab: "Kazakh",
    LanguageCode.kk_Cyrl: "Kazakh",
    LanguageCode.kk_KZ: "Kazakh",
    LanguageCode.kl: "Kalaallisut",
    LanguageCode.km: "Central Khmer",
    LanguageCode.kn: "Kannada",
    LanguageCode.kn_IN: "Kannada",
    LanguageCode.ko: "Korean",
    LanguageCode.ko_CN: "Korean",
    LanguageCode.ko_KP: "Korean",
    LanguageCode.ko_KR: "Korean",
    LanguageCode.ks: "Kashmiri",
    LanguageCode.ks_Arab: "Kashmiri",
    LanguageCode.ks_Deva: "Kashmiri",
    LanguageCode.ku: "Kurdish",
    LanguageCode.kw: "Cornish",
    LanguageCode.ky: "Kyrgyz",
    LanguageCode.la: "Latin",
    LanguageCode.lb: "Luxembourgish",
    LanguageCode.lg: "Ganda",
    LanguageCode.ln: "Lingala",
    LanguageCode.ln_AO: "Lingala",
    LanguageCode.ln_CF: "Lingala",
    LanguageCode.ln_CG: "Lingala",
    LanguageCode.lo: "Lao",
    LanguageCode.lt: "Lithuanian",
    LanguageCode.lt_LT: "Lithuanian",
    LanguageCode.lu: "Luba-Katanga",
    LanguageCode.lv: "Latvian",
    LanguageCode.lv_LV: "Latvian",
    LanguageCode.mg: "Malagasy",
    LanguageCode.mi: "Maori",
    LanguageCode.mk: "Macedonian",
    LanguageCode.ml: "Malayalam",
    LanguageCode.ml_IN: "Malayalam",
    LanguageCode.mn: "Mongolian",
    LanguageCode.mn_Mong: "Mongolian",
    LanguageCode.mn_Mong_MN: "Mongolian",
    LanguageCode.mr: "Marathi",
    LanguageCode.mr_IN: "Marathi",
    LanguageCode.ms: "Malay",
    LanguageCode.ms_Arab: "Malay",
    LanguageCode.ms_Arab_BN: "Malay",
    LanguageCode.ms_BN: "Malay",
    LanguageCode.ms_ID: "Malay",
    LanguageCode.ms_SG: "Malay",
    LanguageCode.mt: "Maltese",
    LanguageCode.my: "Burmese",
    LanguageCode.nb: "Norwegian Bokmål",
    LanguageCode.nb_SJ: "Norwegian Bokmål",
    LanguageCode.nd: "North Ndebele",
    LanguageCode.ne: "Nepali",
    LanguageCode.ne_IN: "Nepali",
    LanguageCode.nl: "Dutch",
    LanguageCode.nl_AW: "Dutch",
    LanguageCode.nl_BE: "Dutch",
    LanguageCode.nl_BQ: "Dutch",
    LanguageCode.nl_CW: "Dutch",
    LanguageCode.nl_NL: "Dutch",
    LanguageCode.nl_SR: "Dutch",
    LanguageCode.nl_SX: "Dutch",
    LanguageCode.nn: "Norwegian Nynorsk",
    LanguageCode.no: "Norwegian",
    LanguageCode.no_NO: "Norwegian",
    LanguageCode.nr: "South Ndebele",
    LanguageCode.nv: "Navajo",
    LanguageCode.ny: "Chichewa",
    LanguageCode.oc: "Occitan",
    LanguageCode.oc_ES: "Occitan",
    LanguageCode.om: "Oromo",
    LanguageCode.om_KE: "Oromo",
    LanguageCode.or_: "Oriya",
    LanguageCode.os: "Ossetian",
    LanguageCode.os_RU: "Ossetian",
    LanguageCode.pa: "Punjabi",
    LanguageCode.pa_IN: "Punjabi",
    LanguageCode.pa_Arab: "Punjabi",
    LanguageCode.pa_Guru: "Punjabi",
    LanguageCode.pl: "Polish",
    LanguageCode.pl_PL: "Polish",
    LanguageCode.ps: "Pashto",
    LanguageCode.ps_PK: "Pashto",
    LanguageCode.pt: "Portuguese",
    LanguageCode.pt_AO: "Portuguese",
    LanguageCode.pt_BR: "Portuguese",
    LanguageCode.pt_CH: "Portuguese",
    LanguageCode.pt_CV: "Portuguese",
    LanguageCode.pt_GQ: "Portuguese",
    LanguageCode.pt_GW: "Portuguese",
    LanguageCode.pt_LU: "Portuguese",
    LanguageCode.pt_MO: "Portuguese",
    LanguageCode.pt_MZ: "Portuguese",
    LanguageCode.pt_PT: "Portuguese",
    LanguageCode.pt_ST: "Portuguese",
    LanguageCode.pt_TL: "Portuguese",
    LanguageCode.qu: "Quechua",
    LanguageCode.qu_BO: "Quechua",
    LanguageCode.qu_EC: "Quechua",
    LanguageCode.rm: "Romansh",
    LanguageCode.rn: "Rundi",
    LanguageCode.ro: "Romanian",
    LanguageCode.ro_MD: "Romanian",
    LanguageCode.ro_RO: "Romanian",
    LanguageCode.ru: "Russian",
    LanguageCode.ru_BY: "Russian",
    LanguageCode.ru_KG: "Russian",
    LanguageCode.ru_KZ: "Russian",
    LanguageCode.ru_MD: "Russian",
    LanguageCode.ru_RU: "Russian",
    LanguageCode.ru_UA: "Russian",
    LanguageCode.rw: "Kinyarwanda",
    LanguageCode.sa: "Sanskrit",
    LanguageCode.sc: "Sardinian",
    LanguageCode.sd: "Sindhi",
    LanguageCode.sd_Arab: "Sindhi",
    LanguageCode.sd_Deva: "Sindhi",
    LanguageCode.se: "Northern Sami",
    LanguageCode.se_FI: "Northern Sami",
    LanguageCode.se_SE: "Northern Sami",
    LanguageCode.sg: "Sango",
    LanguageCode.si: "Sinhala",
    LanguageCode.sk: "Slovak",
    LanguageCode.sk_SK: "Slovak",
    LanguageCode.sl: "Slovenian",
    LanguageCode.sl_SI: "Slovenian",
    LanguageCode.sn: "Shona",
    LanguageCode.so: "Somali",
    LanguageCode.so_DJ: "Somali",
    LanguageCode.so_ET: "Somali",
    LanguageCode.so_KE: "Somali",
    LanguageCode.sq: "Albanian",
    LanguageCode.sq_MK: "Albanian",
    LanguageCode.sq_XK: "Albanian",
    LanguageCode.sr: "Serbian",
    LanguageCode.sr_RS: "Serbian",
    LanguageCode.sr_Cyrl: "Serbian",
    LanguageCode.sr_Cyrl_BA: "Serbian",
    LanguageCode.sr_Cyrl_ME: "Serbian",
    LanguageCode.sr_Cyrl_XK: "Serbian",
    LanguageCode.sr_Latn: "Serbian",
    LanguageCode.sr_Latn_BA: "Serbian",
    LanguageCode.sr_Latn_ME: "Serbian",
    LanguageCode.sr_Latn_XK: "Serbian",
    LanguageCode.ss: "Swati",
    LanguageCode.ss_SZ: "Swati",
    LanguageCode.st: "Southern Sotho",
    LanguageCode.st_LS: "Southern Sotho",
    LanguageCode.su: "Sundanese",
    LanguageCode.su_Latn: "Sundanese",
    LanguageCode.sv: "Swedish",
    LanguageCode.sv_AX: "Swedish",
    LanguageCode.sv_FI: "Swedish",
    LanguageCode.sv_SE: "Swedish",
    LanguageCode.sw: "Swahili",
    LanguageCode.sw_CD: "Swahili",
    LanguageCode.sw_KE: "Swahili",
    LanguageCode.sw_TZ: "Swahili",
    LanguageCode.sw_UG: "Swahili",
    LanguageCode.ta: "Tamil",
    LanguageCode.ta_IN: "Tamil",
    LanguageCode.ta_LK: "Tamil",
    LanguageCode.ta_MY: "Tamil",
    LanguageCode.ta_SG: "Tamil",
    LanguageCode.te: "Telugu",
    LanguageCode.te_IN: "Telugu",
    LanguageCode.tg: "Tajik",
    LanguageCode.th: "Thai",
    LanguageCode.th_TH: "Thai",
    LanguageCode.ti: "Tigrinya",
    LanguageCode.ti_ER: "Tigrinya",
    LanguageCode.tk: "Turkmen",
    LanguageCode.tl: "Tagalog",
    LanguageCode.tn: "Tswana",
    LanguageCode.tn_BW: "Tswana",
    LanguageCode.to: "Tonga",
    LanguageCode.tr: "Turkish",
    LanguageCode.tr_CY: "Turkish",
    LanguageCode.tr_TR: "Turkish",
    LanguageCode.ts: "Tsonga",
    LanguageCode.tt: "Tatar",
    LanguageCode.ug: "Uyghur",
    LanguageCode.uk: "Ukrainian",
    LanguageCode.uk_UA: "Ukrainian",
    LanguageCode.ur: "Urdu",
    LanguageCode.ur_IN: "Urdu",
    LanguageCode.ur_PK: "Urdu",
    LanguageCode.uz: "Uzbek",
    LanguageCode.uz_Arab: "Uzbek",
    LanguageCode.uz_Cyrl: "Uzbek",
    LanguageCode.uz_Latn: "Uzbek",
    LanguageCode.ve: "Venda",
    LanguageCode.vi: "Vietnamese",
    LanguageCode.vi_VN: "Vietnamese",
    LanguageCode.vo: "Volapük",
    LanguageCode.wa: "Walloon",
    LanguageCode.wo: "Wolof",
    LanguageCode.xh: "Xhosa",
    LanguageCode.yi: "Yiddish",
    LanguageCode.yo: "Yoruba",
    LanguageCode.yo_BJ: "Yoruba",
    LanguageCode.za: "Zhuang",
    LanguageCode.zh: "Chinese",
    LanguageCode.zh_CH: "Chinese",
    LanguageCode.zh_TW: "Chinese",
    LanguageCode.zh_Hans: "Chinese",
    LanguageCode.zh_Hans_HK: "Chinese",
    LanguageCode.zh_Hans_MO: "Chinese",
    LanguageCode.zh_Hans_MY: "Chinese",
    LanguageCode.zh_Hans_SG: "Chinese",
    LanguageCode.zh_Hant: "Chinese",
    LanguageCode.zh_Hant_HK: "Chinese",
    LanguageCode.zh_Hant_MO: "Chinese",
    LanguageCode.zh_Hant_MY: "Chinese",
    LanguageCode.zh_Latn: "Chinese",
    LanguageCode.zu: "Zulu",
    LanguageCode.zu_ZA: "Zulu",
}


def detect_language(model: FastText, texts: list[str]) -> tuple[LanguageCode, float]:
    """
    Detects the dominant language from a list of texts.
    Returns a tuple containing the language code and its average confidence score.
    """
    if not texts:
        return LanguageCode.en, 0.0

    # Get top 3 predictions for each text to gather candidates
    labels, probabilities = model.predict(texts, k=3)

    score_sums: defaultdict[str, float] = defaultdict(float)

    # Aggregate scores for each language across all texts
    for text_labels, text_probs in zip(labels, probabilities):
        for label, prob in zip(text_labels, text_probs):
            # Clean label: "__label__en" -> "en"
            lang = label.replace("__label__", "")
            score_sums[lang] += float(prob)

    # Find the language with the highest total score
    best_lang_str = max(score_sums, key=lambda x: score_sums.get(x, 0.0))
    
    # Calculate average score (total score / number of input texts)
    avg_score = score_sums[best_lang_str] / len(texts)

    # Convert string to LanguageCode. Fallback to English if prediction is unknown (safe guard)
    try:
        best_lang = LanguageCode(best_lang_str)
    except ValueError:
        # Fallback for languages that might be in FastText but not in our explicit supported list, or vice versa
        best_lang = LanguageCode.en

    return best_lang, avg_score