"""
SPG (Script Prompt Generator) — version GUI + CLI.

Fonctions principales :
- génération de prompts artistiques structurés ;
- contraintes strictes sur tous les champs ;
- fusion des styles externes depuis aesthetics.txt ;
- nationalité précise ou nationalité aléatoire ;
- mode terminal conservé.
"""

from __future__ import annotations

import argparse
import random
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Mapping, MutableMapping, Optional, Sequence, Set, Tuple, Union

try:
    import pyperclip  # type: ignore
except Exception:  # pragma: no cover
    pyperclip = None

from spg_data import (
    ACCESSORIES,
    ACTIONS,
    CLOTHING,
    EAR_SHAPES,
    ENVIRONMENTS,
    EYE_COLORS,
    EYE_SHAPES,
    FACE_SHAPES,
    HAIR_COLORS,
    HAIR_LENGTHS,
    HAIR_TYPES,
    IMAGE_TYPES,
    META_PROMPT,
    MORPHOLOGIES,
    MOUTH_SHAPES,
    NATIONALITIES,
    PHENOTYPES,
    RACES,
    SEXES,
    SKIN_COLORS,
    SKIN_TYPES,
)

APP_DIR = Path(__file__).resolve().parent
DEFAULT_STYLE_FILE = APP_DIR / "aesthetics.txt"

FieldName = str
OPTIONAL_LIST_FIELDS: Set[FieldName] = {"clothing", "accessory"}

BLOCKED_AESTHETIC_KEYWORDS = (
    "nazi",
    "white nationalist",
    "supremacist",
    "loli",
    "nymphet",
    "slutcore",
    "fetish",
    "bondage",
    "playboy",
)


def _canon(value: str) -> str:
    return " ".join(value.strip().lower().split())


def _clean_style_line(value: str) -> str:
    value = value.replace("\ufeff", "")
    value = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f]+", " ", value)
    return _canon(value)


def _is_safe_external_style(value: str) -> bool:
    lowered = value.lower()
    return not any(keyword in lowered for keyword in BLOCKED_AESTHETIC_KEYWORDS)


def load_aesthetics(file_path: Union[str, Path] = DEFAULT_STYLE_FILE) -> List[str]:
    """Charge les styles additionnels depuis un fichier texte, un style par ligne."""
    aesthetics: List[str] = []
    try:
        path = Path(file_path)
        if not path.exists() and not path.is_absolute():
            path = APP_DIR / path
        if path.exists():
            raw = path.read_text(encoding="utf-8", errors="replace")
            raw = raw.replace("\f", "\n")
            for line in raw.splitlines():
                cleaned = _clean_style_line(line)
                if cleaned and not cleaned.startswith("#") and _is_safe_external_style(cleaned):
                    aesthetics.append(cleaned)
    except Exception:
        pass

    seen: Set[str] = set()
    unique: List[str] = []
    for aesthetic in aesthetics:
        if aesthetic not in seen:
            unique.append(aesthetic)
            seen.add(aesthetic)
    return unique


def build_choice_fields(style_file: Union[str, Path] = DEFAULT_STYLE_FILE) -> Dict[str, Tuple[str, ...]]:
    """Construit les domaines de valeurs, avec fusion des styles externes."""
    base: Dict[str, Tuple[str, ...]] = {
        "image_type": tuple(map(_canon, IMAGE_TYPES)),
        "sex": tuple(map(_canon, SEXES)),
        "race": tuple(map(_canon, RACES)),
        "skin_type": tuple(map(_canon, SKIN_TYPES)),
        "skin_color": tuple(map(_canon, SKIN_COLORS)),
        "phenotype": tuple(map(_canon, PHENOTYPES)),
        "morphology": tuple(map(_canon, MORPHOLOGIES)),
        "face_shape": tuple(map(_canon, FACE_SHAPES)),
        "hair_type": tuple(map(_canon, HAIR_TYPES)),
        "hair_color": tuple(map(_canon, HAIR_COLORS)),
        "hair_length": tuple(map(_canon, HAIR_LENGTHS)),
        "ear_shape": tuple(map(_canon, EAR_SHAPES)),
        "eye_shape": tuple(map(_canon, EYE_SHAPES)),
        "eye_color": tuple(map(_canon, EYE_COLORS)),
        "mouth_shape": tuple(map(_canon, MOUTH_SHAPES)),
        "action": tuple(map(_canon, ACTIONS)),
        "environment": tuple(map(_canon, ENVIRONMENTS)),
        "accessory": tuple(map(_canon, ACCESSORIES)),
        "clothing": tuple(map(_canon, CLOTHING)),
        "nationality": tuple(map(_canon, NATIONALITIES)),
    }

    extra = load_aesthetics(style_file)
    if extra:
        merged = list(base["image_type"])
        merged.extend(style for style in extra if style not in merged)
        base["image_type"] = tuple(merged)
    return base


def _validate_values(
    choice_fields: Mapping[str, Sequence[str]],
    field_name: FieldName,
    values: Sequence[str],
) -> Tuple[List[str], List[str]]:
    allowed = set(map(_canon, choice_fields.get(field_name, ())))
    valid: List[str] = []
    invalid: List[str] = []
    for value in values:
        cleaned = _canon(value)
        if cleaned in allowed:
            valid.append(cleaned)
        else:
            invalid.append(cleaned)
    return valid, invalid


@dataclass
class Constraints:
    require: MutableMapping[FieldName, Set[str]] = field(default_factory=dict)
    forbid: MutableMapping[FieldName, Set[str]] = field(default_factory=dict)

    @staticmethod
    def from_pairs(
        choice_fields: Mapping[str, Sequence[str]],
        pairs_require: Sequence[str],
        pairs_forbid: Sequence[str],
    ) -> "Constraints":
        constraints = Constraints()

        def ingest(pairs: Sequence[str], target: MutableMapping[FieldName, Set[str]]) -> None:
            for pair in pairs:
                if "=" not in pair:
                    raise ValueError(f"Contrainte invalide : {pair}. Format attendu : champ=valeur1,valeur2")
                key, raw_values = pair.split("=", 1)
                key = _canon(key)
                if key not in choice_fields:
                    known = ", ".join(sorted(choice_fields.keys()))
                    raise ValueError(f"Champ inconnu : {key}. Champs disponibles : {known}")
                values = [_canon(v) for v in raw_values.replace("|", ",").split(",") if v.strip()]
                valid, invalid = _validate_values(choice_fields, key, values)
                if invalid:
                    allowed = ", ".join(sorted(map(_canon, choice_fields[key])))
                    raise ValueError(
                        f"Valeur invalide pour {key} : {', '.join(invalid)}. Valeurs autorisées : {allowed}"
                    )
                if not valid:
                    raise ValueError(f"Aucune valeur fournie pour {key}.")
                target.setdefault(key, set()).update(valid)

        ingest(pairs_require, constraints.require)
        ingest(pairs_forbid, constraints.forbid)

        for key, required_values in list(constraints.require.items()):
            overlap = required_values & constraints.forbid.get(key, set())
            if overlap:
                raise ValueError(
                    f"Conflit sur {key} : impossible de forcer et interdire {sorted(overlap)}"
                )
        return constraints

    @staticmethod
    def from_cli(
        choice_fields: Mapping[str, Sequence[str]],
        pairs_require: Sequence[str],
        pairs_forbid: Sequence[str],
    ) -> "Constraints":
        try:
            return Constraints.from_pairs(choice_fields, pairs_require, pairs_forbid)
        except ValueError as exc:
            raise SystemExit(str(exc)) from exc

    def copy(self) -> "Constraints":
        return Constraints(
            require={key: set(values) for key, values in self.require.items()},
            forbid={key: set(values) for key, values in self.forbid.items()},
        )

    def require_one(self, field_name: FieldName, value: str) -> None:
        self.require.setdefault(field_name, set()).add(_canon(value))

    def apply_filter(
        self,
        choice_fields: Mapping[str, Sequence[str]],
        field_name: FieldName,
        options: Sequence[str],
    ) -> List[str]:
        filtered = list(map(_canon, options))
        if field_name in self.require:
            required = self.require[field_name]
            filtered = [option for option in filtered if option in required]
        if field_name in self.forbid:
            forbidden = self.forbid[field_name]
            filtered = [option for option in filtered if option not in forbidden]
        return filtered


@dataclass
class PromptOptions:
    n: int = 3
    seed: Optional[int] = None
    min_age: int = 18
    max_age: int = 45
    copy_to_clipboard: bool = True
    constraints: Constraints = field(default_factory=Constraints)
    style_file: Union[str, Path] = DEFAULT_STYLE_FILE


def _rand_choice(rng: random.Random, sequence: Sequence[str]) -> str:
    items = tuple(sequence)
    if not items:
        return ""
    return rng.choice(items)


def _pick_with_constraints(
    rng: random.Random,
    choice_fields: Mapping[str, Sequence[str]],
    constraints: Constraints,
    field_name: FieldName,
) -> str:
    base = choice_fields[field_name]
    filtered = constraints.apply_filter(choice_fields, field_name, base)
    if not filtered:
        allowed = ", ".join(base)
        raise ValueError(
            f"Aucune option disponible pour {field_name} après application des contraintes. Valeurs initiales : {allowed}"
        )
    return _rand_choice(rng, filtered)


def validate_prompt_options(opts: PromptOptions) -> None:
    if opts.n < 1:
        raise ValueError("Le nombre de prompts doit être supérieur ou égal à 1.")
    if opts.min_age < 0:
        raise ValueError("L'âge minimum ne peut pas être négatif.")
    if opts.min_age > opts.max_age:
        raise ValueError("L'âge minimum ne peut pas être supérieur à l'âge maximum.")


def build_prompt(
    rng: random.Random,
    opts: PromptOptions,
    choice_fields: Mapping[str, Sequence[str]],
) -> str:
    validate_prompt_options(opts)

    age = rng.randint(opts.min_age, opts.max_age)
    style = _pick_with_constraints(rng, choice_fields, opts.constraints, "image_type")

    being = (
        f"{_pick_with_constraints(rng, choice_fields, opts.constraints, 'race')} "
        f"{_pick_with_constraints(rng, choice_fields, opts.constraints, 'sex')}"
    )
    origin = f"from {_pick_with_constraints(rng, choice_fields, opts.constraints, 'nationality')}"
    phenotype = f"{_pick_with_constraints(rng, choice_fields, opts.constraints, 'phenotype')} phenotype"
    skin = (
        f"{_pick_with_constraints(rng, choice_fields, opts.constraints, 'skin_type')} skin, "
        f"{_pick_with_constraints(rng, choice_fields, opts.constraints, 'skin_color')} skin color"
    )
    body_face = ", ".join(
        filter(
            None,
            (
                f"{_pick_with_constraints(rng, choice_fields, opts.constraints, 'morphology')} morphology",
                f"{_pick_with_constraints(rng, choice_fields, opts.constraints, 'face_shape')} face shape",
            ),
        )
    )
    hair = ", ".join(
        (
            f"{_pick_with_constraints(rng, choice_fields, opts.constraints, 'hair_type')} hair type",
            f"{_pick_with_constraints(rng, choice_fields, opts.constraints, 'hair_color')} hair color",
            f"{_pick_with_constraints(rng, choice_fields, opts.constraints, 'hair_length')} hair length",
        )
    )
    ears = f"{_pick_with_constraints(rng, choice_fields, opts.constraints, 'ear_shape')} ear shape"
    eyes = (
        f"{_pick_with_constraints(rng, choice_fields, opts.constraints, 'eye_shape')} eye shape, "
        f"{_pick_with_constraints(rng, choice_fields, opts.constraints, 'eye_color')} eye color"
    )
    mouth = _pick_with_constraints(rng, choice_fields, opts.constraints, "mouth_shape")

    optional_parts: List[str] = []
    for field_name, label in (("clothing", "wearing"), ("accessory", "with")):
        base = choice_fields[field_name]
        filtered = opts.constraints.apply_filter(choice_fields, field_name, base)
        if filtered:
            count = min(len(filtered), rng.randint(0, 2))
            if count:
                picks = rng.sample(filtered, k=count)
                optional_parts.append(f"{label} {', '.join(picks)}")

    environment = ""
    filtered_environment = opts.constraints.apply_filter(
        choice_fields,
        "environment",
        choice_fields["environment"],
    )
    if filtered_environment:
        environment = f"in {_rand_choice(rng, filtered_environment)}"

    action = _pick_with_constraints(rng, choice_fields, opts.constraints, "action")

    parts: List[str] = [
        f"{style} image of a {being}, {age} years old",
        origin,
        phenotype,
        skin,
        body_face,
        hair,
        ears,
        eyes,
        mouth,
        action,
        environment,
        *optional_parts,
        META_PROMPT,
    ]
    return ", ".join(part for part in parts if part)


def generate_prompts(
    opts: PromptOptions,
    choice_fields: Optional[Mapping[str, Sequence[str]]] = None,
) -> List[str]:
    validate_prompt_options(opts)
    fields = choice_fields or build_choice_fields(opts.style_file)
    rng = random.Random(opts.seed)
    return [build_prompt(rng, opts, fields) for _ in range(opts.n)]


def generate_prompts_with_nationality(
    nationality: Optional[str] = None,
    random_nationality: bool = False,
    n: int = 3,
    seed: Optional[int] = None,
    min_age: int = 18,
    max_age: int = 45,
    style_file: Union[str, Path] = DEFAULT_STYLE_FILE,
    base_constraints: Optional[Constraints] = None,
) -> List[str]:
    choice_fields = build_choice_fields(style_file)
    constraints = base_constraints.copy() if base_constraints else Constraints()

    if nationality and random_nationality:
        raise ValueError("Choisis soit une nationalité précise, soit une nationalité aléatoire, pas les deux.")

    if nationality:
        cleaned = _canon(nationality)
        valid, invalid = _validate_values(choice_fields, "nationality", [cleaned])
        if invalid or not valid:
            allowed = ", ".join(choice_fields["nationality"])
            raise ValueError(f"Nationalité inconnue : {nationality}. Valeurs disponibles : {allowed}")
        constraints.require_one("nationality", cleaned)

    opts = PromptOptions(
        n=n,
        seed=seed,
        min_age=min_age,
        max_age=max_age,
        copy_to_clipboard=False,
        constraints=constraints,
        style_file=style_file,
    )
    return generate_prompts(opts, choice_fields)


def build_output(prompts: Sequence[str]) -> str:
    return "\n\n".join(prompts)


def copy_to_clipboard(text: str) -> bool:
    if not text or pyperclip is None:
        return False
    try:
        pyperclip.copy(text)
        return True
    except Exception:
        return False


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate structured art prompts.")
    parser.add_argument("-n", "--num", dest="n", type=int, default=3, help="number of prompts to generate")
    parser.add_argument("--seed", type=int, default=None, help="random seed for reproducibility")
    parser.add_argument("--min-age", type=int, default=18, help="minimum age")
    parser.add_argument("--max-age", type=int, default=45, help="maximum age")
    parser.add_argument("--no-clipboard", action="store_true", help="disable copying to clipboard")
    parser.add_argument("--require", action="append", default=[], help="force choices: field=val1,val2")
    parser.add_argument("--forbid", action="append", default=[], help="forbid choices: field=val1,val2")
    parser.add_argument("--style-file", default=str(DEFAULT_STYLE_FILE), help="path to aesthetics.txt")
    parser.add_argument("--nationality", default=None, help="force one nationality, example: french")
    parser.add_argument("--random-nationality", action="store_true", help="keep nationality random")
    args = parser.parse_args()

    if args.n < 1:
        parser.error("--num must be at least 1")
    if args.min_age > args.max_age:
        parser.error("--min-age cannot be greater than --max-age")
    if args.nationality and args.random_nationality:
        parser.error("Use either --nationality or --random-nationality, not both")

    choice_fields = build_choice_fields(args.style_file)
    constraints = Constraints.from_cli(choice_fields, args.require, args.forbid)

    if args.nationality:
        cleaned_nationality = _canon(args.nationality)
        valid, invalid = _validate_values(choice_fields, "nationality", [cleaned_nationality])
        if invalid or not valid:
            parser.error(f"unknown nationality: {args.nationality}")
        constraints.require_one("nationality", cleaned_nationality)

    opts = PromptOptions(
        n=args.n,
        seed=args.seed,
        min_age=args.min_age,
        max_age=args.max_age,
        copy_to_clipboard=not args.no_clipboard,
        constraints=constraints,
        style_file=args.style_file,
    )

    try:
        output = build_output(generate_prompts(opts, choice_fields))
    except ValueError as exc:
        parser.error(str(exc))
        return

    print(output)

    if opts.copy_to_clipboard and copy_to_clipboard(output):
        print("\nCopied to clipboard.")


if __name__ == "__main__":
    main()
