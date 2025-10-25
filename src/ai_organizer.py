"""
AI Organizer Module for Media Library Organization

This module handles communication with Google Gemini AI to get organization
suggestions for media files and directories using the google-genai library.
"""

import os
import json
import re
from typing import Dict, List, Optional, Tuple, Union
from dataclasses import dataclass
from pathlib import Path

import google.genai as genai
from google.genai import types

from tree_generator import DirectoryNode, TreeGenerator


@dataclass
class OrganizationSuggestion:
    """Represents an AI suggestion for organizing media files."""
    source_path: str
    destination_path: str
    operation: str  # 'move', 'rename', 'create_directory'
    confidence: float
    reason: str


@dataclass
class OrganizationPlan:
    """Complete organization plan for a media collection."""
    show_name: str
    year: Optional[int]
    suggestions: List[OrganizationSuggestion]
    summary: str
    warnings: List[str]


class AIOrganizer:
    """Handles AI-powered media organization using Google Gemini."""

    def __init__(self, api_key: str, model_name: str = "gemini-1.5-flash"):
        """
        Initialize the AI organizer.

        Args:
            api_key: Google Gemini API key
            model_name: Name of the Gemini model to use
        """
        self.api_key = api_key
        self.model_name = model_name

        # Initialize the client
        self.client = genai.Client(api_key=api_key)

    def organize_tv_show(self, tree_text: str, show_folder_name: str) -> OrganizationPlan:
        """
        Get organization suggestions for a TV show directory.

        Args:
            tree_text: Text representation of the directory tree
            show_folder_name: Name of the show folder being organized

        Returns:
            OrganizationPlan with suggestions for organizing the show
        """
        prompt = self._create_tv_show_prompt(tree_text, show_folder_name)

        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=0.1,
                    top_p=0.8,
                    top_k=40,
                    max_output_tokens=8192,
                    safety_settings=[
                        types.SafetySetting(
                            category=types.HarmCategory.HARM_CATEGORY_HARASSMENT,
                            threshold=types.HarmBlockThreshold.BLOCK_NONE
                        ),
                        types.SafetySetting(
                            category=types.HarmCategory.HARM_CATEGORY_HATE_SPEECH,
                            threshold=types.HarmBlockThreshold.BLOCK_NONE
                        ),
                        types.SafetySetting(
                            category=types.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT,
                            threshold=types.HarmBlockThreshold.BLOCK_NONE
                        ),
                        types.SafetySetting(
                            category=types.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT,
                            threshold=types.HarmBlockThreshold.BLOCK_NONE
                        ),
                    ]
                )
            )
            return self._parse_tv_show_response(response.text, show_folder_name)
        except Exception as e:
            raise Exception(f"Failed to get AI response: {str(e)}")

    def organize_movie_collection(self, tree_text: str, movies_folder_name: str) -> OrganizationPlan:
        """
        Get organization suggestions for a movie collection.

        Args:
            tree_text: Text representation of the directory tree
            movies_folder_name: Name of the movies folder being organized

        Returns:
            OrganizationPlan with suggestions for organizing the movies
        """
        prompt = self._create_movie_prompt(tree_text, movies_folder_name)

        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=0.1,
                    top_p=0.8,
                    top_k=40,
                    max_output_tokens=8192,
                    safety_settings=[
                        types.SafetySetting(
                            category=types.HarmCategory.HARM_CATEGORY_HARASSMENT,
                            threshold=types.HarmBlockThreshold.BLOCK_NONE
                        ),
                        types.SafetySetting(
                            category=types.HarmCategory.HARM_CATEGORY_HATE_SPEECH,
                            threshold=types.HarmBlockThreshold.BLOCK_NONE
                        ),
                        types.SafetySetting(
                            category=types.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT,
                            threshold=types.HarmBlockThreshold.BLOCK_NONE
                        ),
                        types.SafetySetting(
                            category=types.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT,
                            threshold=types.HarmBlockThreshold.BLOCK_NONE
                        ),
                    ]
                )
            )
            return self._parse_movie_response(response.text, movies_folder_name)
        except Exception as e:
            raise Exception(f"Failed to get AI response: {str(e)}")

    def _create_tv_show_prompt(self, tree_text: str, show_folder_name: str) -> str:
        """Create a detailed prompt for TV show organization."""
        return f"""
You are an expert media library organizer. I need you to analyze the following TV show directory structure and provide organization suggestions.

**SHOW FOLDER:** {show_folder_name}

**CURRENT DIRECTORY STRUCTURE:**
```
{tree_text}
```

**DESIRED ORGANIZATION FORMAT:**
Show Name (Year)
├── Season 01
│   ├── Show.Name.S01E01.Episode.Title.Quality.mkv
│   ├── Show.Name.S01E02.Episode.Title.Quality.mkv
│   └── ...
├── Season 02
│   ├── Show.Name.S02E01.Episode.Title.Quality.mkv
│   └── ...
└── Season 03 (if applicable)

**ORGANIZATION RULES:**
1. Extract the correct show name and year from the files
2. Create proper season folders (Season 01, Season 02, etc.)
3. Move episode files to their respective season folders
4. Keep the highest quality version if multiple qualities exist for the same episode
5. Preserve subtitle files (.srt, .sub, etc.) alongside their video files
6. Remove unnecessary nested directories
7. PRESERVE ORIGINAL FILENAMES - Do NOT rename files, only move them to correct folders

**RESPONSE FORMAT:**
Please respond with a JSON object containing:
```json
{{
    "show_name": "Extracted Show Name",
    "year": 2021,
    "summary": "Brief description of what needs to be organized",
    "warnings": ["Any potential issues or conflicts"],
    "operations": [
        {{
            "operation": "create_directory",
            "destination_path": "Show Name (2021)/Season 01",
            "reason": "Create season directory"
        }},
        {{
            "operation": "move",
            "source_path": "current/path/to/file.mkv",
            "destination_path": "Show Name (2021)/Season 01/file.mkv",
            "confidence": 0.95,
            "reason": "Move episode to correct season folder"
        }}
    ]
}}
```

**IMPORTANT:**
- Only suggest operations that are clearly beneficial
- Be conservative with file moves if you're unsure
- ALWAYS preserve original filenames - never rename files
- Handle duplicate episodes by keeping the highest quality version
- Include confidence scores (0.0 to 1.0) for each operation

Analyze the structure and provide your organization suggestions:
"""

    def _create_movie_prompt(self, tree_text: str, movies_folder_name: str) -> str:
        """Create a detailed prompt for movie collection organization."""
        return f"""
You are an expert media library organizer. I need you to analyze the following movies directory structure and provide organization suggestions.

**MOVIES FOLDER:** {movies_folder_name}

**CURRENT DIRECTORY STRUCTURE:**
```
{tree_text}
```

**DESIRED ORGANIZATION FORMAT:**
Movies/
├── Movie Name (Year)
│   ├── Movie.Name.Year.Quality.mkv
│   ├── Movie.Name.Year.Quality.srt (if subtitles exist)
│   └── poster.jpg (if poster exists)
├── Another Movie (Year)
│   └── Another.Movie.Year.Quality.mkv
└── ...

**ORGANIZATION RULES:**
1. Extract correct movie name and release year
2. Create individual folders for each movie: "Movie Name (Year)"
3. Move movie files into their respective folders
4. Keep the highest quality version if multiple exist
5. Preserve subtitle and poster files with movies
6. Remove unnecessary nested directories
7. PRESERVE ORIGINAL FILENAMES - Do NOT rename files, only move them to correct folders

**RESPONSE FORMAT:**
Please respond with a JSON object containing:
```json
{{
    "collection_name": "Movies",
    "summary": "Brief description of what needs to be organized",
    "warnings": ["Any potential issues or conflicts"],
    "operations": [
        {{
            "operation": "create_directory",
            "destination_path": "Movie Name (2008)",
            "reason": "Create movie directory"
        }},
        {{
            "operation": "move",
            "source_path": "current/path/to/movie.mkv",
            "destination_path": "Movie Name (2008)/movie.mkv",
            "confidence": 0.95,
            "reason": "Move movie to organized folder"
        }}
    ]
}}
```

**IMPORTANT:**
- Extract movie titles and years accurately
- Handle collections/franchises appropriately
- Be conservative with moves if movie identification is unclear
- Include confidence scores (0.0 to 1.0) for each operation
- ALWAYS preserve original filenames - never rename files

Analyze the structure and provide your organization suggestions:
"""

    def _parse_tv_show_response(self, response_text: str, show_folder_name: str) -> OrganizationPlan:
        """Parse AI response for TV show organization."""
        try:
            # Log full response for debugging
            print(f"Full AI response text: {response_text}")

            # Extract JSON from response
            json_match = re.search(r'```json\s*(\{.*?\})\s*```', response_text, re.DOTALL)
            if not json_match:
                # Try to find JSON without code blocks
                json_match = re.search(r'(\{.*\})', response_text, re.DOTALL)

            if not json_match:
                print(f"No JSON found in response: {response_text[:1000]}")
                raise ValueError("No valid JSON found in AI response")

            json_text = json_match.group(1)

            # Debug output for malformed JSON
            print(f"Extracted JSON text length: {len(json_text)}")
            print(f"Raw JSON response (first 500 chars): {json_text[:500]}")
            print(f"Raw JSON response (last 500 chars): {json_text[-500:]}")



            try:
                data = json.loads(json_text)
            except json.JSONDecodeError as json_err:
                print(f"JSON decode error: {json_err}")
                print(f"Problematic JSON around error: {json_text[max(0, json_err.pos-100):json_err.pos+100]}")
                raise

            # Parse operations into suggestions
            suggestions = []
            for op in data.get('operations', []):
                if op['operation'] == 'create_directory':
                    suggestions.append(OrganizationSuggestion(
                        source_path="",
                        destination_path=op['destination_path'],
                        operation='create_directory',
                        confidence=1.0,
                        reason=op['reason']
                    ))
                elif op['operation'] == 'move':
                    suggestions.append(OrganizationSuggestion(
                        source_path=op['source_path'],
                        destination_path=op['destination_path'],
                        operation='move',
                        confidence=op.get('confidence', 0.8),
                        reason=op['reason']
                    ))

            return OrganizationPlan(
                show_name=data.get('show_name', show_folder_name),
                year=data.get('year'),
                suggestions=suggestions,
                summary=data.get('summary', ''),
                warnings=data.get('warnings', [])
            )

        except (json.JSONDecodeError, KeyError) as e:
            print(f"JSON parsing failed: {str(e)}")
            print(f"Full response that failed: {response_text}")
            raise ValueError(f"Failed to parse AI response: {str(e)}")

    def _parse_movie_response(self, response_text: str, movies_folder_name: str) -> OrganizationPlan:
        """Parse AI response for movie collection organization."""
        try:
            # Log full response for debugging
            print(f"Full AI response text: {response_text}")

            # Extract JSON from response
            json_match = re.search(r'```json\s*(\{.*?\})\s*```', response_text, re.DOTALL)
            if not json_match:
                json_match = re.search(r'(\{.*\})', response_text, re.DOTALL)

            if not json_match:
                print(f"No JSON found in response: {response_text[:1000]}")
                raise ValueError("No valid JSON found in AI response")

            json_text = json_match.group(1)

            # Debug output for malformed JSON
            print(f"Extracted JSON text length: {len(json_text)}")
            print(f"Raw JSON response (first 500 chars): {json_text[:500]}")
            print(f"Raw JSON response (last 500 chars): {json_text[-500:]}")



            try:
                data = json.loads(json_text)
            except json.JSONDecodeError as json_err:
                print(f"JSON decode error: {json_err}")
                print(f"Problematic JSON around error: {json_text[max(0, json_err.pos-100):json_err.pos+100]}")
                raise

            # Parse operations into suggestions
            suggestions = []
            for op in data.get('operations', []):
                if op['operation'] == 'create_directory':
                    suggestions.append(OrganizationSuggestion(
                        source_path="",
                        destination_path=op['destination_path'],
                        operation='create_directory',
                        confidence=1.0,
                        reason=op['reason']
                    ))
                elif op['operation'] == 'move':
                    suggestions.append(OrganizationSuggestion(
                        source_path=op['source_path'],
                        destination_path=op['destination_path'],
                        operation='move',
                        confidence=op.get('confidence', 0.8),
                        reason=op['reason']
                    ))

            return OrganizationPlan(
                show_name=data.get('collection_name', movies_folder_name),
                year=None,
                suggestions=suggestions,
                summary=data.get('summary', ''),
                warnings=data.get('warnings', [])
            )

        except (json.JSONDecodeError, KeyError) as e:
            print(f"JSON parsing failed: {str(e)}")
            print(f"Full response that failed: {response_text}")
            raise ValueError(f"Failed to parse AI response: {str(e)}")



    def validate_suggestions(self, plan: OrganizationPlan, base_path: Path) -> Tuple[List[OrganizationSuggestion], List[str]]:
        """
        Validate organization suggestions against the actual filesystem.

        Args:
            plan: Organization plan to validate
            base_path: Base path for the media library

        Returns:
            Tuple of (valid_suggestions, validation_errors)
        """
        valid_suggestions = []
        errors = []

        for suggestion in plan.suggestions:
            if suggestion.operation == 'create_directory':
                # Check if directory already exists
                dest_path = base_path / suggestion.destination_path
                if dest_path.exists():
                    errors.append(f"Directory already exists: {suggestion.destination_path}")
                else:
                    valid_suggestions.append(suggestion)

            elif suggestion.operation == 'move':
                # Check if source exists
                source_path = base_path / suggestion.source_path
                if not source_path.exists():
                    errors.append(f"Source file not found: {suggestion.source_path}")
                    continue

                # Check if destination parent directory would exist
                dest_path = base_path / suggestion.destination_path
                if not dest_path.parent.exists():
                    # This is okay if we're creating the directory in the same plan
                    create_ops = [s for s in plan.suggestions if s.operation == 'create_directory']
                    parent_will_be_created = any(
                        str(dest_path.parent).startswith(str(base_path / s.destination_path))
                        for s in create_ops
                    )
                    if not parent_will_be_created:
                        errors.append(f"Destination directory doesn't exist: {dest_path.parent}")
                        continue

                valid_suggestions.append(suggestion)

        return valid_suggestions, errors

    def test_connection(self) -> bool:
        """Test if the AI connection is working."""
        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents="Hello, please respond with 'OK' if you can understand this message.",
                config=types.GenerateContentConfig(
                    temperature=0.1,
                    max_output_tokens=100
                )
            )
            return "ok" in response.text.lower()
        except Exception:
            return False

    def __del__(self):
        """Cleanup when the organizer is destroyed."""
        if hasattr(self, 'client'):
            self.client.close()
