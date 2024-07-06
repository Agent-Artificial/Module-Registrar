from pydantic import BaseModel
from typing import Dict, Union, Optional, Any
from data_models import MinerRequest
from modules.translation.translation import Modality

import torch

from enum import Enum


class TASK_STRINGS(Enum):
    speech2text = "s2tt"
    speech2speech = "s2st"
    auto_speech_recognition = "asr"
    text2speech = "t2st"
    text2text = "t2tt"


class TARRGET_LANGUAGES(Enum):
    Afrikaans = "af"
    Amharic = "am"
    Arabic = "ar"
    Asturian = "ast"
    Azerbaijani = "az"
    Bashkir = "ba"
    Belarusian = "be"
    Bulgarian = "bg"
    Bengali = "bn"
    Breton = "br"
    Bosnian = "bs"
    CatalanValencia = "ca"
    Cebuano = "ceb"
    Czech = "cs"
    Welsh = "cy"
    Danish = "da"
    German = "de"
    Greeek = "el"
    English = "en"
    Spanish = "es"
    Estonian = "et"
    Persian = "fa"
    Fulah = "ff"
    Finnish = "fi"
    French = "fr"
    WesternFrisia = "fy"
    Irish = "ga"
    Gaelic_Scottish = "gd"
    Galician = "gl"
    Gujarati = "gu"
    Hausa = "ha"
    Hebrew = "he"
    Hindi = "hi"
    Croatian = "hr"
    Haitian_Creole = "ht"
    Hungarian = "hu"
    Armenian = "hy"
    Indonesian = "id"
    Igbo = "ig"
    Iloko = "ilo"
    Icelandic = "is"
    Italian = "it"
    Japanese = "ja"
    Javanese = "jv"
    Georgian = "ka"
    Kazakh = "kk"
    CentralKhme = "km"
    Kannada = "kn"
    Korean = "ko"
    Luxembourgish = "lb"
    Ganda = "lg"
    Lingala = "ln"
    Lao = "lo"
    Lithuanian = "lt"
    Latvian = "lv"
    Malagasy = "mg"
    Macedonian = "mk"
    Malayalam = "ml"
    Mongolian = "mn"
    Marathi = "mr"
    Malay = "ms"
    Burmese = "my"
    Nepali = "ne"
    Dutch_Flemish = "nl"
    Norwegian = "no"
    NorthernSoth = "ns"
    Occitan = "oc"
    Oriya = "or"
    Panjabi = "pa"
    Polish = "pl"
    Pushto = "ps"
    Portuguese = "pt"
    Romanian = "ro"
    Russian = "ru"
    Sindhi = "sd"
    Sinhala = "si"
    Slovak = "sk"
    Slovenian = "sl"
    Somali = "so"
    Albanian = "sq"
    Serbian = "sr"
    Swati = "ss"
    Sundanese = "su"
    Swedish = "sv"
    Swahili = "sw"
    Tamil = "ta"
    Thai = "th"
    Tagalog = "tl"
    Tswana = "tn"
    Turkish = "tr"
    Ukrainian = "uk"
    Urdu = "ur"
    Uzbek = "uz"
    Vietnamese = "vi"
    Wolof = "wo"
    Xhosa = "xh"
    Yiddish = "yi"
    Yoruba = "yo"
    Chinese = "zh"
    Zulu = "zu"
    

class ModuleConfig(BaseModel):
    model_name_or_card: Union[str, Any] = "seamlessM4T_V2_large"
    vocoder_name: str = "vocoder_v2" if model_name_or_card == "seamlessM4T_V2_large" else "vocoder_36langs"
    device: torch.device = torch.device(device="cuda:0")
    text_tokenizer: str = model_name_or_card
    apply_mintox: bool = True,
    dtype: Union[torch.float16, torch.float32] = torch.float16,
    input_modality: Optional[Modality] = None,
    output_modality: Optional[Modality] = None


class RequestData(BaseModel):
    input: str
    task_string: str
    target_language: str
    

class TranslationRequest(MinerRequest):
    request_data: RequestData
    inference_type: str = "translation"


