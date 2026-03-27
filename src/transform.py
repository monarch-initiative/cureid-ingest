import uuid
from enum import Enum
from typing import Any

import koza
from biolink_model.datamodel.pydanticmodel_v2 import (
    AgentTypeEnum,
    Case,
    CaseToDiseaseAssociation,
    CaseToGeneAssociation,
    CaseToPhenotypicFeatureAssociation,
    ChemicalEntity,
    ChemicalEntityToDiseaseOrPhenotypicFeatureAssociation,
    ChemicalOrDrugOrTreatmentAdverseEventAssociation,
    Disease,
    FDAIDAAdverseEventEnum,
    Gene,
    KnowledgeLevelEnum,
    PhenotypicFeature,
)
from koza import KozaTransform

INFORES_CUREID = "infores:cureid"

# Namespace for deterministic UUIDs
_UUID_NAMESPACE = uuid.UUID("d6a2f389-4f7d-4e6b-a7f3-89c2e4b5d6a1")

NODE_CLASS_MAP = {
    "Drug": ChemicalEntity,
    "Disease": Disease,
    "Gene": Gene,
    "PhenotypicFeature": PhenotypicFeature,
    "AdverseEvent": PhenotypicFeature,
}


@koza.transform_record()
def transform_record(koza_transform: KozaTransform, row: dict[str, Any]) -> list:
    """Transform a single CURE ID record into Biolink entities and associations."""
    edge_type = row["association_category"]

    if edge_type == "biolink:DiseaseToPhenotypicFeatureAssociation":
        return _transform_disease_to_phenotype(row)
    elif edge_type == "biolink:GeneToDiseaseAssociation":
        return _transform_gene_to_disease(row)
    elif edge_type == "biolink:ChemicalToDiseaseOrPhenotypicFeatureAssociation":
        return _transform_chemical(row)
    elif edge_type in ("biolink:GeneToVariantAssociation", "biolink:VariantToDiseaseAssociation"):
        return []
    else:
        raise ValueError(f"Unhandled edge type: {edge_type} in record: {row}")


# ---------------------------------------------------------------------------
# Row-type transformers
# ---------------------------------------------------------------------------


def _transform_disease_to_phenotype(row: dict[str, Any]) -> list:
    """Disease→Phenotype row → Case + Disease + PhenotypicFeature + 2 edges."""
    case = _make_case_node(row)
    disease = Disease(id=row["subject_final_curie"], name=row["subject_final_label"])
    phenotype = PhenotypicFeature(id=row["object_final_curie"], name=row["object_final_label"])
    publications = _get_publications(row)

    case_to_disease = CaseToDiseaseAssociation(
        id=_deterministic_edge_id("CaseToDisease", row["report_id"], row["subject_final_curie"]),
        subject=case.id,
        predicate="biolink:has_disease",
        object=disease.id,
        primary_knowledge_source=INFORES_CUREID,
        aggregator_knowledge_source=["infores:monarchinitiative"],
        knowledge_level=KnowledgeLevelEnum.observation,
        agent_type=AgentTypeEnum.manual_agent,
        publications=publications or None,
    )

    case_to_phenotype = CaseToPhenotypicFeatureAssociation(
        id=_deterministic_edge_id("CaseToPhenotype", row["report_id"], row["object_final_curie"]),
        subject=case.id,
        predicate="biolink:has_phenotype",
        object=phenotype.id,
        disease_context_qualifier=disease.id,
        primary_knowledge_source=INFORES_CUREID,
        aggregator_knowledge_source=["infores:monarchinitiative"],
        knowledge_level=KnowledgeLevelEnum.observation,
        agent_type=AgentTypeEnum.manual_agent,
        publications=publications or None,
    )

    return [case, disease, phenotype, case_to_disease, case_to_phenotype]


def _transform_gene_to_disease(row: dict[str, Any]) -> list:
    """Gene→Disease row → Case + Gene + Disease + 2 edges."""
    case = _make_case_node(row)
    gene = Gene(id=row["subject_final_curie"], name=row["subject_final_label"])
    disease = Disease(id=row["object_final_curie"], name=row["object_final_label"])
    publications = _get_publications(row)

    case_to_disease = CaseToDiseaseAssociation(
        id=_deterministic_edge_id("CaseToDisease", row["report_id"], row["object_final_curie"]),
        subject=case.id,
        predicate="biolink:has_disease",
        object=disease.id,
        primary_knowledge_source=INFORES_CUREID,
        aggregator_knowledge_source=["infores:monarchinitiative"],
        knowledge_level=KnowledgeLevelEnum.observation,
        agent_type=AgentTypeEnum.manual_agent,
        publications=publications or None,
    )

    case_to_gene = CaseToGeneAssociation(
        id=_deterministic_edge_id("CaseToGene", row["report_id"], row["subject_final_curie"]),
        subject=case.id,
        predicate="biolink:has_gene",
        object=gene.id,
        primary_knowledge_source=INFORES_CUREID,
        aggregator_knowledge_source=["infores:monarchinitiative"],
        knowledge_level=KnowledgeLevelEnum.observation,
        agent_type=AgentTypeEnum.manual_agent,
        publications=publications or None,
    )

    return [case, gene, disease, case_to_disease, case_to_gene]


def _transform_chemical(row: dict[str, Any]) -> list:
    """Chemical→Disease/Phenotype/AdverseEvent row → ChemicalEntity + target + 1 edge."""
    subject_node = ChemicalEntity(id=row["subject_final_curie"], name=row["subject_final_label"])

    object_class = NODE_CLASS_MAP.get(row["object_type"])
    if object_class is None:
        raise ValueError(f"Unhandled object type: {row['object_type']} in record: {row}")
    object_node = object_class(id=row["object_final_curie"], name=row["object_final_label"])

    publications = _get_publications(row)

    if row["object_type"] == "AdverseEvent":
        edge = ChemicalOrDrugOrTreatmentAdverseEventAssociation(
            id=str(uuid.uuid4()),
            subject=subject_node.id,
            predicate=row["biolink_predicate"],
            object=object_node.id,
            FDA_adverse_event_level=get_adverse_event_level_from_outcomes(row["outcome"].split(";")),
            primary_knowledge_source=INFORES_CUREID,
            aggregator_knowledge_source=["infores:monarchinitiative"],
            knowledge_level=KnowledgeLevelEnum.observation,
            agent_type=AgentTypeEnum.manual_agent,
            publications=publications or None,
        )
    else:
        edge = ChemicalEntityToDiseaseOrPhenotypicFeatureAssociation(
            id=str(uuid.uuid4()),
            subject=subject_node.id,
            predicate=row["biolink_predicate"],
            object=object_node.id,
            primary_knowledge_source=INFORES_CUREID,
            aggregator_knowledge_source=["infores:monarchinitiative"],
            knowledge_level=KnowledgeLevelEnum.knowledge_assertion,
            agent_type=AgentTypeEnum.manual_agent,
            publications=publications or None,
        )

    return [subject_node, object_node, edge]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_case_node(row: dict[str, Any]) -> Case:
    return Case(
        id=f"CUREID:{row['report_id']}",
        iri=row["link"],
        in_taxon=["NCBITaxon:9606"],
    )


def _deterministic_edge_id(edge_type: str, report_id: str, target_curie: str) -> str:
    return str(uuid.uuid5(_UUID_NAMESPACE, f"{edge_type}-{report_id}-{target_curie}"))


def _get_publications(record: dict[str, Any]) -> list[str]:
    if record.get("pmid"):
        return [f"PMID:{record['pmid']}"]
    return []


# ---------------------------------------------------------------------------
# Adverse event mapping
# ---------------------------------------------------------------------------


class CUREIDAdverseEventEnum(str, Enum):
    death = "Death"
    life_threatening = "Life-threatening"
    hospitalization_initial_or_prolonged = "Hospitalization (initial or prolonged)"
    disability_or_permanent_damage = "Disability or Permanent Damage"
    congenital_anomaly_birth_defects = "Congenital Anomaly/Birth Defects"
    other_serious_or_important_medical_events = "Other Serious or Important Medical Events"
    required_intervention_to_prevent_permanent_impairment_damage = (
        "Required Intervention to Prevent Permanent Impairment/Damage"
    )
    non_serious_medical_event_requiring_intervention = "Non-serious Medical Event Requiring Intervention"
    non_serious_medical_event_not_requiring_intervention = "Non-serious Medical Event Not Requiring Intervention"
    treatment_was_discontinued_due_to_the_adverse_event = "Treatment was Discontinued due to the Adverse Event"
    unknown = "Unknown"


def parse_cureid_adverse_event(ae_string: str) -> CUREIDAdverseEventEnum:
    clean_ae_string = (
        ae_string.strip()
        .replace("-", "_")
        .replace(" ", "_")
        .replace("(", "")
        .replace(")", "")
        .replace("/", "_")
        .replace("<b>", "")
        .replace("</b>", "")
        .lower()
    )
    try:
        return CUREIDAdverseEventEnum[clean_ae_string]
    except (KeyError, ValueError):
        return CUREIDAdverseEventEnum.unknown


def get_adverse_event_level_from_outcomes(outcomes: list[str]) -> FDAIDAAdverseEventEnum:
    life_threatening_outcomes = [CUREIDAdverseEventEnum.death, CUREIDAdverseEventEnum.life_threatening]
    serious_outcomes = [
        CUREIDAdverseEventEnum.hospitalization_initial_or_prolonged,
        CUREIDAdverseEventEnum.disability_or_permanent_damage,
        CUREIDAdverseEventEnum.congenital_anomaly_birth_defects,
        CUREIDAdverseEventEnum.other_serious_or_important_medical_events,
        CUREIDAdverseEventEnum.treatment_was_discontinued_due_to_the_adverse_event,
        CUREIDAdverseEventEnum.required_intervention_to_prevent_permanent_impairment_damage,
    ]
    unexpected_outcomes = [
        CUREIDAdverseEventEnum.non_serious_medical_event_requiring_intervention,
        CUREIDAdverseEventEnum.non_serious_medical_event_not_requiring_intervention,
        CUREIDAdverseEventEnum.unknown,
    ]

    parsed_outcomes = [parse_cureid_adverse_event(outcome) for outcome in outcomes]

    if any(outcome in life_threatening_outcomes for outcome in parsed_outcomes):
        return FDAIDAAdverseEventEnum.life_threatening_adverse_event
    elif any(outcome in serious_outcomes for outcome in parsed_outcomes):
        return FDAIDAAdverseEventEnum.serious_adverse_event
    elif any(outcome in unexpected_outcomes for outcome in parsed_outcomes):
        return FDAIDAAdverseEventEnum.unexpected_adverse_event
    else:
        raise Exception(f"Unmapped Adverse Event: {outcomes}")
