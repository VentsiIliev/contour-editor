"""
Statistics endpoints for API v2.
Defines all statistics-related endpoints with their HTTP methods and metadata.
"""
from enum import Enum
from typing import Dict, List, Optional
from dataclasses import dataclass
from .ApiEndpoints import Endpoint, HttpMethod


class StatisticsEndpoints:
    """
    Statistics-related API endpoints for the glue dispensing system.
    
    Provides endpoints for:
    - Reading component statistics (generator, transducer, pumps, fan, loadcells)
    - Resetting component statistics
    - System-wide statistics management
    """
    
    # ============================================================================
    # READ OPERATIONS (GET) - Statistics retrieval
    # ============================================================================
    
    STATS_ALL = Endpoint(
        path="/api/v2/stats/all",
        method=HttpMethod.GET,
        description="Get all system statistics",
        rate_limited=False
    )
    
    STATS_GENERATOR = Endpoint(
        path="/api/v2/stats/generator",
        method=HttpMethod.GET,
        description="Get generator statistics",
        rate_limited=False
    )
    
    STATS_TRANSDUCER = Endpoint(
        path="/api/v2/stats/transducer", 
        method=HttpMethod.GET,
        description="Get transducer statistics",
        rate_limited=False
    )
    
    STATS_PUMPS = Endpoint(
        path="/api/v2/stats/pumps",
        method=HttpMethod.GET,
        description="Get all pump statistics",
        rate_limited=False
    )
    
    STATS_PUMP_BY_ID = Endpoint(
        path="/api/v2/stats/pumps/{pump_id}",
        method=HttpMethod.GET,
        description="Get specific pump statistics by ID",
        rate_limited=False
    )
    
    STATS_FAN = Endpoint(
        path="/api/v2/stats/fan",
        method=HttpMethod.GET,
        description="Get fan statistics", 
        rate_limited=False
    )
    
    STATS_LOADCELLS = Endpoint(
        path="/api/v2/stats/loadcells",
        method=HttpMethod.GET,
        description="Get all loadcell statistics",
        rate_limited=False
    )
    
    STATS_LOADCELL_BY_ID = Endpoint(
        path="/api/v2/stats/loadcells/{loadcell_id}",
        method=HttpMethod.GET,
        description="Get specific loadcell statistics by ID",
        rate_limited=False
    )
    
    # ============================================================================
    # WRITE / ACTION OPERATIONS (POST) - Statistics reset operations
    # ============================================================================
    
    RESET_ALL_STATS = Endpoint(
        path="/api/v2/stats/reset/all",
        method=HttpMethod.POST,
        description="Reset all system statistics"
    )
    
    RESET_GENERATOR = Endpoint(
        path="/api/v2/stats/reset/generator",
        method=HttpMethod.POST,
        description="Reset generator statistics"
    )
    
    RESET_TRANSDUCER = Endpoint(
        path="/api/v2/stats/reset/transducer",
        method=HttpMethod.POST,
        description="Reset transducer statistics"
    )
    
    RESET_FAN = Endpoint(
        path="/api/v2/stats/reset/fan",
        method=HttpMethod.POST,
        description="Reset fan statistics"
    )
    
    RESET_PUMP_MOTOR = Endpoint(
        path="/api/v2/stats/reset/pumps/{pump_id}/motor",
        method=HttpMethod.POST,
        description="Reset specific pump motor statistics"
    )
    
    RESET_PUMP_BELT = Endpoint(
        path="/api/v2/stats/reset/pumps/{pump_id}/belt",
        method=HttpMethod.POST,
        description="Reset specific pump belt statistics"
    )
    
    RESET_LOADCELL = Endpoint(
        path="/api/v2/stats/reset/loadcells/{loadcell_id}",
        method=HttpMethod.POST,
        description="Reset specific loadcell statistics"
    )
    
    # ============================================================================
    # STATISTICS EXPORT AND REPORTING (GET/POST)
    # ============================================================================
    
    STATS_EXPORT_CSV = Endpoint(
        path="/api/v2/stats/export/csv",
        method=HttpMethod.POST,
        description="Export statistics data as CSV"
    )
    
    STATS_EXPORT_JSON = Endpoint(
        path="/api/v2/stats/export/json", 
        method=HttpMethod.POST,
        description="Export statistics data as JSON"
    )
    
    STATS_REPORT_DAILY = Endpoint(
        path="/api/v2/stats/reports/daily",
        method=HttpMethod.GET,
        description="Get daily statistics report",
        rate_limited=False
    )
    
    STATS_REPORT_WEEKLY = Endpoint(
        path="/api/v2/stats/reports/weekly",
        method=HttpMethod.GET,
        description="Get weekly statistics report",
        rate_limited=False
    )
    
    STATS_REPORT_MONTHLY = Endpoint(
        path="/api/v2/stats/reports/monthly",
        method=HttpMethod.GET,
        description="Get monthly statistics report",
        rate_limited=False
    )


class StatisticsEndpointGroups:
    """Logical grouping of statistics endpoints."""
    
    READ_OPERATIONS = [
        StatisticsEndpoints.STATS_ALL,
        StatisticsEndpoints.STATS_GENERATOR,
        StatisticsEndpoints.STATS_TRANSDUCER,
        StatisticsEndpoints.STATS_PUMPS,
        StatisticsEndpoints.STATS_PUMP_BY_ID,
        StatisticsEndpoints.STATS_FAN,
        StatisticsEndpoints.STATS_LOADCELLS,
        StatisticsEndpoints.STATS_LOADCELL_BY_ID,
    ]
    
    RESET_OPERATIONS = [
        StatisticsEndpoints.RESET_ALL_STATS,
        StatisticsEndpoints.RESET_GENERATOR,
        StatisticsEndpoints.RESET_TRANSDUCER,
        StatisticsEndpoints.RESET_FAN,
        StatisticsEndpoints.RESET_PUMP_MOTOR,
        StatisticsEndpoints.RESET_PUMP_BELT,
        StatisticsEndpoints.RESET_LOADCELL,
    ]
    
    EXPORT_OPERATIONS = [
        StatisticsEndpoints.STATS_EXPORT_CSV,
        StatisticsEndpoints.STATS_EXPORT_JSON,
        StatisticsEndpoints.STATS_REPORT_DAILY,
        StatisticsEndpoints.STATS_REPORT_WEEKLY,
        StatisticsEndpoints.STATS_REPORT_MONTHLY,
    ]
    
    @classmethod
    def get_all_statistics_endpoints(cls) -> List[Endpoint]:
        """Get all statistics endpoints."""
        return cls.READ_OPERATIONS + cls.RESET_OPERATIONS + cls.EXPORT_OPERATIONS


# Legacy endpoint mapping for backwards compatibility
STATISTICS_LEGACY_MAPPING = {
    # Read operations - map old paths to new endpoints
    "stats/generator": StatisticsEndpoints.STATS_GENERATOR,
    "stats/transducer": StatisticsEndpoints.STATS_TRANSDUCER,
    "stats/pumps": StatisticsEndpoints.STATS_PUMPS,
    "stats/pumps/{pump_id}": StatisticsEndpoints.STATS_PUMP_BY_ID,
    "stats/fan": StatisticsEndpoints.STATS_FAN,
    "stats/loadcells": StatisticsEndpoints.STATS_LOADCELLS,
    "stats/loadcells/{loadcell_id}": StatisticsEndpoints.STATS_LOADCELL_BY_ID,
    
    # Reset operations - map old paths to new endpoints
    "reset/generator": StatisticsEndpoints.RESET_GENERATOR,
    "reset/transducer": StatisticsEndpoints.RESET_TRANSDUCER,
    "reset/fan": StatisticsEndpoints.RESET_FAN,
    "reset/pumps/{pump_id}/motor": StatisticsEndpoints.RESET_PUMP_MOTOR,
    "reset/pumps/{pump_id}/belt": StatisticsEndpoints.RESET_PUMP_BELT,
    "reset/loadcells/{loadcell_id}": StatisticsEndpoints.RESET_LOADCELL,
}


def get_statistics_endpoint_by_legacy_path(legacy_path: str) -> Optional[Endpoint]:
    """Convert legacy statistics endpoint path to v2 endpoint."""
    return STATISTICS_LEGACY_MAPPING.get(legacy_path)


if __name__ == "__main__":
    # Demo usage
    print("= Statistics API v2 Endpoints")
    print("=" * 40)
    
    groups = StatisticsEndpointGroups
    for group_name in ['READ_OPERATIONS', 'RESET_OPERATIONS', 'EXPORT_OPERATIONS']:
        group = getattr(groups, group_name)
        print(f"\n{group_name.replace('_', ' ').title()} ({len(group)} endpoints):")
        print("-" * 30)
        for ep in group:
            print(f"  {ep.method_str:6} {ep.path:40} - {ep.description}")
    
    print(f"\nTotal Statistics Endpoints: {len(groups.get_all_statistics_endpoints())}")
    print(f"Legacy Mappings: {len(STATISTICS_LEGACY_MAPPING)}")