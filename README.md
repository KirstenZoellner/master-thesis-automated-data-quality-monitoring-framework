# Automated Data Quality Monitoring Framework (ELT)

## Overview

This repository contains the prototype and artifact developed as part of a Master's Thesis focusing on automated data quality monitoring in modern Data Engineering pipelines.

## Methodological Foundation

The artifact was developed according to the Design Science Research process model by Peffers et al. (2007). Within this process, the repository represents the designed and implemented artifact for automated data quality monitoring in an ELT pipeline.

The implementation follows the design principle of Quality-as-Code, meaning that data quality requirements are formalized as executable validation rules using dbt and Great Expectations.

The solution combines the following technologies:

* **Google BigQuery** as cloud-native data warehouse
* **dbt Core** for data transformation and technical integrity testing
* **Great Expectations (GX)** for automated data quality validation
* **Looker Studio** for monitoring and visualization
* **Python** for orchestration and execution of quality gates

---

## Research Context

This repository was developed as part of a Master's Thesis in Business Informatics.

### Research Objective

Design and evaluation of a DataOps-oriented framework for automated data quality monitoring using open-source technologies and cloud-native data platforms.

---

## Architecture

![Architecture Diagram](docs/architecture.png)

---

## Technology Stack

| Component          | Purpose                                 |
| ------------------ | --------------------------------------- |
| Google BigQuery    | Central Data Warehouse                  |
| dbt Core           | Data Transformation & Technical Testing |
| Great Expectations | Data Quality Validation                 |
| Looker Studio      | Monitoring & Reporting                  |
| Python             | Orchestration & Automation              |

---

## Quality Gate Architecture

The framework validates data quality at multiple stages of the pipeline using dedicated Quality Gates.

### QG1 – Raw Data Validation

Validation of incoming weather data before further processing.

Implemented as the first validation layer using Great Expectations.

Checks include:

* Mandatory field validation (`station_id`, `date`, `avg_temp_c`)
* Temperature range validation
* Consistency validation (`max_temp_c >= min_temp_c`)

---

### QG2 – Reference Data Validation

Validation of city and reference data used within the pipeline.

Implemented with Great Expectations.

Checks include:

* Date completeness validation
* Timeliness validation based on the maximum available observation date
* Plausibility checks for temperature and precipitation values

---

### QG3 – Serving Layer Validation

Validation of transformed and prepared datasets before consumption.

Implemented with Great Expectations.

Checks include:

* Completeness checks
* Timeliness validation
* Value range validation
* Business rule validation

---

## dbt Technical Tests

In addition to the Quality Gates, dbt tests are executed on the transformed model.

Implemented tests include:

* `not_null`
* `unique`
* `accepted_values`

These tests provide an additional technical validation layer for structural data quality issues.

---

### Quality Gate Dimensions

| Quality Gate | Check | Data Quality Dimension |
|-------------|-------|-------------------------|
| QG1 | station_id not null | Completeness |
| QG1 | date not null | Completeness |
| QG1 | max_temp_c between -90 and 60 | Accuracy |
| QG1 | max_temp_c >= min_temp_c | Consistency |
| QG2 | ISO-2 format validation | Validity |
| QG2 | ISO-2 accepted values | Accuracy / Validity |
| QG2 | country_code accepted values | Accuracy / Validity |
| QG3 | date not null | Completeness |
| QG3 | freshness / timeliness check | Timeliness |
| QG3 | avg_temp_c range | Accuracy |
| QG3 | precipitation_mm range | Accuracy |
| dbt | unique station_id + date | Uniqueness |
| dbt | not_null city_name | Completeness |
| dbt | accepted_values season | Validity |

---

## Evaluation Scenarios

To evaluate the effectiveness of the framework, three different datasets are processed.

| Scenario    | Description                                                               |
| ----------- | ------------------------------------------------------------------------- |
| `clean`     | Dataset without injected quality issues                                   |
| `technical` | Dataset containing technical issues such as duplicates and missing values |
| `faulty`    | Dataset containing semantic and business-rule violations                  |

### Expected Behaviour

#### clean

* No intentionally injected quality issues are expected
* dbt tests and Quality Gates are used as baseline validation
* Dashboard provides a reference view for comparison with faulty scenarios

#### technical

* Technical issues are detected by dbt tests
* Structural quality problems become visible in monitoring

#### faulty

* Business-rule violations are detected by Great Expectations
* Data quality alerts are generated
* Dashboard visualizes reduced data quality scores

---

## Execution Guide

### 1. Execute dbt Transformation

```bash
dbt run --vars "{weather_table: daily_weather_clean}"
```

### 2. Execute dbt Tests

```bash
dbt test --vars "{weather_table: daily_weather_clean}"
```

### 3. Execute Great Expectations Quality Gates

```bash
python validate_qg1_raw.py clean
python validate_qg2_cities.py clean
python validate_qg3_serving.py clean
```

### 4. Load dbt Test Results

```bash
python load_dbt_results.py clean
```

---

## Monitoring & Reporting

All validation results are written to BigQuery and consolidated in the `dq_results` table.

The monitoring dashboard is implemented in Looker Studio and provides:

* Number of detected errors per scenario
* Failed checks per Quality Gate
* Validation results per scenario
* Distribution of checks across validation tools

---

## Repository Structure

```text
weather_pipeline/
├── models/
│   ├── schema.yml
│   └── stg_daily_weather.sql
├── dbt_project.yml

gx/
├── validate_qg1_raw.py
├── validate_qg2_cities.py
├── validate_qg3_serving.py
├── load_dbt_results.py

docs/
├── architecture.png

looker/
├── README.md
├── dashboard_anzahl_datenqualitaetspruefungen_je_werkzeug_und_szenario.png
├── dashboard_anzahl_erkannter_fehler_pro_szenario.png
├── dashboard_anzahl_fehlgeschlagener_pruefungen_pro_quality_gate.png
└── dashboard_ergebnis_datenqualitaetspruefungen_je_szenario.png
```

---

## Author

Master Thesis Project


