# Project Classification Scripts

This directory contains scripts for automating the classification of projects using the OpenAI API integration. These scripts allow you to classify projects individually or in batch, with options for saving results to the database or to JSON files.

## Available Scripts

1. **auto_classify_projects.py**: Main script for classifying projects from the database
2. **example_classify.py**: Simple example script for testing classification with a single project
3. **batch_classify.py**: Script for classifying multiple projects from a JSON file
4. **sample_projects.json**: Sample JSON file with example projects for testing

## Prerequisites

- Python 3.6+
- OpenAI API key set in the `.env` file
- Database configured and accessible (for auto_classify_projects.py)
- Required Python packages installed (see requirements.txt)

## Usage Instructions

### 1. Classifying Projects from the Database

The `auto_classify_projects.py` script retrieves projects from the database and classifies them using the OpenAI API. It can process up to 100 projects in a single run.

```bash
python auto_classify_projects.py [options]
```

Options:
- `--limit NUMBER`: Maximum number of projects to classify (default: 100)
- `--filter TYPE`: Filter projects to classify:
  - `unclassified`: Only process projects without existing AI suggestions (default)
  - `all`: Process all projects, even those with existing suggestions
- `--dry-run`: Run without saving results to the database
- `--output FILENAME`: Specify output file for results

Examples:
```bash
# Classify up to 100 unclassified projects
python auto_classify_projects.py

# Classify only 10 projects
python auto_classify_projects.py --limit 10

# Reclassify all projects, including those already classified
python auto_classify_projects.py --filter all

# Test the classification without saving to the database
python auto_classify_projects.py --dry-run
```

### 2. Testing with a Single Project

The `example_classify.py` script demonstrates how to use the OpenAI integration with a single sample project. This is useful for testing the classification functionality without accessing the database.

```bash
python example_classify.py
```

This script:
1. Creates an OpenAI client
2. Defines a sample project
3. Calls the `suggest_categories` method
4. Prints the classification results

### 3. Batch Processing from a JSON File

The `batch_classify.py` script processes multiple projects from a JSON file and saves the classification results to another JSON file. This is useful for classifying projects from external sources without using the database.

```bash
python batch_classify.py sample_projects.json [options]
```

Options:
- `--limit NUMBER`: Maximum number of projects to classify (default: 100)
- `--output FILENAME`: Specify output file for results

Examples:
```bash
# Classify all projects in the sample_projects.json file
python batch_classify.py sample_projects.json

# Classify only the first 3 projects
python batch_classify.py sample_projects.json --limit 3

# Save results to a specific file
python batch_classify.py sample_projects.json --output my_results.json
```

## Output Files

The scripts generate several output files:

1. **Log files**:
   - `auto_classify.log`: Log file for auto_classify_projects.py
   - `batch_classify.log`: Log file for batch_classify.py

2. **Results files**:
   - `auto_classify_results_TIMESTAMP.json`: Results from auto_classify_projects.py
   - `batch_results_TIMESTAMP.json`: Results from batch_classify.py

## Database Integration

The `auto_classify_projects.py` script integrates with the database to:
1. Retrieve projects that need classification
2. Save classification results to the `ai_suggestions` table
3. Track which projects have already been classified

## Error Handling

All scripts include comprehensive error handling:
- API errors are caught and logged
- Database errors are handled gracefully
- Individual project failures don't stop the entire process
- All errors are logged to both the console and log file

## Notes

- The scripts use the OpenAI API, which may incur costs depending on your usage
- Processing 100 projects may take significant time depending on API response times
- The scripts respect the existing database structure and ensure data consistency
- For production use, consider running these scripts as scheduled tasks or in a containerized environment

## Example Workflow

1. Test the classification with a single project:
   ```bash
   python example_classify.py
   ```

2. Test batch classification with sample projects:
   ```bash
   python batch_classify.py sample_projects.json --limit 2
   ```

3. Run the full classification on the database:
   ```bash
   python auto_classify_projects.py --limit 100
   ```

4. Review the results in the generated JSON files and logs
