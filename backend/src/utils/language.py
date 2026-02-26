import math
from collections import defaultdict
from enum import StrEnum

from fasttext import FastText


class LanguageCode(StrEnum):
    """
    ISO 639-1 language codes supported by the translation service.
    """

    aa = "aa"
    ab = "ab"
    af = "af"
    ak = "ak"
    am = "am"
    an = "an"
    ar = "ar"
    as_ = "as"
    az = "az"
    ba = "ba"
    be = "be"
    bg = "bg"
    bm = "bm"
    bn = "bn"
    bo = "bo"
    br = "br"
    bs = "bs"
    ca = "ca"
    ce = "ce"
    co = "co"
    cs = "cs"
    cv = "cv"
    cy = "cy"
    da = "da"
    de = "de"
    dv = "dv"
    dz = "dz"
    ee = "ee"
    el = "el"
    en = "en"
    eo = "eo"
    es = "es"
    et = "et"
    eu = "eu"
    fa = "fa"
    ff = "ff"
    fi = "fi"
    fil_PH = "fil-PH"
    fo = "fo"
    fr = "fr"
    fy = "fy"
    ga = "ga"
    gd = "gd"
    gl = "gl"
    gn = "gn"
    gu = "gu"
    gv = "gv"
    ha = "ha"
    he = "he"
    hi = "hi"
    hr = "hr"
    ht = "ht"
    hu = "hu"
    hy = "hy"
    ia = "ia"
    id = "id"
    ie = "ie"
    ig = "ig"
    ii = "ii"
    ik = "ik"
    io = "io"
    is_ = "is"
    it = "it"
    iu = "iu"
    ja = "ja"
    jv = "jv"
    ka = "ka"
    ki = "ki"
    kk = "kk"
    kl = "kl"
    km = "km"
    kn = "kn"
    ko = "ko"
    ks = "ks"
    ku = "ku"
    kw = "kw"
    ky = "ky"
    la = "la"
    lb = "lb"
    lg = "lg"
    ln = "ln"
    lo = "lo"
    lt = "lt"
    lu = "lu"
    lv = "lv"
    mg = "mg"
    mi = "mi"
    mk = "mk"
    ml = "ml"
    mn = "mn"
    mr = "mr"
    ms = "ms"
    mt = "mt"
    my = "my"
    nb = "nb"
    nd = "nd"
    ne = "ne"
    nl = "nl"
    nn = "nn"
    no = "no"
    nr = "nr"
    nv = "nv"
    ny = "ny"
    oc = "oc"
    om = "om"
    or_ = "or"
    os = "os"
    pa = "pa"
    pl = "pl"
    ps = "ps"
    pt = "pt"
    qu = "qu"
    rm = "rm"
    rn = "rn"
    ro = "ro"
    ru = "ru"
    rw = "rw"
    sa = "sa"
    sc = "sc"
    sd = "sd"
    se = "se"
    sg = "sg"
    si = "si"
    sk = "sk"
    sl = "sl"
    sn = "sn"
    so = "so"
    sq = "sq"
    sr = "sr"
    ss = "ss"
    st = "st"
    su = "su"
    sv = "sv"
    sw = "sw"
    ta = "ta"
    te = "te"
    tg = "tg"
    th = "th"
    ti = "ti"
    tk = "tk"
    tl = "tl"
    tn = "tn"
    to = "to"
    tr = "tr"
    ts = "ts"
    tt = "tt"
    ug = "ug"
    uk = "uk"
    ur = "ur"
    uz = "uz"
    ve = "ve"
    vi = "vi"
    vo = "vo"
    wa = "wa"
    wo = "wo"
    xh = "xh"
    yi = "yi"
    yo = "yo"
    za = "za"
    zh = "zh"
    zu = "zu"


LANGUAGES: dict[LanguageCode, str] = {
    LanguageCode.aa: "Afar",
    LanguageCode.ab: "Abkhazian",
    LanguageCode.af: "Afrikaans",
    LanguageCode.ak: "Akan",
    LanguageCode.am: "Amharic",
    LanguageCode.an: "Aragonese",
    LanguageCode.ar: "Arabic",
    LanguageCode.as_: "Assamese",
    LanguageCode.az: "Azerbaijani",
    LanguageCode.ba: "Bashkir",
    LanguageCode.be: "Belarusian",
    LanguageCode.bg: "Bulgarian",
    LanguageCode.bm: "Bambara",
    LanguageCode.bn: "Bengali",
    LanguageCode.bo: "Tibetan",
    LanguageCode.br: "Breton",
    LanguageCode.bs: "Bosnian",
    LanguageCode.ca: "Catalan",
    LanguageCode.ce: "Chechen",
    LanguageCode.co: "Corsican",
    LanguageCode.cs: "Czech",
    LanguageCode.cv: "Chuvash",
    LanguageCode.cy: "Welsh",
    LanguageCode.da: "Danish",
    LanguageCode.de: "German",
    LanguageCode.dv: "Divehi",
    LanguageCode.dz: "Dzongkha",
    LanguageCode.ee: "Ewe",
    LanguageCode.el: "Greek",
    LanguageCode.en: "English",
    LanguageCode.eo: "Esperanto",
    LanguageCode.es: "Spanish",
    LanguageCode.et: "Estonian",
    LanguageCode.eu: "Basque",
    LanguageCode.fa: "Persian",
    LanguageCode.ff: "Fulah",
    LanguageCode.fi: "Finnish",
    LanguageCode.fil_PH: "Filipino",
    LanguageCode.fo: "Faroese",
    LanguageCode.fr: "French",
    LanguageCode.fy: "Western Frisian",
    LanguageCode.ga: "Irish",
    LanguageCode.gd: "Scottish Gaelic",
    LanguageCode.gl: "Galician",
    LanguageCode.gn: "Guarani",
    LanguageCode.gu: "Gujarati",
    LanguageCode.gv: "Manx",
    LanguageCode.ha: "Hausa",
    LanguageCode.he: "Hebrew",
    LanguageCode.hi: "Hindi",
    LanguageCode.hr: "Croatian",
    LanguageCode.ht: "Haitian",
    LanguageCode.hu: "Hungarian",
    LanguageCode.hy: "Armenian",
    LanguageCode.ia: "Interlingua",
    LanguageCode.id: "Indonesian",
    LanguageCode.ie: "Interlingue",
    LanguageCode.ig: "Igbo",
    LanguageCode.ii: "Sichuan Yi",
    LanguageCode.ik: "Inupiaq",
    LanguageCode.io: "Ido",
    LanguageCode.is_: "Icelandic",
    LanguageCode.it: "Italian",
    LanguageCode.iu: "Inuktitut",
    LanguageCode.ja: "Japanese",
    LanguageCode.jv: "Javanese",
    LanguageCode.ka: "Georgian",
    LanguageCode.ki: "Kikuyu",
    LanguageCode.kk: "Kazakh",
    LanguageCode.kl: "Kalaallisut",
    LanguageCode.km: "Central Khmer",
    LanguageCode.kn: "Kannada",
    LanguageCode.ko: "Korean",
    LanguageCode.ks: "Kashmiri",
    LanguageCode.ku: "Kurdish",
    LanguageCode.kw: "Cornish",
    LanguageCode.ky: "Kyrgyz",
    LanguageCode.la: "Latin",
    LanguageCode.lb: "Luxembourgish",
    LanguageCode.lg: "Ganda",
    LanguageCode.ln: "Lingala",
    LanguageCode.lo: "Lao",
    LanguageCode.lt: "Lithuanian",
    LanguageCode.lu: "Luba-Katanga",
    LanguageCode.lv: "Latvian",
    LanguageCode.mg: "Malagasy",
    LanguageCode.mi: "Maori",
    LanguageCode.mk: "Macedonian",
    LanguageCode.ml: "Malayalam",
    LanguageCode.mn: "Mongolian",
    LanguageCode.mr: "Marathi",
    LanguageCode.ms: "Malay",
    LanguageCode.mt: "Maltese",
    LanguageCode.my: "Burmese",
    LanguageCode.nb: "Norwegian Bokmål",
    LanguageCode.nd: "North Ndebele",
    LanguageCode.ne: "Nepali",
    LanguageCode.nl: "Dutch",
    LanguageCode.nn: "Norwegian Nynorsk",
    LanguageCode.no: "Norwegian",
    LanguageCode.nr: "South Ndebele",
    LanguageCode.nv: "Navajo",
    LanguageCode.ny: "Chichewa",
    LanguageCode.oc: "Occitan",
    LanguageCode.om: "Oromo",
    LanguageCode.or_: "Oriya",
    LanguageCode.os: "Ossetian",
    LanguageCode.pa: "Punjabi",
    LanguageCode.pl: "Polish",
    LanguageCode.ps: "Pashto",
    LanguageCode.pt: "Portuguese",
    LanguageCode.qu: "Quechua",
    LanguageCode.rm: "Romansh",
    LanguageCode.rn: "Rundi",
    LanguageCode.ro: "Romanian",
    LanguageCode.ru: "Russian",
    LanguageCode.rw: "Kinyarwanda",
    LanguageCode.sa: "Sanskrit",
    LanguageCode.sc: "Sardinian",
    LanguageCode.sd: "Sindhi",
    LanguageCode.se: "Northern Sami",
    LanguageCode.sg: "Sango",
    LanguageCode.si: "Sinhala",
    LanguageCode.sk: "Slovak",
    LanguageCode.sl: "Slovenian",
    LanguageCode.sn: "Shona",
    LanguageCode.so: "Somali",
    LanguageCode.sq: "Albanian",
    LanguageCode.sr: "Serbian",
    LanguageCode.ss: "Swati",
    LanguageCode.st: "Southern Sotho",
    LanguageCode.su: "Sundanese",
    LanguageCode.sv: "Swedish",
    LanguageCode.sw: "Swahili",
    LanguageCode.ta: "Tamil",
    LanguageCode.te: "Telugu",
    LanguageCode.tg: "Tajik",
    LanguageCode.th: "Thai",
    LanguageCode.ti: "Tigrinya",
    LanguageCode.tk: "Turkmen",
    LanguageCode.tl: "Tagalog",
    LanguageCode.tn: "Tswana",
    LanguageCode.to: "Tonga",
    LanguageCode.tr: "Turkish",
    LanguageCode.ts: "Tsonga",
    LanguageCode.tt: "Tatar",
    LanguageCode.ug: "Uyghur",
    LanguageCode.uk: "Ukrainian",
    LanguageCode.ur: "Urdu",
    LanguageCode.uz: "Uzbek",
    LanguageCode.ve: "Venda",
    LanguageCode.vi: "Vietnamese",
    LanguageCode.vo: "Volapük",
    LanguageCode.wa: "Walloon",
    LanguageCode.wo: "Wolof",
    LanguageCode.xh: "Xhosa",
    LanguageCode.yi: "Yiddish",
    LanguageCode.yo: "Yoruba",
    LanguageCode.za: "Zhuang",
    LanguageCode.zh: "Chinese",
    LanguageCode.zu: "Zulu",
}


def detect_language(
    model: FastText, texts: list[str], default: LanguageCode = LanguageCode.en
) -> LanguageCode:
    """
    Detects the dominant language from a list of texts.
    Returns the detected language code, or default (default English) if confidence is low.
    """
    if not texts:
        return default

    # Get top 3 predictions for each text to gather candidates
    labels, probabilities = model.predict(texts, k=3)

    score_sums: defaultdict[str, float] = defaultdict(float)

    # Aggregate scores for each language across all texts
    for text_labels, text_probs in zip(labels, probabilities):
        for label, prob in zip(text_labels, text_probs):
            # Clean label: "__label__en" -> "en"
            lang = label.replace("__label__", "")
            score_sums[lang] += float(prob)

    # Sort languages by score
    sorted_scores = sorted(score_sums.items(), key=lambda item: item[1], reverse=True)
    if not sorted_scores:
        return default

    best_lang_str, best_total_score = sorted_scores[0]

    # Calculate average score (total score / number of input texts)
    avg_score = best_total_score / len(texts)

    # Calculate ratio between top 1 and top 2
    if len(sorted_scores) > 1:
        second_best_score = sorted_scores[1][1]
        ratio = (
            best_total_score / second_best_score if second_best_score > 0 else math.inf
        )
    else:
        ratio = math.inf

    # Convert string to LanguageCode. Fallback to fallback_lang if prediction is unknown (safe guard)
    try:
        best_lang = LanguageCode(best_lang_str)
    except ValueError:
        # Fallback for languages that might be in FastText but not in our explicit supported list, or vice versa
        return default

    # Apply heuristics to decide if we trust the detection
    # 1. High confidence absolute score
    if avg_score >= 0.8:
        return best_lang

    # 2. Medium confidence but good relative margin (e.g. 3x better than next best)
    #    (Helps with short sentences like "Como estas?" where FastText is fairly sure but not 80% sure)
    if avg_score >= 0.6 and ratio > 3.0:
        return best_lang

    # 3. Lower confidence but very high relative margin
    #    (Helps with even shorter text or noisy text that strongly points to one language)
    if avg_score >= 0.4 and ratio > 5.0:
        return best_lang

    # Fallback if confidence is too low
    return default
