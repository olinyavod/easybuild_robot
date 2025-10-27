"""
Project Matcher for semantic matching of user text with project tags.
"""

import logging
from typing import List, Optional, Tuple
from sentence_transformers import SentenceTransformer, util
import torch

from .models import Project

logger = logging.getLogger(__name__)


class ProjectMatcher:
    """
    Matches user text with project tags using semantic similarity.
    
    Uses the same ruBERT-tiny model as CommandRegistry for consistency.
    """
    
    def __init__(self, model_name: str = "cointegrated/rubert-tiny", threshold: float = 0.5):
        """
        Initialize project matcher.
        
        Args:
            model_name: Name of the sentence-transformers model to use
            threshold: Minimum similarity score to consider a match
        """
        self.model_name = model_name
        self.threshold = threshold
        
        logger.info(f"Loading model {model_name} for project matching...")
        self.model = SentenceTransformer(model_name)
        logger.info("Project matcher initialized")
    
    def find_projects_by_semantic_match(
        self, 
        text: str, 
        projects: List[Project],
        group_id: Optional[int] = None
    ) -> List[Tuple[Project, float]]:
        """
        Find projects that match the given text semantically based on their tags.
        
        Args:
            text: User text to match
            projects: List of projects to search in
            group_id: Optional group ID to filter projects
            
        Returns:
            List of tuples (Project, similarity_score) sorted by score (highest first)
        """
        if not text or not text.strip():
            return []
        
        if not projects:
            return []
        
        # Filter projects by group if specified
        if group_id is not None:
            projects = [
                p for p in projects 
                if not p.allowed_group_ids or group_id in p.allowed_group_ids
            ]
        
        # Filter projects that have tags
        projects_with_tags = [p for p in projects if p.tags]
        
        if not projects_with_tags:
            logger.debug("No projects with tags found")
            return []
        
        # Clean and normalize text
        text_cleaned = text.strip().lower()
        
        # Get user text embedding
        user_embedding = self.model.encode(text_cleaned, convert_to_tensor=True)
        
        matches = []
        
        # Check each project
        for project in projects_with_tags:
            # Get embeddings for all project tags
            tag_embeddings = self.model.encode(project.tags, convert_to_tensor=True)
            
            # Calculate cosine similarity with all tags
            similarities = util.cos_sim(user_embedding, tag_embeddings)[0]
            
            # Take maximum similarity across all tags
            max_similarity = torch.max(similarities).item()
            
            if max_similarity >= self.threshold:
                matches.append((project, max_similarity))
                logger.info(
                    f"Project '{project.name}' matched with score {max_similarity:.3f} "
                    f"(tags: {', '.join(project.tags)})"
                )
        
        # Sort by similarity score (highest first)
        matches.sort(key=lambda x: x[1], reverse=True)
        
        return matches
    
    def find_best_project(
        self, 
        text: str, 
        projects: List[Project],
        group_id: Optional[int] = None
    ) -> Optional[Tuple[Project, float]]:
        """
        Find the best matching project for the given text.
        
        Args:
            text: User text to match
            projects: List of projects to search in
            group_id: Optional group ID to filter projects
            
        Returns:
            Tuple (Project, similarity_score) or None if no match found
        """
        matches = self.find_projects_by_semantic_match(text, projects, group_id)
        
        if matches:
            return matches[0]
        
        return None
    
    def find_project_by_name_or_tags(
        self,
        text: str,
        projects: List[Project],
        group_id: Optional[int] = None
    ) -> Optional[Project]:
        """
        Find project by exact name match or semantic tag match.
        
        First tries to find by exact name, then by semantic tags.
        
        Args:
            text: User text (project name or description)
            projects: List of projects to search in
            group_id: Optional group ID to filter projects
            
        Returns:
            Matched Project or None
        """
        if not text or not text.strip():
            return None
        
        text_cleaned = text.strip()
        
        # Filter by group if specified
        if group_id is not None:
            projects = [
                p for p in projects 
                if not p.allowed_group_ids or group_id in p.allowed_group_ids
            ]
        
        # Try exact name match first (case-insensitive)
        for project in projects:
            if project.name.lower() == text_cleaned.lower():
                logger.info(f"Found project by exact name match: '{project.name}'")
                return project
        
        # Try partial name match
        for project in projects:
            if text_cleaned.lower() in project.name.lower():
                logger.info(f"Found project by partial name match: '{project.name}'")
                return project
        
        # Try semantic tag match
        best_match = self.find_best_project(text_cleaned, projects, group_id)
        if best_match:
            project, score = best_match
            logger.info(f"Found project by semantic tag match: '{project.name}' (score: {score:.3f})")
            return project
        
        return None

