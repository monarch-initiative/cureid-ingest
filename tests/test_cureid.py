import pytest
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

from transform import get_adverse_event_level_from_outcomes, transform_record

# ---------------------------------------------------------------------------
# Fixtures — one per source row type
# ---------------------------------------------------------------------------


@pytest.fixture
def disease_to_phenotype_row():
    """A row representing a disease → has_phenotype → phenotypic feature."""
    return {
        "subject_label_original": "Noonan syndrome",
        "subject_label": "Noonan syndrome",
        "subject_type": "Disease",
        "subject_final_label": "Noonan syndrome",
        "subject_final_curie": "MONDO:0018542",
        "subject_missing_final": "",
        "predicate_raw": "has_phenotype",
        "biolink_predicate": "biolink:has_phenotype",
        "association_category": "biolink:DiseaseToPhenotypicFeatureAssociation",
        "object_label_original": "Short stature",
        "object_label": "Short stature",
        "object_type": "PhenotypicFeature",
        "object_final_label": "Short stature",
        "object_final_curie": "HP:0004322",
        "object_missing_final": "",
        "report_id": "1",
        "pmid": "12345678",
        "link": "https://cure.ncats.io/case/1",
        "outcome": "",
    }


@pytest.fixture
def gene_to_disease_row():
    """A row representing a gene → gene_associated_with_condition → disease."""
    return {
        "subject_label_original": "BRAF",
        "subject_label": "BRAF",
        "subject_type": "Gene",
        "subject_final_label": "BRAF",
        "subject_final_curie": "NCBIGene:673",
        "subject_missing_final": "",
        "predicate_raw": "gene_associated_with_condition",
        "biolink_predicate": "biolink:gene_associated_with_condition",
        "association_category": "biolink:GeneToDiseaseAssociation",
        "object_label_original": "Noonan syndrome",
        "object_label": "Noonan syndrome",
        "object_type": "Disease",
        "object_final_label": "Noonan syndrome",
        "object_final_curie": "MONDO:0018542",
        "object_missing_final": "",
        "report_id": "1",
        "pmid": "12345678",
        "link": "https://cure.ncats.io/case/1",
        "outcome": "",
    }


@pytest.fixture
def chemical_to_disease_row():
    """A row representing a chemical → applied_to_treat → disease."""
    return {
        "subject_label_original": "Trametinib",
        "subject_label": "Trametinib",
        "subject_type": "Drug",
        "subject_final_label": "trametinib",
        "subject_final_curie": "CHEBI:75998",
        "subject_missing_final": "",
        "predicate_raw": "applied_to_treat",
        "biolink_predicate": "biolink:applied_to_treat",
        "association_category": "biolink:ChemicalToDiseaseOrPhenotypicFeatureAssociation",
        "object_label_original": "Noonan syndrome",
        "object_label": "Noonan syndrome",
        "object_type": "Disease",
        "object_final_label": "Noonan syndrome",
        "object_final_curie": "MONDO:0018542",
        "object_missing_final": "",
        "report_id": "1",
        "pmid": "12345678",
        "link": "https://cure.ncats.io/case/1",
        "outcome": "",
    }


@pytest.fixture
def chemical_to_phenotype_row():
    """A row representing a chemical → applied_to_treat → phenotypic feature."""
    return {
        "subject_label_original": "Trametinib",
        "subject_label": "Trametinib",
        "subject_type": "Drug",
        "subject_final_label": "trametinib",
        "subject_final_curie": "CHEBI:75998",
        "subject_missing_final": "",
        "predicate_raw": "applied_to_treat",
        "biolink_predicate": "biolink:applied_to_treat",
        "association_category": "biolink:ChemicalToDiseaseOrPhenotypicFeatureAssociation",
        "object_label_original": "Short stature",
        "object_label": "Short stature",
        "object_type": "PhenotypicFeature",
        "object_final_label": "Short stature",
        "object_final_curie": "HP:0004322",
        "object_missing_final": "",
        "report_id": "1",
        "pmid": "12345678",
        "link": "https://cure.ncats.io/case/1",
        "outcome": "",
    }


@pytest.fixture
def adverse_event_row():
    """A row representing a chemical with an adverse event."""
    return {
        "subject_label_original": "Trametinib",
        "subject_label": "Trametinib",
        "subject_type": "Drug",
        "subject_final_label": "trametinib",
        "subject_final_curie": "CHEBI:75998",
        "subject_missing_final": "",
        "predicate_raw": "has_adverse_event",
        "biolink_predicate": "biolink:has_adverse_event",
        "association_category": "biolink:ChemicalToDiseaseOrPhenotypicFeatureAssociation",
        "object_label_original": "Rash",
        "object_label": "Rash",
        "object_type": "AdverseEvent",
        "object_final_label": "Rash",
        "object_final_curie": "HP:0000988",
        "object_missing_final": "",
        "report_id": "1",
        "pmid": "12345678",
        "link": "https://cure.ncats.io/case/1",
        "outcome": "Non-serious Medical Event Not Requiring Intervention",
    }


@pytest.fixture
def gene_to_variant_row():
    """A row representing gene → has_sequence_variant → variant (skipped)."""
    return {
        "subject_label_original": "BRAF",
        "subject_label": "BRAF",
        "subject_type": "Gene",
        "subject_final_label": "BRAF",
        "subject_final_curie": "NCBIGene:673",
        "subject_missing_final": "",
        "predicate_raw": "has_sequence_variant",
        "biolink_predicate": "biolink:has_sequence_variant",
        "association_category": "biolink:GeneToVariantAssociation",
        "object_label_original": "V600E",
        "object_label": "V600E",
        "object_type": "SequenceVariant",
        "object_final_label": "V600E",
        "object_final_curie": "",
        "object_missing_final": "True",
        "report_id": "1",
        "pmid": "12345678",
        "link": "https://cure.ncats.io/case/1",
        "outcome": "",
    }


@pytest.fixture
def variant_to_disease_row():
    """A row representing variant → genetically_associated_with → disease (skipped)."""
    return {
        "subject_label_original": "V600E",
        "subject_label": "V600E",
        "subject_type": "SequenceVariant",
        "subject_final_label": "V600E",
        "subject_final_curie": "",
        "subject_missing_final": "True",
        "predicate_raw": "genetically_associated_with",
        "biolink_predicate": "biolink:genetically_associated_with",
        "association_category": "biolink:VariantToDiseaseAssociation",
        "object_label_original": "Noonan syndrome",
        "object_label": "Noonan syndrome",
        "object_type": "Disease",
        "object_final_label": "Noonan syndrome",
        "object_final_curie": "MONDO:0018542",
        "object_missing_final": "",
        "report_id": "1",
        "pmid": "12345678",
        "link": "https://cure.ncats.io/case/1",
        "outcome": "",
    }


# ---------------------------------------------------------------------------
# Case + Disease + Phenotype (from disease→phenotype source rows)
# ---------------------------------------------------------------------------


class TestCaseDiseaseAndPhenotype:
    def test_entity_count(self, disease_to_phenotype_row):
        entities = transform_record(None, disease_to_phenotype_row)
        assert len(entities) == 5  # Case + Disease + PhenotypicFeature + 2 edges

    def test_case_node(self, disease_to_phenotype_row):
        entities = transform_record(None, disease_to_phenotype_row)
        case = entities[0]
        assert isinstance(case, Case)
        assert case.id == "CUREID:1"
        assert case.iri == "https://cure.ncats.io/case/1"
        assert case.in_taxon == ["NCBITaxon:9606"]

    def test_disease_node(self, disease_to_phenotype_row):
        entities = transform_record(None, disease_to_phenotype_row)
        disease = entities[1]
        assert isinstance(disease, Disease)
        assert disease.id == "MONDO:0018542"

    def test_phenotype_node(self, disease_to_phenotype_row):
        entities = transform_record(None, disease_to_phenotype_row)
        phenotype = entities[2]
        assert isinstance(phenotype, PhenotypicFeature)
        assert phenotype.id == "HP:0004322"

    def test_case_to_disease_edge(self, disease_to_phenotype_row):
        entities = transform_record(None, disease_to_phenotype_row)
        edge = entities[3]
        assert isinstance(edge, CaseToDiseaseAssociation)
        assert edge.subject == "CUREID:1"
        assert edge.object == "MONDO:0018542"
        assert edge.predicate == "biolink:has_disease"
        assert edge.knowledge_level == KnowledgeLevelEnum.observation
        assert edge.agent_type == AgentTypeEnum.manual_agent

    def test_case_to_phenotype_edge(self, disease_to_phenotype_row):
        entities = transform_record(None, disease_to_phenotype_row)
        edge = entities[4]
        assert isinstance(edge, CaseToPhenotypicFeatureAssociation)
        assert edge.subject == "CUREID:1"
        assert edge.object == "HP:0004322"
        assert edge.predicate == "biolink:has_phenotype"
        assert edge.disease_context_qualifier == "MONDO:0018542"
        assert edge.knowledge_level == KnowledgeLevelEnum.observation
        assert edge.agent_type == AgentTypeEnum.manual_agent

    def test_deterministic_edge_ids(self, disease_to_phenotype_row):
        """Same row should produce same edge IDs."""
        entities_a = transform_record(None, disease_to_phenotype_row)
        entities_b = transform_record(None, disease_to_phenotype_row)
        assert entities_a[3].id == entities_b[3].id  # Case→Disease
        assert entities_a[4].id == entities_b[4].id  # Case→Phenotype

    def test_publications(self, disease_to_phenotype_row):
        entities = transform_record(None, disease_to_phenotype_row)
        edge = entities[3]
        assert edge.publications == ["PMID:12345678"]


# ---------------------------------------------------------------------------
# Case + Disease + Gene (from gene→disease source rows)
# ---------------------------------------------------------------------------


class TestCaseDiseaseAndGene:
    def test_entity_count(self, gene_to_disease_row):
        entities = transform_record(None, gene_to_disease_row)
        assert len(entities) == 5  # Case + Gene + Disease + 2 edges

    def test_case_node(self, gene_to_disease_row):
        entities = transform_record(None, gene_to_disease_row)
        case = entities[0]
        assert isinstance(case, Case)
        assert case.id == "CUREID:1"

    def test_gene_node(self, gene_to_disease_row):
        entities = transform_record(None, gene_to_disease_row)
        gene = entities[1]
        assert isinstance(gene, Gene)
        assert gene.id == "NCBIGene:673"

    def test_disease_node(self, gene_to_disease_row):
        entities = transform_record(None, gene_to_disease_row)
        disease = entities[2]
        assert isinstance(disease, Disease)
        assert disease.id == "MONDO:0018542"

    def test_case_to_disease_edge(self, gene_to_disease_row):
        entities = transform_record(None, gene_to_disease_row)
        edge = entities[3]
        assert isinstance(edge, CaseToDiseaseAssociation)
        assert edge.subject == "CUREID:1"
        assert edge.object == "MONDO:0018542"
        assert edge.predicate == "biolink:has_disease"

    def test_case_to_gene_edge(self, gene_to_disease_row):
        entities = transform_record(None, gene_to_disease_row)
        edge = entities[4]
        assert isinstance(edge, CaseToGeneAssociation)
        assert edge.subject == "CUREID:1"
        assert edge.object == "NCBIGene:673"
        assert edge.predicate == "biolink:has_gene"
        assert edge.knowledge_level == KnowledgeLevelEnum.observation

    def test_deterministic_edge_ids(self, gene_to_disease_row):
        entities_a = transform_record(None, gene_to_disease_row)
        entities_b = transform_record(None, gene_to_disease_row)
        assert entities_a[3].id == entities_b[3].id
        assert entities_a[4].id == entities_b[4].id


# ---------------------------------------------------------------------------
# Chemical → Disease rows → ChemicalEntity + Disease + 1 edge (no Case)
# ---------------------------------------------------------------------------


class TestChemicalToDisease:
    def test_entity_count(self, chemical_to_disease_row):
        entities = transform_record(None, chemical_to_disease_row)
        assert len(entities) == 3

    def test_subject_is_chemical_entity(self, chemical_to_disease_row):
        entities = transform_record(None, chemical_to_disease_row)
        assert isinstance(entities[0], ChemicalEntity)
        assert entities[0].id == "CHEBI:75998"
        assert entities[0].name == "trametinib"

    def test_object_is_disease(self, chemical_to_disease_row):
        entities = transform_record(None, chemical_to_disease_row)
        assert isinstance(entities[1], Disease)
        assert entities[1].id == "MONDO:0018542"

    def test_edge_is_chemical_to_disease_association(self, chemical_to_disease_row):
        entities = transform_record(None, chemical_to_disease_row)
        edge = entities[2]
        assert isinstance(edge, ChemicalEntityToDiseaseOrPhenotypicFeatureAssociation)
        assert edge.subject == "CHEBI:75998"
        assert edge.object == "MONDO:0018542"
        assert edge.predicate == "biolink:applied_to_treat"
        assert edge.knowledge_level == KnowledgeLevelEnum.knowledge_assertion

    def test_no_case_node(self, chemical_to_disease_row):
        entities = transform_record(None, chemical_to_disease_row)
        assert not any(isinstance(e, Case) for e in entities)

    def test_publication_is_set(self, chemical_to_disease_row):
        entities = transform_record(None, chemical_to_disease_row)
        edge = entities[2]
        assert "PMID:12345678" in edge.publications


# ---------------------------------------------------------------------------
# Chemical → Phenotype rows → ChemicalEntity + PhenotypicFeature + 1 edge
# ---------------------------------------------------------------------------


class TestChemicalToPhenotype:
    def test_entity_count(self, chemical_to_phenotype_row):
        entities = transform_record(None, chemical_to_phenotype_row)
        assert len(entities) == 3

    def test_subject_is_chemical_entity(self, chemical_to_phenotype_row):
        entities = transform_record(None, chemical_to_phenotype_row)
        assert isinstance(entities[0], ChemicalEntity)

    def test_object_is_phenotypic_feature(self, chemical_to_phenotype_row):
        entities = transform_record(None, chemical_to_phenotype_row)
        assert isinstance(entities[1], PhenotypicFeature)
        assert entities[1].id == "HP:0004322"

    def test_edge_predicate(self, chemical_to_phenotype_row):
        entities = transform_record(None, chemical_to_phenotype_row)
        edge = entities[2]
        assert isinstance(edge, ChemicalEntityToDiseaseOrPhenotypicFeatureAssociation)
        assert edge.predicate == "biolink:applied_to_treat"

    def test_no_case_node(self, chemical_to_phenotype_row):
        entities = transform_record(None, chemical_to_phenotype_row)
        assert not any(isinstance(e, Case) for e in entities)


# ---------------------------------------------------------------------------
# Adverse event rows → ChemicalEntity + PhenotypicFeature + 1 edge
# ---------------------------------------------------------------------------


class TestAdverseEvent:
    def test_produces_adverse_event_association(self, adverse_event_row):
        entities = transform_record(None, adverse_event_row)
        edge = entities[2]
        assert isinstance(edge, ChemicalOrDrugOrTreatmentAdverseEventAssociation)
        assert edge.FDA_adverse_event_level == FDAIDAAdverseEventEnum.unexpected_adverse_event
        assert edge.knowledge_level == KnowledgeLevelEnum.observation

    def test_adverse_event_object_is_phenotypic_feature(self, adverse_event_row):
        entities = transform_record(None, adverse_event_row)
        assert isinstance(entities[1], PhenotypicFeature)

    def test_no_case_node(self, adverse_event_row):
        entities = transform_record(None, adverse_event_row)
        assert not any(isinstance(e, Case) for e in entities)


# ---------------------------------------------------------------------------
# Skipped row types
# ---------------------------------------------------------------------------


class TestSkippedRows:
    def test_gene_to_variant_returns_empty(self, gene_to_variant_row):
        entities = transform_record(None, gene_to_variant_row)
        assert entities == []

    def test_variant_to_disease_returns_empty(self, variant_to_disease_row):
        entities = transform_record(None, variant_to_disease_row)
        assert entities == []


# ---------------------------------------------------------------------------
# Adverse event level mapping (unchanged)
# ---------------------------------------------------------------------------


class TestAdverseEventLevelMapping:
    def test_life_threatening(self):
        level = get_adverse_event_level_from_outcomes(["Death"])
        assert level == FDAIDAAdverseEventEnum.life_threatening_adverse_event

    def test_serious(self):
        level = get_adverse_event_level_from_outcomes(["Hospitalization (initial or prolonged)"])
        assert level == FDAIDAAdverseEventEnum.serious_adverse_event

    def test_unexpected(self):
        level = get_adverse_event_level_from_outcomes(["Non-serious Medical Event Not Requiring Intervention"])
        assert level == FDAIDAAdverseEventEnum.unexpected_adverse_event

    def test_multiple_outcomes_takes_worst(self):
        level = get_adverse_event_level_from_outcomes(["Non-serious Medical Event Not Requiring Intervention", "Death"])
        assert level == FDAIDAAdverseEventEnum.life_threatening_adverse_event
