# CURE ID

[CURE ID](https://cure.ncats.io/) is a free platform developed by FDA and NIH to share novel uses of existing drugs (drug repurposing/off-label use) and explore what others have tried. The goal is to find potential treatments for challenging diseases that lack good treatment options. Information is collected from case reports and series published in the medical literature.

- [CURE ID bulk data downloads](https://opendata.ncats.nih.gov/public/cureid/)

## Source Data

This ingest uses the `cureid_data.tsv` file from the [NCATS Open Data Portal](https://opendata.ncats.nih.gov/public/cureid/). The file contains manually and LLM curated associations between chemicals, diseases, phenotypic features, genes, and variants from case reports documented in CURE ID.

This initial ingest focuses on case report entities and relationships for RASopathies as documented in CURE ID.

### Source File Fields

- subject_type, subject_final_curie, subject_final_label
- object_type, object_final_curie, object_final_label
- association_category, biolink_predicate
- outcome, pmid, link, report_id

## Data Model

This ingest uses a **case-centered star model** where `biolink:Case` nodes represent individual patient case reports from CURE ID. Each case links to its diseases, phenotypes, and genes, preserving the case report context that would be lost with direct pairwise edges.

### Row-type-to-output mapping

| Source Row Type | Output Entities |
|---|---|
| Disease → has_phenotype → PhenotypicFeature | Case + Disease + PhenotypicFeature + CaseToDiseaseAssociation + CaseToPhenotypicFeatureAssociation |
| Gene → gene_associated_with_condition → Disease | Case + Gene + Disease + CaseToDiseaseAssociation + CaseToGeneAssociation |
| Drug → applied_to_treat → Disease | ChemicalEntity + Disease + ChemicalEntityToDiseaseOrPhenotypicFeatureAssociation |
| Drug → applied_to_treat → PhenotypicFeature | ChemicalEntity + PhenotypicFeature + ChemicalEntityToDiseaseOrPhenotypicFeatureAssociation |
| Drug → has_adverse_event → AdverseEvent | ChemicalEntity + PhenotypicFeature + ChemicalOrDrugOrTreatmentAdverseEventAssociation |
| Gene → has_sequence_variant → SequenceVariant | Skipped (variant CURIEs missing) |
| SequenceVariant → genetically_associated_with → Disease | Skipped (variant CURIEs missing) |

### Case Node

`biolink:Case` — an individual patient case report from CURE ID.

| Property | Value | Notes |
| -------- | ----- | ----- |
| id | `CUREID:{report_id}` | From `report_id` field |
| iri | URL | CURE ID case report URL |
| in_taxon | `["NCBITaxon:9606"]` | Human |

## Biolink Captured

### Case to Disease

**[biolink:CaseToDiseaseAssociation](https://biolink.github.io/biolink-model/CaseToDiseaseAssociation/)**

| Property | Value | Notes |
| -------- | ----- | ----- |
| id | UUID5 (deterministic) | Deduplicates across rows for the same case+disease |
| subject | CURIE | `biolink:Case` (CUREID) |
| predicate | `biolink:has_disease` | |
| object | CURIE | `biolink:Disease` (MONDO, UMLS) |
| publications | CURIE list | PMIDs from case reports |
| primary_knowledge_source | `infores:cureid` | |
| knowledge_level | `observation` | Case-level observation |
| agent_type | `manual_agent` | |

### Case to Phenotypic Feature

**[biolink:CaseToPhenotypicFeatureAssociation](https://biolink.github.io/biolink-model/CaseToPhenotypicFeatureAssociation/)**

| Property | Value | Notes |
| -------- | ----- | ----- |
| id | UUID5 (deterministic) | Deduplicates across rows for the same case+phenotype |
| subject | CURIE | `biolink:Case` (CUREID) |
| predicate | `biolink:has_phenotype` | |
| object | CURIE | `biolink:PhenotypicFeature` (HP, NCIT, UMLS) |
| disease_context_qualifier | CURIE | Disease associated with the phenotype in the case |
| publications | CURIE list | PMIDs from case reports |
| primary_knowledge_source | `infores:cureid` | |
| knowledge_level | `observation` | Case-level observation |
| agent_type | `manual_agent` | |

### Case to Gene

**[biolink:CaseToGeneAssociation](https://biolink.github.io/biolink-model/CaseToGeneAssociation/)**

| Property | Value | Notes |
| -------- | ----- | ----- |
| id | UUID5 (deterministic) | Deduplicates across rows for the same case+gene |
| subject | CURIE | `biolink:Case` (CUREID) |
| predicate | `biolink:has_gene` | |
| object | CURIE | `biolink:Gene` (NCBIGene) |
| publications | CURIE list | PMIDs from case reports |
| primary_knowledge_source | `infores:cureid` | |
| knowledge_level | `observation` | Case-level observation |
| agent_type | `manual_agent` | |

### Chemical to Disease/Phenotype (treatment)

**[biolink:ChemicalEntityToDiseaseOrPhenotypicFeatureAssociation](https://biolink.github.io/biolink-model/ChemicalEntityToDiseaseOrPhenotypicFeatureAssociation/)**

| Property | Value | Notes |
| -------- | ----- | ----- |
| id | UUID4 (random) | |
| subject | CURIE | `biolink:ChemicalEntity` (CHEBI, UNII) |
| predicate | `biolink:applied_to_treat` | |
| object | CURIE | `biolink:Disease` (MONDO, UMLS) or `biolink:PhenotypicFeature` (HP, NCIT, UMLS) |
| publications | CURIE list | PMIDs from case reports |
| primary_knowledge_source | `infores:cureid` | |
| knowledge_level | `knowledge_assertion` | |
| agent_type | `manual_agent` | |

### Chemical Adverse Events

**[biolink:ChemicalOrDrugOrTreatmentAdverseEventAssociation](https://biolink.github.io/biolink-model/ChemicalOrDrugOrTreatmentAdverseEventAssociation/)**

| Property | Value | Notes |
| -------- | ----- | ----- |
| id | UUID4 (random) | |
| subject | CURIE | `biolink:ChemicalEntity` (CHEBI, UNII) |
| predicate | `biolink:has_adverse_event` | |
| object | CURIE | `biolink:PhenotypicFeature` (HP, NCIT, UMLS) |
| FDA_adverse_event_level | FDAIDAAdverseEventEnum | Mapped from CURE ID outcome severity |
| publications | CURIE list | PMIDs from case reports |
| primary_knowledge_source | `infores:cureid` | |
| knowledge_level | `observation` | |
| agent_type | `manual_agent` | |

### Dropped Edge Types

- **Gene → Disease** (`GeneToDiseaseAssociation`): Dropped because these are case-level observations, not curated gene-disease assertions. The gene context is preserved via Case → Gene edges.
- **Gene → Variant** and **Variant → Disease**: Dropped because all variant CURIEs are missing in the source data.

### Adverse Event Level Mapping

CURE ID outcomes are mapped to FDA IDA adverse event levels:

| CURE ID Outcome | FDA IDA Level |
| --------------- | ------------- |
| Death, Life-threatening | `life_threatening_adverse_event` |
| Hospitalization, Disability, Congenital Anomaly, Other Serious Events, Treatment Discontinued, Required Intervention | `serious_adverse_event` |
| Non-serious (requiring or not requiring intervention), Unknown | `unexpected_adverse_event` |

When multiple outcomes are reported, the most severe level is used.

## Citation

Farid T, Ruzhnikov MRZ, Duggal M, Tumas KC, Strongin S, Sid E, Fuchs SR, Sacks L, Pichard DC, Pilgrim-Grayson C, Mathé EA, Stone HA. **CURE ID: A Platform to Collect Real-World Treatment Data for Drug Repurposing in Rare Genetic Disorders.** _Am J Med Genet C Semin Med Genet. 2025 Sep;199(3):189-193._ doi: 10.1002/ajmg.c.32153. [PMID:41496707](https://pubmed.ncbi.nlm.nih.gov/41496707/)

## License

BSD-3-Clause
