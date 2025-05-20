import os
import json
import logging
import argparse
from datetime import datetime
from dotenv import load_dotenv
from app import create_app, db
from app.models import Projeto, AISuggestion
from app.ai_integration import OpenAIClient

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("auto_classify.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def get_projects_to_classify(limit=100, filter_type=None):
    """
    Get projects from the database that need classification.
    
    Args:
        limit: Maximum number of projects to return
        filter_type: Type of filter to apply ('unclassified', 'all', or None)
        
    Returns:
        List of projects to classify
    """
    try:
        query = Projeto.query
        
        # Apply filter if specified
        if filter_type == 'unclassified':
            # Get projects that don't have AI suggestions
            subquery = db.session.query(AISuggestion.id_projeto)
            query = query.filter(~Projeto.id.in_(subquery))
        
        # Order by ID to ensure consistent results
        query = query.order_by(Projeto.id)
        
        # Apply limit
        projects = query.limit(limit).all()
        
        logger.info(f"Retrieved {len(projects)} projects to classify")
        return projects
    except Exception as e:
        logger.error(f"Error retrieving projects: {str(e)}")
        return []

def format_project_for_classification(project):
    """
    Format a project object into the dictionary format expected by the OpenAIClient.
    
    Args:
        project: Projeto object from the database
        
    Returns:
        Dictionary with project data formatted for classification
    """
    return {
        'id': project.id,
        'titulo': project.titulo,
        'titulo_publico': project.titulo_publico,
        'objetivo': project.objetivo,
        'descricao_publica': project.descricao_publica,
        'tags': project.tags
    }

def classify_projects(api_key, limit=100, filter_type=None, dry_run=False):
    """
    Classify projects using the OpenAI API.
    
    Args:
        api_key: OpenAI API key
        limit: Maximum number of projects to classify
        filter_type: Type of filter to apply ('unclassified', 'all', or None)
        dry_run: If True, don't save results to database
        
    Returns:
        Dictionary with statistics about the classification process
    """
    # Create OpenAI client
    client = OpenAIClient(api_key)
    
    # Get projects to classify
    projects = get_projects_to_classify(limit, filter_type)
    
    if not projects:
        logger.warning("No projects found to classify")
        return {
            "total": 0,
            "success": 0,
            "error": 0,
            "skipped": 0
        }
    
    # Statistics
    stats = {
        "total": len(projects),
        "success": 0,
        "error": 0,
        "skipped": 0,
        "results": []
    }
    
    # Process each project
    for i, project in enumerate(projects):
        try:
            logger.info(f"Processing project {i+1}/{len(projects)}: ID={project.id}, Title='{project.titulo}'")
            
            # Format project for classification
            project_data = format_project_for_classification(project)
            
            # Check if project already has a suggestion
            existing_suggestion = AISuggestion.query.filter_by(id_projeto=project.id).first()
            if existing_suggestion and filter_type != 'all':
                logger.info(f"Project {project.id} already has a suggestion, skipping")
                stats["skipped"] += 1
                continue
            
            # Classify project
            logger.info(f"Classifying project {project.id}")
            suggestion = client.suggest_categories(project_data)
            
            # Check for errors
            if 'error' in suggestion:
                logger.error(f"Error classifying project {project.id}: {suggestion['error']}")
                stats["error"] += 1
                stats["results"].append({
                    "project_id": project.id,
                    "status": "error",
                    "error": suggestion['error']
                })
                continue
            
            # Save suggestion to database if not dry run
            if not dry_run:
                success = client._save_suggestion_to_db(project.id, suggestion)
                if success:
                    logger.info(f"Successfully saved suggestion for project {project.id}")
                else:
                    logger.error(f"Failed to save suggestion for project {project.id}")
                    stats["error"] += 1
                    continue
            else:
                logger.info(f"Dry run - not saving suggestion for project {project.id}")
            
            # Update statistics
            stats["success"] += 1
            stats["results"].append({
                "project_id": project.id,
                "status": "success",
                "suggestion": {
                    "microarea": suggestion.get('_aia_n1_macroarea', ''),
                    "segmento": suggestion.get('_aia_n2_segmento', ''),
                    "dominio": suggestion.get('_aia_n3_dominio_afeito', ''),
                    "dominio_outro": suggestion.get('_aia_n3_dominio_outro', ''),
                    "tecverde_se_aplica": suggestion.get('tecverde_se_aplica', False)
                }
            })
            
            # Log progress
            logger.info(f"Completed {i+1}/{len(projects)} projects")
            
        except Exception as e:
            logger.error(f"Unexpected error processing project {project.id}: {str(e)}")
            stats["error"] += 1
            stats["results"].append({
                "project_id": project.id,
                "status": "error",
                "error": str(e)
            })
    
    # Log final statistics
    logger.info(f"Classification complete. Total: {stats['total']}, Success: {stats['success']}, Error: {stats['error']}, Skipped: {stats['skipped']}")
    
    return stats

def save_results_to_file(stats, filename=None):
    """
    Save classification results to a JSON file.
    
    Args:
        stats: Statistics dictionary from classify_projects
        filename: Name of file to save results to (default: auto_classify_results_TIMESTAMP.json)
        
    Returns:
        Path to the saved file
    """
    if not filename:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"auto_classify_results_{timestamp}.json"
    
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(stats, f, indent=2, ensure_ascii=False)
        logger.info(f"Results saved to {filename}")
        return filename
    except Exception as e:
        logger.error(f"Error saving results to file: {str(e)}")
        return None

def main():
    """Main function to run the script."""
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Automatically classify projects using OpenAI API')
    parser.add_argument('--limit', type=int, default=100, help='Maximum number of projects to classify (default: 100)')
    parser.add_argument('--filter', choices=['unclassified', 'all'], default='unclassified', 
                        help='Filter projects to classify (unclassified: only projects without suggestions, all: all projects)')
    parser.add_argument('--dry-run', action='store_true', help='Run without saving results to database')
    parser.add_argument('--output', type=str, help='Output file for results (default: auto_classify_results_TIMESTAMP.json)')
    args = parser.parse_args()
    
    # Load environment variables
    load_dotenv()
    api_key = os.getenv('OPENAI_API_KEY')
    
    if not api_key:
        logger.error("OpenAI API key not found. Set the OPENAI_API_KEY environment variable.")
        return
    
    # Create Flask app and context
    app = create_app()
    
    with app.app_context():
        # Run classification
        logger.info(f"Starting classification with limit={args.limit}, filter={args.filter}, dry_run={args.dry_run}")
        stats = classify_projects(api_key, args.limit, args.filter, args.dry_run)
        
        # Save results to file
        save_results_to_file(stats, args.output)
        
        # Print summary
        print("\nClassification Summary:")
        print(f"Total projects processed: {stats['total']}")
        print(f"Successfully classified: {stats['success']}")
        print(f"Errors: {stats['error']}")
        print(f"Skipped (already classified): {stats['skipped']}")

if __name__ == "__main__":
    main()
