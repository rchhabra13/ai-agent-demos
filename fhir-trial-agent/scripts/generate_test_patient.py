#!/usr/bin/env python3
"""
Generate synthetic FHIR R4 Patient bundles for local testing.

No real patient data is used. Profiles are randomly generated using
clinically plausible but entirely fictional values.

Usage:
    python scripts/generate_test_patient.py
    python scripts/generate_test_patient.py --condition "breast cancer" --output patient.json
    python scripts/generate_test_patient.py --count 5 --output-dir ./test_patients/
"""

from __future__ import annotations

import argparse
import json
import random
import uuid
from datetime import date, timedelta
from pathlib import Path

# ── Condition templates ──────────────────────────────────────────────────────

CONDITION_TEMPLATES: dict[str, dict] = {
    "nsclc": {
        "display": "Non-small cell lung cancer",
        "icd10": "C34.10",
        "snomed": "254637007",
        "stages": ["Stage IIA", "Stage IIB", "Stage IIIA", "Stage IIIB", "Stage IV"],
        "medications": ["Pembrolizumab", "Carboplatin", "Paclitaxel", "Osimertinib", "Nivolumab"],
        "labs": [("Hemoglobin", "718-7", (8.5, 14.0), "g/dL"), ("LDH", "2532-0", (150, 600), "U/L")],
    },
    "breast cancer": {
        "display": "Breast cancer",
        "icd10": "C50.919",
        "snomed": "254837009",
        "stages": ["Stage I", "Stage II", "Stage III", "Stage IV"],
        "medications": ["Trastuzumab", "Pertuzumab", "Tamoxifen", "Letrozole", "Palbociclib"],
        "labs": [("CA 15-3", None, (20, 200), "U/mL"), ("Hemoglobin", "718-7", (9.0, 14.0), "g/dL")],
    },
    "colorectal cancer": {
        "display": "Colorectal cancer",
        "icd10": "C20",
        "snomed": "363346000",
        "stages": ["Stage II", "Stage III", "Stage IV"],
        "medications": ["FOLFOX", "Bevacizumab", "Cetuximab", "Capecitabine"],
        "labs": [("CEA", None, (2.0, 50.0), "ng/mL"), ("Hemoglobin", "718-7", (8.0, 13.0), "g/dL")],
    },
    "type 2 diabetes": {
        "display": "Type 2 diabetes mellitus",
        "icd10": "E11.9",
        "snomed": "44054006",
        "stages": [],
        "medications": ["Metformin", "Semaglutide", "Empagliflozin", "Insulin glargine"],
        "labs": [
            ("HbA1c", None, (6.5, 11.0), "%"),
            ("Creatinine", "2160-0", (0.7, 2.5), "mg/dL"),
            ("eGFR", "33914-3", (30, 90), "mL/min/1.73m2"),
        ],
    },
}


def random_date(start_year: int = 1945, end_year: int = 1990) -> date:
    start = date(start_year, 1, 1)
    end = date(end_year, 12, 31)
    return start + timedelta(days=random.randint(0, (end - start).days))


def random_onset_date() -> date:
    return date.today() - timedelta(days=random.randint(90, 900))


def build_patient_bundle(condition_key: str = "nsclc") -> dict:
    template = CONDITION_TEMPLATES.get(condition_key.lower(), CONDITION_TEMPLATES["nsclc"])
    patient_id = f"synthetic-{uuid.uuid4().hex[:8]}"
    gender = random.choice(["male", "female"])
    birth_date = random_date()
    stage = random.choice(template["stages"]) if template["stages"] else None
    ecog = random.choice([0, 1, 1, 1, 2])  # Weighted toward 0-1

    entries = []

    # Patient resource
    entries.append({
        "resource": {
            "resourceType": "Patient",
            "id": patient_id,
            "name": [{"use": "official", "family": "Synthetic", "given": ["Test"]}],
            "birthDate": birth_date.isoformat(),
            "gender": gender,
            "address": [{
                "city": random.choice(["Boston", "Chicago", "Houston", "Phoenix", "Los Angeles"]),
                "state": random.choice(["MA", "IL", "TX", "AZ", "CA"]),
                "postalCode": str(random.randint(10000, 99999)),
                "country": "United States",
            }],
        }
    })

    # Primary condition
    condition: dict = {
        "resourceType": "Condition",
        "id": f"cond-{uuid.uuid4().hex[:8]}",
        "clinicalStatus": {
            "coding": [{"system": "http://terminology.hl7.org/CodeSystem/condition-clinical", "code": "active"}]
        },
        "verificationStatus": {
            "coding": [{"system": "http://terminology.hl7.org/CodeSystem/condition-ver-status", "code": "confirmed"}]
        },
        "code": {
            "coding": [
                {"system": "http://snomed.info/sct", "code": template["snomed"], "display": template["display"]},
                {"system": "http://hl7.org/fhir/sid/icd-10", "code": template["icd10"]},
            ],
            "text": f"{template['display']}{', ' + stage if stage else ''}",
        },
        "onsetDateTime": random_onset_date().isoformat(),
        "subject": {"reference": f"Patient/{patient_id}"},
    }
    if stage:
        condition["stage"] = [{"summary": {"text": stage, "coding": [{"display": stage}]}}]
    entries.append({"resource": condition})

    # 1-2 medications
    meds = random.sample(template["medications"], k=min(2, len(template["medications"])))
    for med_name in meds:
        entries.append({
            "resource": {
                "resourceType": "MedicationRequest",
                "id": f"med-{uuid.uuid4().hex[:8]}",
                "status": "active",
                "intent": "order",
                "medicationCodeableConcept": {
                    "coding": [{"display": med_name}],
                    "text": med_name,
                },
                "subject": {"reference": f"Patient/{patient_id}"},
            }
        })

    # Lab values
    for lab_name, loinc, (low, high), unit in template["labs"]:
        value = round(random.uniform(low, high), 1)
        entries.append({
            "resource": {
                "resourceType": "Observation",
                "id": f"obs-{uuid.uuid4().hex[:8]}",
                "status": "final",
                "code": {
                    "coding": [{"system": "http://loinc.org", "code": loinc or "unknown", "display": lab_name}],
                    "text": lab_name,
                },
                "valueQuantity": {"value": value, "unit": unit},
                "effectiveDateTime": (date.today() - timedelta(days=random.randint(7, 60))).isoformat(),
                "subject": {"reference": f"Patient/{patient_id}"},
            }
        })

    # ECOG observation
    entries.append({
        "resource": {
            "resourceType": "Observation",
            "id": f"obs-ecog-{uuid.uuid4().hex[:8]}",
            "status": "final",
            "code": {
                "coding": [{"system": "http://loinc.org", "code": "10334-1", "display": "ECOG Performance Status"}]
            },
            "valueInteger": ecog,
            "effectiveDateTime": date.today().isoformat(),
            "subject": {"reference": f"Patient/{patient_id}"},
        }
    })

    return {
        "resourceType": "Bundle",
        "type": "searchset",
        "total": len(entries),
        "entry": entries,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate synthetic FHIR patient bundles for testing.")
    parser.add_argument(
        "--condition",
        default="nsclc",
        choices=list(CONDITION_TEMPLATES.keys()),
        help="Primary condition template",
    )
    parser.add_argument("--output", type=Path, default=None, help="Output file path (single patient)")
    parser.add_argument("--count", type=int, default=1, help="Number of patients to generate")
    parser.add_argument("--output-dir", type=Path, default=None, help="Directory for multiple patients")
    args = parser.parse_args()

    if args.count > 1 and args.output_dir:
        args.output_dir.mkdir(parents=True, exist_ok=True)
        for i in range(args.count):
            bundle = build_patient_bundle(args.condition)
            path = args.output_dir / f"patient_{i + 1:03d}.json"
            path.write_text(json.dumps(bundle, indent=2))
            print(f"  Written: {path}")
        print(f"\nGenerated {args.count} synthetic patients in {args.output_dir}/")
    else:
        bundle = build_patient_bundle(args.condition)
        output_str = json.dumps(bundle, indent=2)
        if args.output:
            args.output.write_text(output_str)
            print(f"Written to {args.output}")
        else:
            print(output_str)


if __name__ == "__main__":
    main()
