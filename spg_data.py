"""
SPG — Données statiques (version améliorée)
-------------------------------------------
Toutes les valeurs sont en minuscules, dédupliquées et corrigées.
Les listes servent de "domaines" de valeurs valides pour les contraintes.
Ajoute librement de nouvelles entrées si besoin (toujours en minuscules).
"""

# Types d'image / styles de rendu (complétés ; les styles externes d'aesthetics.txt
# seront fusionnés à l'exécution dans main.py → champ "image_type").
IMAGE_TYPES = (
    "photo",
    "photorealistic",
)

# Attributs d'identité
SEXES = (
    "male",
    "female",
)

RACES = (
    "human",
    "alien",
)

# Peau
SKIN_TYPES = (
    "normal",
    "vitiligo",
    "fur",
)

# Couleurs de peau (corrigées et enrichies légèrement)
SKIN_COLORS = (
    "pale",
    "ivory",
    "porcelain",
    "warm ivory",
    "sand",
    "limestone",
    "beige",
    "sienna",
    "honey",
    "tan",
    "almond",
    "chestnut",
    "bronze",
    "umber",
    "golden",
    "espresso",
    "cacao",
)

# Phénotypes géographiques (catégories larges et imparfaites — usage responsable)
PHENOTYPES = (
    "caucasian",
    "north african",
    "middle eastern",
    "sub-saharan african",
    "east asian",
    "south asian",
    "native american",
    "oceanic",
    "melanesian",
    "polynesian",
    "australian aboriginal",
)

# Morphologies / visage
MORPHOLOGIES = (
    "bottom hourglass",
    "inverted triangle",
    "round",
    "diamond",
    "athletic",
)

FACE_SHAPES = (
    "oval",
    "square",
    "round",
    "diamond",
    "long",
    "heart",
    "triangle",
    "inverted triangle",
    "rectangle",
    "oblong",
    "angular round",
)

# Cheveux
HAIR_TYPES = (
    "straight",
    "wavy",
    "curly",
    "kinky",
)

HAIR_COLORS = (
    "black",
    "brown",
    "blonde",
    "auburn",
    "ginger",
)

HAIR_LENGTHS = (
    "short",
    "medium",
    "long",
    "extremely long",
)

# Oreilles
EAR_SHAPES = (
    "small",
    "big",
    "attached lobe",
    "round",
    "square",
    "pointed",
)

# Yeux
EYE_SHAPES = (
    "round",
    "roundish-almond",
    "almond",
    "thin almond",
    "droopy",
    "droopy hooded",
    "hooded",
    "asian",
    "childish round asian",
)

EYE_COLORS = (
    "brown",
    "blue",
    "green",
    "amber",
    "hazel",
    "grey",
    "greyish blue",
    "deep blue",
    "dark green",
    "forest green",
    "dark hazel",
    "spring green",
    "greenish blue",
    "yellowish green",
    "freckled hazel",
)

# Bouche
MOUTH_SHAPES = (
    "full lips",
    "heavy upper lips",
    "wide lips",
    "heavy lower lips",
    "thin lips",
    "heart shaped lips",
    "downward-turned lips",
)

# Catégories optionnelles (tu peux enrichir librement)
CLOTHING = (
    "leather jacket", "hoodie", "kimono"
)

ENVIRONMENTS = (
    "night city street", "studio background", "forest clearing"
)

ACTIONS = (
    "selfie",
    "portrait",
    "standing pose",
    "close-up",
    "professional photography",
    "cinematic portrait",
    "editorial portrait",
    "studio photoshoot",
)

ACCESSORIES = (
    "glasses", "earrings", "scarf"
)

# Qualité globale / métadonnées
META_PROMPT = "8k, high quality, ultra photorealistic, iphone shot, iphone image quality"

# Nationalités (forme adjectivale, en minuscules)
NATIONALITIES = (
    "afghan", "albanian", "algerian", "american", "andorran", "angolan", "antiguans",
    "argentinean", "armenian", "australian", "austrian", "azerbaijani", "bahamian",
    "bahraini", "bangladeshi", "barbadian", "barbudans", "batswana", "belarusian",
    "belgian", "belizean", "beninese", "bhutanese", "bolivian", "bosnian", "brazilian",
    "british", "bruneian", "bulgarian", "burkinabe", "burmese", "burundian",
    "cambodian", "cameroonian", "canadian", "cape verdean", "central african",
    "chadian", "chilean", "chinese", "colombian", "comoran", "congolese",
    "costa rican", "croatian", "cuban", "cypriot", "czech", "danish", "djibouti",
    "dominican", "dutch", "dutchman", "dutchwoman", "east timorese", "ecuadorean",
    "egyptian", "emirian", "equatorial guinean", "eritrean", "estonian", "ethiopian",
    "fijian", "filipino", "finnish", "french", "gabonese", "gambian", "georgian",
    "german", "ghanaian", "greek", "grenadian", "guatemalan", "guinea-bissauan",
    "guinean", "guyanese", "haitian", "herzegovinian", "honduran", "hungarian",
    "i-kiribati", "icelander", "indian", "indonesian", "iranian", "iraqi", "irish",
    "israeli", "italian", "ivorian", "jamaican", "japanese", "jordanian",
    "kazakhstani", "kenyan", "kittian and nevisian", "kuwaiti", "kyrgyz", "laotian",
    "latvian", "lebanese", "liberian", "libyan", "liechtensteiner", "lithuanian",
    "luxembourger", "macedonian", "malagasy", "malawian", "malaysian", "maldivan",
    "malian", "maltese", "marshallese", "mauritanian", "mauritian", "mexican",
    "micronesian", "moldovan", "monacan", "mongolian", "moroccan", "mosotho",
    "motswana", "mozambican", "namibian", "nauruan", "nepalese", "netherlander",
    "new zealander", "ni-vanuatu", "nicaraguan", "nigerian", "nigerien",
    "north korean", "northern irish", "norwegian", "omani", "pakistani", "palauan",
    "panamanian", "papua new guinean", "paraguayan", "peruvian", "polish",
    "portuguese", "qatari", "romanian", "russian", "rwandan", "saint lucian",
    "salvadoran", "samoan", "san marinese", "sao tomean", "saudi", "scottish",
    "senegalese", "serbian", "seychellois", "sierra leonean", "singaporean",
    "slovakian", "slovenian", "solomon islander", "somali", "south african",
    "south korean", "spanish", "sri lankan", "sudanese", "surinamer", "swazi",
    "swedish", "swiss", "syrian", "taiwanese", "tajik", "tanzanian", "thai",
    "togolese", "tongan", "trinidadian or tobagonian", "tunisian", "turkish",
    "tuvaluan", "ugandan", "ukrainian", "uruguayan", "uzbekistani", "venezuelan",
    "vietnamese", "welsh", "yemenite", "zambian", "zimbabwean",
)
