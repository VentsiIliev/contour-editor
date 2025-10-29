"""
Endpoint validation and documentation utilities for API v2.
Provides comprehensive validation, documentation generation, and consistency checking.
"""
from typing import Dict, List, Set, Optional, Any
import re
from dataclasses import dataclass
from enum import Enum

from ..constants.ApiEndpoints import ApiEndpoints, HttpMethod, EndpointGroups, LEGACY_ENDPOINT_MAPPING


@dataclass
class ValidationResult:
    """Result of endpoint validation."""
    is_valid: bool
    endpoint_name: str
    issues: List[str]
    suggestions: List[str]


class EndpointValidator:
    """
    Comprehensive endpoint validation and documentation generator.
    
    Features:
    - Path validation (REST conventions)
    - Method validation
    - Consistency checking
    - Legacy mapping validation
    - Documentation generation
    """
    
    # REST naming conventions
    VALID_RESOURCE_PATTERN = re.compile(r'^[a-z]+(-[a-z]+)*$')
    VALID_PATH_PATTERN = re.compile(r'^/api/v2/[a-z-]+(/[a-z-]+|/\{[a-z_]+\})*$')
    
    @classmethod
    def validate_endpoint(cls, endpoint_name: str) -> ValidationResult:
        """Validate a single endpoint for REST compliance and consistency."""
        if not hasattr(ApiEndpoints, endpoint_name):
            return ValidationResult(
                is_valid=False,
                endpoint_name=endpoint_name,
                issues=[f"Endpoint '{endpoint_name}' not found in ApiEndpoints"],
                suggestions=["Check spelling or add endpoint definition"]
            )
        
        endpoint = getattr(ApiEndpoints, endpoint_name)
        issues = []
        suggestions = []
        
        # Validate path structure
        if not cls.VALID_PATH_PATTERN.match(endpoint.path):
            issues.append(f"Path '{endpoint.path}' doesn't follow REST conventions")
            suggestions.append("Use lowercase, hyphenated paths like /api/v2/resource-name")
        
        # Validate path-method consistency
        path_parts = endpoint.path.strip('/').split('/')
        if len(path_parts) >= 4:
            resource = path_parts[3]  # After /api/v2/
            
            # Check CRUD pattern consistency
            if endpoint.method == HttpMethod.GET:
                if resource.endswith('s') and '{' not in endpoint.path:
                    # Collection GET should be for listing
                    if not endpoint.description.lower().startswith(('get', 'list', 'retrieve')):
                        issues.append("GET collection endpoint should describe listing/retrieving")
                elif '{' in endpoint.path:
                    # Resource GET should be for single item
                    if not endpoint.description.lower().startswith(('get', 'retrieve')):
                        issues.append("GET resource endpoint should describe getting single item")
            
            elif endpoint.method == HttpMethod.POST:
                if not endpoint.description.lower().startswith(('create', 'add', 'execute', 'perform')):
                    suggestions.append("POST endpoints typically create, execute, or perform actions")
            
            elif endpoint.method == HttpMethod.PUT:
                if not endpoint.description.lower().startswith(('update', 'replace', 'set')):
                    suggestions.append("PUT endpoints typically update or replace resources")
            
            elif endpoint.method == HttpMethod.DELETE:
                if not endpoint.description.lower().startswith(('delete', 'remove')):
                    suggestions.append("DELETE endpoints should delete or remove resources")
        
        # Check authentication requirements
        if endpoint.requires_auth and 'auth' in endpoint.path.lower():
            if endpoint_name != 'AUTH_LOGIN' and endpoint_name != 'AUTH_QR_LOGIN':
                issues.append("Authentication endpoints other than login shouldn't require auth")
        
        # Check rate limiting for sensitive operations
        if not endpoint.rate_limited and endpoint.method in [HttpMethod.POST, HttpMethod.PUT, HttpMethod.DELETE]:
            suggestions.append("Mutation operations should typically be rate limited")
        
        return ValidationResult(
            is_valid=len(issues) == 0,
            endpoint_name=endpoint_name,
            issues=issues,
            suggestions=suggestions
        )
    
    @classmethod
    def validate_all_endpoints(cls) -> Dict[str, ValidationResult]:
        """Validate all endpoints in the API."""
        results = {}
        
        for endpoint_name in dir(ApiEndpoints):
            if endpoint_name.startswith('_') or not hasattr(getattr(ApiEndpoints, endpoint_name), 'path'):
                continue
            
            results[endpoint_name] = cls.validate_endpoint(endpoint_name)
        
        return results
    
    @classmethod
    def check_consistency(cls) -> Dict[str, List[str]]:
        """Check consistency across all endpoints."""
        issues = {
            'path_conflicts': [],
            'naming_inconsistencies': [],
            'legacy_mapping_issues': [],
            'group_organization': []
        }
        
        # Check for path conflicts
        paths_seen = {}
        for endpoint_name in dir(ApiEndpoints):
            if endpoint_name.startswith('_'):
                continue
            
            endpoint = getattr(ApiEndpoints, endpoint_name, None)
            if endpoint and hasattr(endpoint, 'path'):
                key = (endpoint.path, endpoint.method.value)
                if key in paths_seen:
                    issues['path_conflicts'].append(
                        f"Path conflict: {endpoint.path} {endpoint.method.value} used by both {paths_seen[key]} and {endpoint_name}"
                    )
                else:
                    paths_seen[key] = endpoint_name
        
        # Check naming consistency
        prefixes = {}
        for endpoint_name in dir(ApiEndpoints):
            if endpoint_name.startswith('_'):
                continue
            
            if '_' in endpoint_name:
                prefix = endpoint_name.split('_')[0]
                if prefix not in prefixes:
                    prefixes[prefix] = []
                prefixes[prefix].append(endpoint_name)
        
        # Check for inconsistent naming within groups
        for prefix, endpoints in prefixes.items():
            if len(endpoints) < 2:
                continue
            
            # Check if all endpoints in group follow similar patterns
            suffixes = [ep.split('_', 1)[1] for ep in endpoints if '_' in ep]
            if len(set(suffix.split('_')[0] for suffix in suffixes)) > 3:
                issues['naming_inconsistencies'].append(
                    f"Group {prefix} has inconsistent naming: {endpoints}"
                )
        
        # Check legacy mapping completeness
        all_endpoints = set(endpoint_name for endpoint_name in dir(ApiEndpoints) 
                           if not endpoint_name.startswith('_') and hasattr(getattr(ApiEndpoints, endpoint_name), 'path'))
        
        mapped_endpoints = set()
        for legacy_path, endpoint in LEGACY_ENDPOINT_MAPPING.items():
            if hasattr(endpoint, 'path'):
                # Find which endpoint this maps to
                for ep_name in all_endpoints:
                    ep = getattr(ApiEndpoints, ep_name)
                    if ep.path == endpoint.path and ep.method == endpoint.method:
                        mapped_endpoints.add(ep_name)
                        break
        
        unmapped_endpoints = all_endpoints - mapped_endpoints
        if unmapped_endpoints:
            issues['legacy_mapping_issues'].append(
                f"Endpoints without legacy mapping: {sorted(unmapped_endpoints)}"
            )
        
        return issues
    
    @classmethod
    def generate_documentation(cls) -> str:
        """Generate comprehensive API documentation."""
        doc = []
        doc.append("# Industrial Automation API v2 - Endpoint Reference")
        doc.append("=" * 60)
        doc.append("")
        doc.append("This document provides a complete reference for all API v2 endpoints.")
        doc.append("")
        
        # Group endpoints by category
        groups = {
            'Authentication': [],
            'System': [],
            'Robot': [],
            'Camera': [],
            'Workpieces': [],
            'Settings': [],
            'Glue': []
        }
        
        for endpoint_name in sorted(dir(ApiEndpoints)):
            if endpoint_name.startswith('_'):
                continue
            
            endpoint = getattr(ApiEndpoints, endpoint_name, None)
            if not endpoint or not hasattr(endpoint, 'path'):
                continue
            
            # Categorize by first part of endpoint name
            category = endpoint_name.split('_')[0].title()
            if category in groups:
                groups[category].append((endpoint_name, endpoint))
            else:
                # Try to infer from path
                path_parts = endpoint.path.strip('/').split('/')
                if len(path_parts) >= 4:
                    resource = path_parts[3].title()
                    if resource in groups:
                        groups[resource].append((endpoint_name, endpoint))
                    else:
                        groups['System'].append((endpoint_name, endpoint))
        
        # Generate documentation for each group
        for group_name, endpoints in groups.items():
            if not endpoints:
                continue
            
            doc.append(f"## {group_name} Endpoints")
            doc.append("-" * (len(group_name) + 11))
            doc.append("")
            
            for endpoint_name, endpoint in sorted(endpoints):
                doc.append(f"### {endpoint_name}")
                doc.append(f"- **Path**: `{endpoint.path}`")
                doc.append(f"- **Method**: `{endpoint.method.value}`")
                doc.append(f"- **Description**: {endpoint.description}")
                doc.append(f"- **Requires Authentication**: {'Yes' if endpoint.requires_auth else 'No'}")
                doc.append(f"- **Rate Limited**: {'Yes' if endpoint.rate_limited else 'No'}")
                doc.append("")
        
        # Add legacy compatibility section
        doc.append("## Legacy Compatibility")
        doc.append("---------------------")
        doc.append("")
        doc.append("The following legacy paths are automatically converted to v2 endpoints:")
        doc.append("")
        
        for legacy_path, v2_endpoint in sorted(LEGACY_ENDPOINT_MAPPING.items()):
            doc.append(f"- `{legacy_path}` → `{v2_endpoint.method.value} {v2_endpoint.path}`")
        
        doc.append("")
        doc.append("## Validation Summary")
        doc.append("-------------------")
        doc.append("")
        
        # Add validation summary
        validation_results = cls.validate_all_endpoints()
        total_endpoints = len(validation_results)
        valid_endpoints = sum(1 for result in validation_results.values() if result.is_valid)
        
        doc.append(f"- **Total Endpoints**: {total_endpoints}")
        doc.append(f"- **Valid Endpoints**: {valid_endpoints}")
        doc.append(f"- **Issues Found**: {total_endpoints - valid_endpoints}")
        doc.append("")
        
        if valid_endpoints < total_endpoints:
            doc.append("### Validation Issues")
            doc.append("")
            for result in validation_results.values():
                if not result.is_valid:
                    doc.append(f"**{result.endpoint_name}**:")
                    for issue in result.issues:
                        doc.append(f"  - ❌ {issue}")
                    for suggestion in result.suggestions:
                        doc.append(f"  - 💡 {suggestion}")
                    doc.append("")
        
        return "\n".join(doc)
    
    @classmethod
    def export_openapi_schema(cls) -> Dict[str, Any]:
        """Export endpoints as OpenAPI 3.0 schema."""
        schema = {
            "openapi": "3.0.0",
            "info": {
                "title": "Industrial Automation API",
                "version": "2.0.0",
                "description": "RESTful API for industrial automation and glue dispensing system"
            },
            "servers": [
                {"url": "/api/v2", "description": "API v2 base URL"}
            ],
            "paths": {},
            "components": {
                "securitySchemes": {
                    "SessionAuth": {
                        "type": "apiKey",
                        "in": "header",
                        "name": "Authorization"
                    }
                }
            }
        }
        
        for endpoint_name in sorted(dir(ApiEndpoints)):
            if endpoint_name.startswith('_'):
                continue
            
            endpoint = getattr(ApiEndpoints, endpoint_name, None)
            if not endpoint or not hasattr(endpoint, 'path'):
                continue
            
            path = endpoint.path.replace('/api/v2', '')  # Remove base path
            method = endpoint.method.value.lower()
            
            if path not in schema["paths"]:
                schema["paths"][path] = {}
            
            operation = {
                "summary": endpoint.description,
                "operationId": endpoint_name.lower(),
                "responses": {
                    "200": {
                        "description": "Success response",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "success": {"type": "boolean"},
                                        "message": {"type": "string"},
                                        "data": {"type": "object"}
                                    }
                                }
                            }
                        }
                    },
                    "400": {"description": "Bad request"},
                    "401": {"description": "Unauthorized"},
                    "500": {"description": "Internal server error"}
                }
            }
            
            if endpoint.requires_auth:
                operation["security"] = [{"SessionAuth": []}]
            
            schema["paths"][path][method] = operation
        
        return schema


# Convenience functions for common validation tasks
def validate_endpoint_name(name: str) -> bool:
    """Quick validation of endpoint name."""
    result = EndpointValidator.validate_endpoint(name)
    return result.is_valid


def get_endpoint_issues(name: str) -> List[str]:
    """Get validation issues for specific endpoint."""
    result = EndpointValidator.validate_endpoint(name)
    return result.issues + result.suggestions


def generate_api_docs() -> str:
    """Generate complete API documentation."""
    return EndpointValidator.generate_documentation()


if __name__ == "__main__":
    # Example usage
    print("🔍 API v2 Endpoint Validation Report")
    print("=" * 40)
    
    # Validate all endpoints
    results = EndpointValidator.validate_all_endpoints()
    
    valid_count = sum(1 for r in results.values() if r.is_valid)
    total_count = len(results)
    
    print(f"📊 Summary: {valid_count}/{total_count} endpoints valid")
    print()
    
    # Show issues
    has_issues = False
    for result in results.values():
        if not result.is_valid or result.suggestions:
            if not has_issues:
                print("⚠️  Issues Found:")
                has_issues = True
            
            print(f"\n{result.endpoint_name}:")
            for issue in result.issues:
                print(f"  ❌ {issue}")
            for suggestion in result.suggestions:
                print(f"  💡 {suggestion}")
    
    if not has_issues:
        print("✅ All endpoints pass validation!")
    
    # Check consistency
    print("\n🔗 Consistency Check:")
    consistency = EndpointValidator.check_consistency()
    
    for category, issues in consistency.items():
        if issues:
            print(f"\n{category.replace('_', ' ').title()}:")
            for issue in issues:
                print(f"  ⚠️  {issue}")
    
    print("\n📚 Documentation generated successfully!")