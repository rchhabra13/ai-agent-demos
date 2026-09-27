# Clinical Insights Assistant - Test Suite

This directory contains comprehensive pytest test files for the Clinical Insights Assistant project.

## Test Files Created

### 1. test_data_loader.py (9.1 KB)
Tests for data loading and validation functionality.

**Test Classes:**
- `TestLoadData` - Tests for load_data function (3 tests)
  - Returns DataFrame
  - Has required columns
  - Correct data types

- `TestValidateData` - Tests for validate_data function (4 tests)
  - Accepts valid data
  - Detects missing columns
  - Detects null values
  - Range checks

- `TestGenerateSampleData` - Tests for generate_sample_data function (4 tests)
  - Returns DataFrame
  - Has correct columns
  - Correct size
  - No nulls

- `TestGetPatientSummary` - Tests for get_patient_summary function (6 tests)
  - Returns dict
  - Filters by patient ID
  - Calculates statistics
  - Includes adverse events
  - Single patient handling

**Total: 17 tests**

### 2. test_issue_detection.py (12 KB)
Tests for anomaly and issue detection functions.

**Test Classes:**
- `TestDetectAdverseEvents` - Tests for detect_adverse_events function (5 tests)
  - Identifies flagged events
  - Returns DataFrame
  - Empty when no events
  - Extracts doctor notes
  - Correlates with outcomes

- `TestDetectDosageAnomalies` - Tests for detect_dosage_anomalies function (5 tests)
  - Identifies extreme values
  - Returns DataFrame
  - Normal values handling
  - By trial day detection
  - Zero dosage detection

- `TestDetectComplianceDrop` - Tests for detect_compliance_drop function (6 tests)
  - Identifies drops
  - Returns DataFrame
  - Threshold detection
  - Per-patient calculation
  - Stable compliance

- `TestRunAllDetections` - Tests for run_all_detections function (7 tests)
  - Returns dict
  - Includes adverse events
  - Includes dosage anomalies
  - Includes compliance drops
  - With empty data
  - Multiple issues

**Total: 23 tests**

### 3. test_cohort_analysis.py (13 KB)
Tests for statistical cohort comparison functions.

**Test Classes:**
- `TestGetCohortStats` - Tests for get_cohort_stats function (6 tests)
  - Returns dict
  - Calculates mean
  - Calculates std
  - Counts samples
  - Multiple cohorts
  - Missing values handling

- `TestCompareCohortsTtest` - Tests for compare_cohorts_ttest function (6 tests)
  - Returns tuple
  - Significant difference
  - No significant difference
  - Equal means
  - Different sizes
  - With DataFrame data

- `TestCompareCohortsChi2` - Tests for compare_cohorts_chisquared function (6 tests)
  - Returns tuple
  - With adverse events
  - Significant difference
  - No difference
  - From DataFrame
  - Multiple categories

- `TestAnalyzeOutcomeTrends` - Tests for analyze_outcome_trends function (8 tests)
  - Returns dict
  - Calculates improvement
  - Detects decline
  - Stable outcomes
  - Multiple cohorts
  - By dosage
  - With variance

**Total: 26 tests**

### 4. test_scenario_simulation.py (12 KB)
Tests for scenario simulation and sensitivity analysis functions.

**Test Classes:**
- `TestSimulateDosageChange` - Tests for simulate_dosage_change function (6 tests)
  - Increases dosage
  - Returns DataFrame
  - Preserves other columns
  - Percentage increase
  - By patient change
  - With escalation

- `TestSimulateComplianceIntervention` - Tests for simulate_compliance_intervention function (6 tests)
  - Increases compliance
  - Returns DataFrame
  - Caps at 100%
  - By patient intervention
  - Phased improvement
  - Minimal change

- `TestRunSensitivityAnalysis` - Tests for run_sensitivity_analysis function (8 tests)
  - Returns dict
  - Includes base case
  - Dosage variation
  - Compliance variation
  - Combined factors
  - Range of values
  - Outcome bounds
  - Multiple patients

**Total: 20 tests**

### 5. test_agent.py (12 KB)
Tests for agent core and memory functionality.

**Test Classes:**
- `TestMemory` - Tests for Memory class (6 tests)
  - Initialization
  - Stores conversation
  - Stores context
  - Retrieves messages
  - Tracks analysis results
  - Context persistence

- `TestAgentInit` - Tests for Agent initialization (7 tests)
  - Initialization
  - Has memory
  - Loads data
  - Empty memory
  - Has ask method
  - Configuration
  - Multiple instances

- `TestAgentAsk` - Tests for Agent ask method (10 tests)
  - Returns string
  - Simple questions
  - Patient-specific queries
  - Cohort queries
  - Analysis queries
  - Updates memory
  - Scenario requests
  - Multiple questions
  - Complex queries
  - Actionable insights
  - Data requests
  - Context preservation

- `TestAgentIntegration` - Integration tests (4 tests)
  - Agent-memory integration
  - Conversation flow
  - Data analysis workflow
  - Sample dataset

**Total: 27 tests**

## Usage

All test files use pytest and create DataFrames inline rather than loading from file.

### Running All Tests
```bash
pytest tests/
```

### Running Specific Test File
```bash
pytest tests/test_data_loader.py
```

### Running Specific Test Class
```bash
pytest tests/test_data_loader.py::TestLoadData
```

### Running Specific Test
```bash
pytest tests/test_data_loader.py::TestLoadData::test_load_data_returns_dataframe
```

### Verbose Output
```bash
pytest tests/ -v
```

### With Coverage
```bash
pytest tests/ --cov=src
```

## Test Data

All tests use inline DataFrame creation with the following columns:
- patient_id
- trial_day
- dosage_mg
- compliance_pct
- adverse_event_flag
- doctor_notes
- outcome_score
- cohort
- visit_date

No external data files are required for tests.

## Summary Statistics

- **Total Test Files:** 5
- **Total Test Classes:** 19
- **Total Test Methods:** 113
- **All tests use inline DataFrames** (no file I/O)
- **All tests use pytest framework**
- **All tests cover primary functionality** of their respective modules

## Test Coverage Areas

1. **Data Loading & Validation** - File I/O, data structure validation, type checking
2. **Issue Detection** - Anomaly detection, event flagging, correlation analysis
3. **Statistical Analysis** - Descriptive statistics, hypothesis testing, trend analysis
4. **Scenario Simulation** - Parameter variation, sensitivity analysis, intervention modeling
5. **Agent Functionality** - Initialization, memory management, conversation handling
