from flask import session, redirect, url_for
from app import app
from os import getenv
import requests

def dict_html(dct):
    html = ''
    if type(dct) == list:
        
        html += '<table class="table table-bordered table-striped">\n' 
        for item in dct:
            html += '<tr><td>' + dict_html(item) + '</td></tr>'
        html += '</table>\n'

    elif type(dct) == dict:
        html += '<table class="table table-bordered table-striped"><thead><tr>'
        for key in dct.keys():
            html += '<th>' + str(key) + '</th>'
        html += '</thead></tr><tbody><tr>'
        for value in dct.values():
            html += '<td>' + dict_html(value) + '</td>'
        html += '</tr></tbody></table>\n'

    else:
        return str(dct)
    return str(html)


def img_helper(images):
    """returns {sm: 'url', md: 'url', lg: 'url'}"""

    sm = images[::-1][0]["url"]
    md = images[int(len(images)/2)]["url"]
    lg = images[0]["url"]

    return {"sm": sm, "md": md, "lg": lg}

def refresh_token(refresh_token):

    auth_token_url = f"{app.config['API_BASE']}/api/token"

    res = requests.post(auth_token_url, data = {
        "grant_type":"refresh_token",
        "refresh_token":refresh_token,
        "client_id":getenv("SPOTIPY_CLIENT_ID"),
        "client_secret":getenv("SPOTIPY_CLIENT_SECRET")
    })

    res_body = res.json()
    if res_body.get("refresh_token"):
        res_body["refresh_token"] = refresh_token

    return res_body.get("access_token")


countries = [
  {
    "code": "AD",
    "country": "Andorra"
  },
  {
    "code": "AE",
    "country": "United Arab Emirates"
  },
  {
    "code": "AF",
    "country": "Afghanistan"
  },
  {
    "code": "AG",
    "country": "Antigua and Barbuda"
  },
  {
    "code": "AI",
    "country": "Anguilla"
  },
  {
    "code": "AL",
    "country": "Albania"
  },
  {
    "code": "AM",
    "country": "Armenia"
  },
  {
    "code": "AO",
    "country": "Angola"
  },
  {
    "code": "AQ",
    "country": "Antarctica"
  },
  {
    "code": "AR",
    "country": "Argentina"
  },
  {
    "code": "AS",
    "country": "American Samoa"
  },
  {
    "code": "AT",
    "country": "Austria"
  },
  {
    "code": "AU",
    "country": "Australia"
  },
  {
    "code": "AW",
    "country": "Aruba"
  },
  {
    "code": "AX",
    "country": "Åland Islands"
  },
  {
    "code": "AZ",
    "country": "Azerbaijan"
  },
  {
    "code": "BA",
    "country": "Bosnia and Herzegovina"
  },
  {
    "code": "BB",
    "country": "Barbados"
  },
  {
    "code": "BD",
    "country": "Bangladesh"
  },
  {
    "code": "BE",
    "country": "Belgium"
  },
  {
    "code": "BF",
    "country": "Burkina Faso"
  },
  {
    "code": "BG",
    "country": "Bulgaria"
  },
  {
    "code": "BH",
    "country": "Bahrain"
  },
  {
    "code": "BI",
    "country": "Burundi"
  },
  {
    "code": "BJ",
    "country": "Benin"
  },
  {
    "code": "BL",
    "country": "Saint Barthélemy"
  },
  {
    "code": "BM",
    "country": "Bermuda"
  },
  {
    "code": "BN",
    "country": "Brunei Darussalam"
  },
  {
    "code": "BO",
    "country": "Bolivia (Plurinational State of)"
  },
  {
    "code": "BQ",
    "country": "Bonaire, Sint Eustatius and Saba"
  },
  {
    "code": "BR",
    "country": "Brazil"
  },
  {
    "code": "BS",
    "country": "Bahamas"
  },
  {
    "code": "BT",
    "country": "Bhutan"
  },
  {
    "code": "BV",
    "country": "Bouvet Island"
  },
  {
    "code": "BW",
    "country": "Botswana"
  },
  {
    "code": "BY",
    "country": "Belarus"
  },
  {
    "code": "BZ",
    "country": "Belize"
  },
  {
    "code": "CA",
    "country": "Canada"
  },
  {
    "code": "CC",
    "country": "Cocos (Keeling) Islands"
  },
  {
    "code": "CD",
    "country": "Congo, Democratic Republic of the"
  },
  {
    "code": "CF",
    "country": "Central African Republic"
  },
  {
    "code": "CG",
    "country": "Congo"
  },
  {
    "code": "CH",
    "country": "Switzerland"
  },
  {
    "code": "CI",
    "country": "Côte d'Ivoire"
  },
  {
    "code": "CK",
    "country": "Cook Islands"
  },
  {
    "code": "CL",
    "country": "Chile"
  },
  {
    "code": "CM",
    "country": "Cameroon"
  },
  {
    "code": "CN",
    "country": "China"
  },
  {
    "code": "CO",
    "country": "Colombia"
  },
  {
    "code": "CR",
    "country": "Costa Rica"
  },
  {
    "code": "CU",
    "country": "Cuba"
  },
  {
    "code": "CV",
    "country": "Cabo Verde"
  },
  {
    "code": "CW",
    "country": "Curaçao"
  },
  {
    "code": "CX",
    "country": "Christmas Island"
  },
  {
    "code": "CY",
    "country": "Cyprus"
  },
  {
    "code": "CZ",
    "country": "Czechia"
  },
  {
    "code": "DE",
    "country": "Germany"
  },
  {
    "code": "DJ",
    "country": "Djibouti"
  },
  {
    "code": "DK",
    "country": "Denmark"
  },
  {
    "code": "DM",
    "country": "Dominica"
  },
  {
    "code": "DO",
    "country": "Dominican Republic"
  },
  {
    "code": "DZ",
    "country": "Algeria"
  },
  {
    "code": "EC",
    "country": "Ecuador"
  },
  {
    "code": "EE",
    "country": "Estonia"
  },
  {
    "code": "EG",
    "country": "Egypt"
  },
  {
    "code": "EH",
    "country": "Western Sahara"
  },
  {
    "code": "ER",
    "country": "Eritrea"
  },
  {
    "code": "ES",
    "country": "Spain"
  },
  {
    "code": "ET",
    "country": "Ethiopia"
  },
  {
    "code": "FI",
    "country": "Finland"
  },
  {
    "code": "FJ",
    "country": "Fiji"
  },
  {
    "code": "FK",
    "country": "Falkland Islands (Malvinas)"
  },
  {
    "code": "FM",
    "country": "Micronesia (Federated States of)"
  },
  {
    "code": "FO",
    "country": "Faroe Islands"
  },
  {
    "code": "FR",
    "country": "France"
  },
  {
    "code": "GA",
    "country": "Gabon"
  },
  {
    "code": "GB",
    "country": "United Kingdom of Great Britain and Northern Ireland"
  },
  {
    "code": "GD",
    "country": "Grenada"
  },
  {
    "code": "GE",
    "country": "Georgia"
  },
  {
    "code": "GF",
    "country": "French Guiana"
  },
  {
    "code": "GG",
    "country": "Guernsey"
  },
  {
    "code": "GH",
    "country": "Ghana"
  },
  {
    "code": "GI",
    "country": "Gibraltar"
  },
  {
    "code": "GL",
    "country": "Greenland"
  },
  {
    "code": "GM",
    "country": "Gambia"
  },
  {
    "code": "GN",
    "country": "Guinea"
  },
  {
    "code": "GP",
    "country": "Guadeloupe"
  },
  {
    "code": "GQ",
    "country": "Equatorial Guinea"
  },
  {
    "code": "GR",
    "country": "Greece"
  },
  {
    "code": "GS",
    "country": "South Georgia and the South Sandwich Islands"
  },
  {
    "code": "GT",
    "country": "Guatemala"
  },
  {
    "code": "GU",
    "country": "Guam"
  },
  {
    "code": "GW",
    "country": "Guinea-Bissau"
  },
  {
    "code": "GY",
    "country": "Guyana"
  },
  {
    "code": "HK",
    "country": "Hong Kong"
  },
  {
    "code": "HM",
    "country": "Heard Island and McDonald Islands"
  },
  {
    "code": "HN",
    "country": "Honduras"
  },
  {
    "code": "HR",
    "country": "Croatia"
  },
  {
    "code": "HT",
    "country": "Haiti"
  },
  {
    "code": "HU",
    "country": "Hungary"
  },
  {
    "code": "ID",
    "country": "Indonesia"
  },
  {
    "code": "IE",
    "country": "Ireland"
  },
  {
    "code": "IL",
    "country": "Israel"
  },
  {
    "code": "IM",
    "country": "Isle of Man"
  },
  {
    "code": "IN",
    "country": "India"
  },
  {
    "code": "IO",
    "country": "British Indian Ocean Territory"
  },
  {
    "code": "IQ",
    "country": "Iraq"
  },
  {
    "code": "IR",
    "country": "Iran (Islamic Republic of)"
  },
  {
    "code": "IS",
    "country": "Iceland"
  },
  {
    "code": "IT",
    "country": "Italy"
  },
  {
    "code": "JE",
    "country": "Jersey"
  },
  {
    "code": "JM",
    "country": "Jamaica"
  },
  {
    "code": "JO",
    "country": "Jordan"
  },
  {
    "code": "JP",
    "country": "Japan"
  },
  {
    "code": "KE",
    "country": "Kenya"
  },
  {
    "code": "KG",
    "country": "Kyrgyzstan"
  },
  {
    "code": "KH",
    "country": "Cambodia"
  },
  {
    "code": "KI",
    "country": "Kiribati"
  },
  {
    "code": "KM",
    "country": "Comoros"
  },
  {
    "code": "KN",
    "country": "Saint Kitts and Nevis"
  },
  {
    "code": "KP",
    "country": "Korea (Democratic People's Republic of)"
  },
  {
    "code": "KR",
    "country": "Korea, Republic of"
  },
  {
    "code": "KW",
    "country": "Kuwait"
  },
  {
    "code": "KY",
    "country": "Cayman Islands"
  },
  {
    "code": "KZ",
    "country": "Kazakhstan"
  },
  {
    "code": "LA",
    "country": "Lao People's Democratic Republic"
  },
  {
    "code": "LB",
    "country": "Lebanon"
  },
  {
    "code": "LC",
    "country": "Saint Lucia"
  },
  {
    "code": "LI",
    "country": "Liechtenstein"
  },
  {
    "code": "LK",
    "country": "Sri Lanka"
  },
  {
    "code": "LR",
    "country": "Liberia"
  },
  {
    "code": "LS",
    "country": "Lesotho"
  },
  {
    "code": "LT",
    "country": "Lithuania"
  },
  {
    "code": "LU",
    "country": "Luxembourg"
  },
  {
    "code": "LV",
    "country": "Latvia"
  },
  {
    "code": "LY",
    "country": "Libya"
  },
  {
    "code": "MA",
    "country": "Morocco"
  },
  {
    "code": "MC",
    "country": "Monaco"
  },
  {
    "code": "MD",
    "country": "Moldova, Republic of"
  },
  {
    "code": "ME",
    "country": "Montenegro"
  },
  {
    "code": "MF",
    "country": "Saint Martin (French part)"
  },
  {
    "code": "MG",
    "country": "Madagascar"
  },
  {
    "code": "MH",
    "country": "Marshall Islands"
  },
  {
    "code": "MK",
    "country": "North Macedonia"
  },
  {
    "code": "ML",
    "country": "Mali"
  },
  {
    "code": "MM",
    "country": "Myanmar"
  },
  {
    "code": "MN",
    "country": "Mongolia"
  },
  {
    "code": "MO",
    "country": "Macao"
  },
  {
    "code": "MP",
    "country": "Northern Mariana Islands"
  },
  {
    "code": "MQ",
    "country": "Martinique"
  },
  {
    "code": "MR",
    "country": "Mauritania"
  },
  {
    "code": "MS",
    "country": "Montserrat"
  },
  {
    "code": "MT",
    "country": "Malta"
  },
  {
    "code": "MU",
    "country": "Mauritius"
  },
  {
    "code": "MV",
    "country": "Maldives"
  },
  {
    "code": "MW",
    "country": "Malawi"
  },
  {
    "code": "MX",
    "country": "Mexico"
  },
  {
    "code": "MY",
    "country": "Malaysia"
  },
  {
    "code": "MZ",
    "country": "Mozambique"
  },
  {
    "code": "NA",
    "country": "Namibia"
  },
  {
    "code": "NC",
    "country": "New Caledonia"
  },
  {
    "code": "NE",
    "country": "Niger"
  },
  {
    "code": "NF",
    "country": "Norfolk Island"
  },
  {
    "code": "NG",
    "country": "Nigeria"
  },
  {
    "code": "NI",
    "country": "Nicaragua"
  },
  {
    "code": "NL",
    "country": "Netherlands"
  },
  {
    "code": "NO",
    "country": "Norway"
  },
  {
    "code": "NP",
    "country": "Nepal"
  },
  {
    "code": "NR",
    "country": "Nauru"
  },
  {
    "code": "NU",
    "country": "Niue"
  },
  {
    "code": "NZ",
    "country": "New Zealand"
  },
  {
    "code": "OM",
    "country": "Oman"
  },
  {
    "code": "PA",
    "country": "Panama"
  },
  {
    "code": "PE",
    "country": "Peru"
  },
  {
    "code": "PF",
    "country": "French Polynesia"
  },
  {
    "code": "PG",
    "country": "Papua New Guinea"
  },
  {
    "code": "PH",
    "country": "Philippines"
  },
  {
    "code": "PK",
    "country": "Pakistan"
  },
  {
    "code": "PL",
    "country": "Poland"
  },
  {
    "code": "PM",
    "country": "Saint Pierre and Miquelon"
  },
  {
    "code": "PN",
    "country": "Pitcairn"
  },
  {
    "code": "PR",
    "country": "Puerto Rico"
  },
  {
    "code": "PS",
    "country": "Palestine, State of"
  },
  {
    "code": "PT",
    "country": "Portugal"
  },
  {
    "code": "PW",
    "country": "Palau"
  },
  {
    "code": "PY",
    "country": "Paraguay"
  },
  {
    "code": "QA",
    "country": "Qatar"
  },
  {
    "code": "RE",
    "country": "Réunion"
  },
  {
    "code": "RO",
    "country": "Romania"
  },
  {
    "code": "RS",
    "country": "Serbia"
  },
  {
    "code": "RU",
    "country": "Russian Federation"
  },
  {
    "code": "RW",
    "country": "Rwanda"
  },
  {
    "code": "SA",
    "country": "Saudi Arabia"
  },
  {
    "code": "SB",
    "country": "Solomon Islands"
  },
  {
    "code": "SC",
    "country": "Seychelles"
  },
  {
    "code": "SD",
    "country": "Sudan"
  },
  {
    "code": "SE",
    "country": "Sweden"
  },
  {
    "code": "SG",
    "country": "Singapore"
  },
  {
    "code": "SH",
    "country": "Saint Helena, Ascension and Tristan da Cunha"
  },
  {
    "code": "SI",
    "country": "Slovenia"
  },
  {
    "code": "SJ",
    "country": "Svalbard and Jan Mayen"
  },
  {
    "code": "SK",
    "country": "Slovakia"
  },
  {
    "code": "SL",
    "country": "Sierra Leone"
  },
  {
    "code": "SM",
    "country": "San Marino"
  },
  {
    "code": "SN",
    "country": "Senegal"
  },
  {
    "code": "SO",
    "country": "Somalia"
  },
  {
    "code": "SR",
    "country": "Suriname"
  },
  {
    "code": "SS",
    "country": "South Sudan"
  },
  {
    "code": "ST",
    "country": "Sao Tome and Principe"
  },
  {
    "code": "SV",
    "country": "El Salvador"
  },
  {
    "code": "SX",
    "country": "Sint Maarten (Dutch part)"
  },
  {
    "code": "SY",
    "country": "Syrian Arab Republic"
  },
  {
    "code": "SZ",
    "country": "Eswatini"
  },
  {
    "code": "TC",
    "country": "Turks and Caicos Islands"
  },
  {
    "code": "TD",
    "country": "Chad"
  },
  {
    "code": "TF",
    "country": "French Southern Territories"
  },
  {
    "code": "TG",
    "country": "Togo"
  },
  {
    "code": "TH",
    "country": "Thailand"
  },
  {
    "code": "TJ",
    "country": "Tajikistan"
  },
  {
    "code": "TK",
    "country": "Tokelau"
  },
  {
    "code": "TL",
    "country": "Timor-Leste"
  },
  {
    "code": "TM",
    "country": "Turkmenistan"
  },
  {
    "code": "TN",
    "country": "Tunisia"
  },
  {
    "code": "TO",
    "country": "Tonga"
  },
  {
    "code": "TR",
    "country": "Türkiye"
  },
  {
    "code": "TT",
    "country": "Trinidad and Tobago"
  },
  {
    "code": "TV",
    "country": "Tuvalu"
  },
  {
    "code": "TW",
    "country": "Taiwan, Province of China"
  },
  {
    "code": "TZ",
    "country": "Tanzania, United Republic of"
  },
  {
    "code": "UA",
    "country": "Ukraine"
  },
  {
    "code": "UG",
    "country": "Uganda"
  },
  {
    "code": "UM",
    "country": "United States Minor Outlying Islands"
  },
  {
    "code": "US",
    "country": "United States of America"
  },
  {
    "code": "UY",
    "country": "Uruguay"
  },
  {
    "code": "UZ",
    "country": "Uzbekistan"
  },
  {
    "code": "VA",
    "country": "Holy See"
  },
  {
    "code": "VC",
    "country": "Saint Vincent and the Grenadines"
  },
  {
    "code": "VE",
    "country": "Venezuela (Bolivarian Republic of)"
  },
  {
    "code": "VG",
    "country": "Virgin Islands (British)"
  },
  {
    "code": "VI",
    "country": "Virgin Islands (U.S.)"
  },
  {
    "code": "VN",
    "country": "Viet Nam"
  },
  {
    "code": "VU",
    "country": "Vanuatu"
  },
  {
    "code": "WF",
    "country": "Wallis and Futuna"
  },
  {
    "code": "WS",
    "country": "Samoa"
  },
  {
    "code": "YE",
    "country": "Yemen"
  },
  {
    "code": "YT",
    "country": "Mayotte"
  },
  {
    "code": "ZA",
    "country": "South Africa"
  },
  {
    "code": "ZM",
    "country": "Zambia"
  },
  {
    "code": "ZW",
    "country": "Zimbabwe"
  }
]