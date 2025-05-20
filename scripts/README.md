# Scripts Directory

This directory contains various scripts organized by functionality for the GEPES Classifier project.

## Directory Structure

- **classification/**: Scripts related to project classification using AI
  - Auto-classification scripts
  - Batch classification scripts
  - Example and test scripts
  - Classification results

- **category_management/**: Scripts for managing categories
  - Adding sample categories
  - Listing categories
  - Debugging category structure
  - Running the category manager

- **tecverde/**: Scripts related to TecVerde functionality
  - Adding TecVerde categories
  - Listing TecVerde categories
  - Setting up TecVerde categories
  - Testing TecVerde suggestions

- **database/**: Scripts for database operations
  - Altering database columns
  - Creating admin users

- **tests/**: Testing scripts
  - Category function tests
  - Route tests

## Usage

Most scripts can be run directly from the command line. For example:

```bash
# From the project root directory
python scripts/classification/auto_classify_projects.py

# Or navigate to the scripts directory first
cd scripts/classification
python auto_classify_projects.py
```

For more detailed information about specific script categories, please refer to the README files in each subdirectory:

- [Classification Scripts](classification/README_AUTO_CLASSIFY.md)
- [Category Management](category_management/README_CATEGORY_MANAGER.md)
- [TecVerde Scripts](tecverde/README_TECVERDE.md)
- [Database Operations](database/README_VALOR_COLUMN_FIX.md)
- [Testing Scripts](tests/README_TESTING.md)
