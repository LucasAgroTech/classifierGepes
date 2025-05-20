# Automatic Project Classification Script

This script automates the classification of projects using the OpenAI API integration. It can process up to 100 projects in a single run, ensuring data consistency and proper database storage.

## Features

- Automatically classify projects using OpenAI's API
- Process up to 100 projects in a single run (configurable)
- Filter projects that haven't been classified yet
- Option to run in "dry run" mode without saving to the database
- Detailed logging and error handling
- Save classification results to a JSON file for review

## Prerequisites

- Python 3.6+
- OpenAI API key set in the `.env` file
- Database configured and accessible

## Installation

No additional installation is required beyond the main application dependencies. The script uses the existing OpenAI integration from the application.

## Usage

```bash
python auto_classify_projects.py [options]
```

### Options

- `--limit NUMBER`: Maximum number of projects to classify (default: 100)
- `--filter TYPE`: Filter projects to classify:
  - `unclassified`: Only process projects without existing AI suggestions (default)
  - `all`: Process all projects, even those with existing suggestions
- `--dry-run`: Run without saving results to the database
- `--output FILENAME`: Specify output file for results (default: auto_classify_results_TIMESTAMP.json)

### Examples

Classify up to 100 unclassified projects:
```bash
python auto_classify_projects.py
```

Classify only 10 projects:
```bash
python auto_classify_projects.py --limit 10
```

Reclassify all projects, including those already classified:
```bash
python auto_classify_projects.py --filter all
```

Test the classification without saving to the database:
```bash
python auto_classify_projects.py --dry-run
```

Save results to a specific file:
```bash
python auto_classify_projects.py --output my_results.json
```

## Output

The script generates two types of output:

1. **Console output**: Summary of the classification process
2. **Log file**: Detailed logs in `auto_classify.log`
3. **Results file**: JSON file with detailed results of each classification

### Results File Format

```json
{
  "total": 10,
  "success": 8,
  "error": 1,
  "skipped": 1,
  "results": [
    {
      "project_id": 1,
      "status": "success",
      "suggestion": {
        "microarea": "Energia renovável",
        "segmento": "Energia solar fotovoltaica",
        "dominio": "Integração com edificações e infraestrutura urbana",
        "dominio_outro": "Integração com redes elétricas",
        "tecverde_se_aplica": true
      }
    },
    {
      "project_id": 2,
      "status": "error",
      "error": "Error message"
    },
    ...
  ]
}
```

## Error Handling

The script includes comprehensive error handling:

- API errors are caught and logged
- Database errors are handled gracefully
- Individual project failures don't stop the entire process
- All errors are logged to both the console and log file

## Notes

- The script uses the OpenAI API, which may incur costs depending on your usage
- Processing 100 projects may take significant time depending on API response times
- The script respects the existing database structure and ensures data consistency
