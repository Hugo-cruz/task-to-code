"""Confluence and JIRA API client for extracting task data."""

import requests
import base64
from typing import Dict, Any, Optional, List
from urllib.parse import urljoin
import json


class ConfluenceJiraClient:
    """Client for interacting with Confluence and JIRA APIs."""
    
    def __init__(self, base_url: str, username: str, api_token: str):
        """
        Initialize the Confluence/JIRA client.
        
        Args:
            base_url: Base URL for your Atlassian instance (e.g., https://company.atlassian.net)
            username: Your Atlassian username/email
            api_token: Your Atlassian API token
        """
        self.base_url = base_url.rstrip('/')
        self.username = username
        self.api_token = api_token
        
        # Create authentication header
        auth_string = f"{username}:{api_token}"
        auth_bytes = auth_string.encode('ascii')
        auth_b64 = base64.b64encode(auth_bytes).decode('ascii')
        
        self.headers = {
            'Authorization': f'Basic {auth_b64}',
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }
        
        self.session = requests.Session()
        self.session.headers.update(self.headers)
    
    def get_confluence_page(self, page_id: str) -> Dict[str, Any]:
        """
        Get a Confluence page by ID.
        
        Args:
            page_id: The ID of the Confluence page
            
        Returns:
            Dictionary containing page data
        """
        url = f"{self.base_url}/wiki/api/v2/pages/{page_id}"
        params = {
            'body-format': 'atlas_doc_format',
            'include-labels': 'true'
        }
        
        response = self.session.get(url, params=params)
        response.raise_for_status()
        
        return response.json()
    
    def get_confluence_page_content(self, page_id: str) -> str:
        """
        Get the content of a Confluence page as plain text.
        
        Args:
            page_id: The ID of the Confluence page
            
        Returns:
            Plain text content of the page
        """
        page_data = self.get_confluence_page(page_id)
        
        # Extract content from the atlas document format
        body = page_data.get('body', {})
        atlas_doc = body.get('atlas_doc_format', {})
        content = atlas_doc.get('value', '')
        
        # Parse the atlas document format to extract text
        return self._extract_text_from_atlas_doc(content)
    
    def get_jira_issue(self, issue_key: str) -> Dict[str, Any]:
        """
        Get a JIRA issue by key.
        
        Args:
            issue_key: The key of the JIRA issue (e.g., 'PROJ-123')
            
        Returns:
            Dictionary containing issue data
        """
        url = f"{self.base_url}/rest/api/3/issue/{issue_key}"
        params = {
            'expand': 'renderedFields,names,schema,operations,editmeta,changelog'
        }
        
        response = self.session.get(url, params=params)
        response.raise_for_status()
        
        return response.json()
    
    def get_jira_issue_details(self, issue_key: str) -> Dict[str, Any]:
        """
        Get formatted JIRA issue details for code generation.
        
        Args:
            issue_key: The key of the JIRA issue
            
        Returns:
            Dictionary with formatted issue details
        """
        issue = self.get_jira_issue(issue_key)
        fields = issue.get('fields', {})
        rendered_fields = issue.get('renderedFields', {})
        
        return {
            'key': issue.get('key'),
            'summary': fields.get('summary'),
            'description': rendered_fields.get('description', ''),
            'issue_type': fields.get('issuetype', {}).get('name'),
            'priority': fields.get('priority', {}).get('name'),
            'status': fields.get('status', {}).get('name'),
            'assignee': fields.get('assignee', {}).get('displayName') if fields.get('assignee') else None,
            'reporter': fields.get('reporter', {}).get('displayName') if fields.get('reporter') else None,
            'labels': fields.get('labels', []),
            'components': [comp.get('name') for comp in fields.get('components', [])],
            'acceptance_criteria': self._extract_acceptance_criteria(rendered_fields.get('description', '')),
            'subtasks': [
                {
                    'key': subtask.get('key'),
                    'summary': subtask.get('fields', {}).get('summary'),
                    'status': subtask.get('fields', {}).get('status', {}).get('name')
                }
                for subtask in fields.get('subtasks', [])
            ]
        }
    
    def search_jira_issues(self, jql: str, max_results: int = 50) -> List[Dict[str, Any]]:
        """
        Search for JIRA issues using JQL.
        
        Args:
            jql: JQL query string
            max_results: Maximum number of results to return
            
        Returns:
            List of issue dictionaries
        """
        url = f"{self.base_url}/rest/api/3/search"
        payload = {
            'jql': jql,
            'maxResults': max_results,
            'fields': ['summary', 'status', 'assignee', 'issuetype', 'priority']
        }
        
        response = self.session.post(url, json=payload)
        response.raise_for_status()
        
        result = response.json()
        return result.get('issues', [])
    
    def _extract_text_from_atlas_doc(self, atlas_content: str) -> str:
        """
        Extract plain text from Confluence's Atlas Document Format.
        
        Args:
            atlas_content: Atlas document format content as string
            
        Returns:
            Plain text content
        """
        try:
            # Parse the atlas document format JSON
            doc = json.loads(atlas_content) if isinstance(atlas_content, str) else atlas_content
            
            def extract_text_recursive(node):
                text = ""
                
                if isinstance(node, dict):
                    # Handle text nodes
                    if node.get('type') == 'text':
                        text += node.get('text', '')
                    
                    # Handle other node types with content
                    if 'content' in node:
                        for child in node['content']:
                            text += extract_text_recursive(child)
                    
                    # Add line breaks for certain block elements
                    if node.get('type') in ['paragraph', 'heading', 'listItem']:
                        text += '\n'
                
                elif isinstance(node, list):
                    for item in node:
                        text += extract_text_recursive(item)
                
                return text
            
            return extract_text_recursive(doc).strip()
            
        except (json.JSONDecodeError, TypeError, KeyError):
            # If parsing fails, return the content as-is or empty string
            return str(atlas_content) if atlas_content else ""
    
    def _extract_acceptance_criteria(self, description: str) -> List[str]:
        """
        Extract acceptance criteria from issue description.
        
        Args:
            description: Issue description text
            
        Returns:
            List of acceptance criteria
        """
        criteria = []
        lines = description.split('\n')
        
        in_acceptance_section = False
        for line in lines:
            line = line.strip()
            
            # Look for acceptance criteria section
            if 'acceptance criteria' in line.lower():
                in_acceptance_section = True
                continue
            
            # If we're in the acceptance criteria section
            if in_acceptance_section:
                # Stop if we hit another section
                if line.startswith('#') or line.startswith('**'):
                    break
                
                # Extract criteria (usually bulleted or numbered)
                if line.startswith(('-', '*', '•')) or line[0:2].replace('.', '').isdigit():
                    criteria.append(line.lstrip('- *•0123456789. '))
        
        return criteria
