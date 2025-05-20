"""
Batch classification script for processing multiple projects from a JSON file.
This script demonstrates how to classify projects from an external source without using the database.
"""

import os
import json
import argparse
import logging
from datetime import datetime
from dotenv import load_dotenv
from app.ai_integration import OpenAIClient

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("batch_classify.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def load_projects_from_file(filename):
    """
    Load projects from a JSON file.
    
    Args:
        filename: Path to the JSON file
        
    Returns:
        List of project dictionaries
    """
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Check if the data is a list or a dictionary with a projects key
        if isinstance(data, list):
            projects = data
        elif isinstance(data, dict) and 'projects' in data:
            projects = data['projects']
        else:
            logger.error(f"Invalid JSON format in {filename}. Expected a list or a dictionary with a 'projects' key.")
            return []
        
        logger.info(f"Loaded {len(projects)} projects from {filename}")
        return projects
    except Exception as e:
        logger.error(f"Error loading projects from {filename}: {str(e)}")
        return []

def save_results_to_file(results, filename=None):
    """
    Save classification results to a JSON file.
    
    Args:
        results: Dictionary with classification results
        filename: Name of file to save results to (default: batch_results_TIMESTAMP.json)
        
    Returns:
        Path to the saved file
    """
    if not filename:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"batch_results_{timestamp}.json"
    
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        logger.info(f"Results saved to {filename}")
        return filename
    except Exception as e:
        logger.error(f"Error saving results to file: {str(e)}")
        return None

def classify_projects(api_key, projects, limit=100):
    """
    Classify projects using the OpenAI API.
    
    Args:
        api_key: OpenAI API key
        projects: List of project dictionaries
        limit: Maximum number of projects to classify
        
    Returns:
        Dictionary with classification results
    """
    # Create OpenAI client
    client = OpenAIClient(api_key)
    
    # Limit the number of projects to process
    projects_to_process = projects[:limit]
    
    # Statistics
    results = {
        "total": len(projects_to_process),
        "success": 0,
        "error": 0,
        "classifications": []
    }
    
    # Process each project
    for i, project in enumerate(projects_to_process):
        try:
            logger.info(f"Processing project {i+1}/{len(projects_to_process)}: ID={project.get('id', i+1)}, Title='{project.get('titulo', 'Unknown')}'")
            
            # Ensure project has required fields
            if not all(key in project for key in ['titulo', 'objetivo']):
                logger.warning(f"Project {i+1} is missing required fields (titulo, objetivo)")
                # Add minimal information if missing
                if 'id' not in project:
                    project['id'] = i + 1
                if 'titulo' not in project:
                    project['titulo'] = f"Project {i+1}"
                if 'objetivo' not in project:
                    project['objetivo'] = ""
                if 'descricao_publica' not in project:
                    project['descricao_publica'] = ""
                if 'tags' not in project:
                    project['tags'] = ""
            
            # Classify project
            suggestion = client.suggest_categories(project)
            
            # Check for errors
            if 'error' in suggestion:
                logger.error(f"Error classifying project {project.get('id', i+1)}: {suggestion['error']}")
                results["error"] += 1
                results["classifications"].append({
                    "project_id": project.get('id', i+1),
                    "title": project.get('titulo', 'Unknown'),
                    "status": "error",
                    "error": suggestion['error']
                })
                continue
            
            # Update statistics
            results["success"] += 1
            results["classifications"].append({
                "project_id": project.get('id', i+1),
                "title": project.get('titulo', 'Unknown'),
                "status": "success",
                "classification": {
                    "microarea": suggestion.get('_aia_n1_macroarea', ''),
                    "segmento": suggestion.get('_aia_n2_segmento', ''),
                    "dominio": suggestion.get('_aia_n3_dominio_afeito', ''),
                    "dominio_outro": suggestion.get('_aia_n3_dominio_outro', ''),
                    "confianca": suggestion.get('confianca', ''),
                    "justificativa": suggestion.get('justificativa', ''),
                    "tecverde_se_aplica": suggestion.get('tecverde_se_aplica', False),
                    "tecverde_classe": suggestion.get('tecverde_classe', ''),
                    "tecverde_subclasse": suggestion.get('tecverde_subclasse', ''),
                    "tecverde_confianca": suggestion.get('tecverde_confianca', ''),
                    "tecverde_justificativa": suggestion.get('tecverde_justificativa', '')
                }
            })
            
            # Log progress
            logger.info(f"Completed {i+1}/{len(projects_to_process)} projects")
            
        except Exception as e:
            logger.error(f"Unexpected error processing project {project.get('id', i+1)}: {str(e)}")
            results["error"] += 1
            results["classifications"].append({
                "project_id": project.get('id', i+1),
                "title": project.get('titulo', 'Unknown'),
                "status": "error",
                "error": str(e)
            })
    
    # Log final statistics
    logger.info(f"Classification complete. Total: {results['total']}, Success: {results['success']}, Error: {results['error']}")
    
    return results

def main():
    """Main function to run the script."""
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Batch classify projects from a JSON file using OpenAI API')
    parser.add_argument('input_file', help='JSON file containing projects to classify')
    parser.add_argument('--limit', type=int, default=100, help='Maximum number of projects to classify (default: 100)')
    parser.add_argument('--output', type=str, help='Output file for results (default: batch_results_TIMESTAMP.json)')
    args = parser.parse_args()
    
    # Load environment variables
    load_dotenv()
    api_key = os.getenv('OPENAI_API_KEY')
    
    if not api_key:
        logger.error("OpenAI API key not found. Set the OPENAI_API_KEY environment variable.")
        return
    
    # Load projects from file
    projects = load_projects_from_file(args.input_file)
    
    if not projects:
        logger.error(f"No projects found in {args.input_file}")
        return
    
    # Run classification
    logger.info(f"Starting batch classification with limit={args.limit}")
    results = classify_projects(api_key, projects, args.limit)
    
    # Save results to file
    output_file = save_results_to_file(results, args.output)
    
    # Print summary
    print("\nBatch Classification Summary:")
    print(f"Total projects processed: {results['total']}")
    print(f"Successfully classified: {results['success']}")
    print(f"Errors: {results['error']}")
    if output_file:
        print(f"Results saved to: {output_file}")

if __name__ == "__main__":
    main()
