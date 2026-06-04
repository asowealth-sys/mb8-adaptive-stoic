from __future__ import annotations

from typing import Any


def custom_gpt_openapi_schema(base_url: str = "https://example.com") -> dict[str, Any]:
    return {
        "openapi": "3.1.0",
        "info": {
            "title": "MB 8.0 Adaptive STOIC Actions",
            "version": "0.2.0",
            "description": "Custom GPT Actions schema for deterministic MB 8.0 runs and run history.",
        },
        "servers": [{"url": base_url.rstrip("/")}],
        "paths": {
            "/run-mb8-json": {
                "post": {
                    "operationId": "runMb8FromJsonRecords",
                    "summary": "Run MB 8.0 from JSON records, CSV text, or XLSX base64",
                    "security": [{"ApiKeyAuth": []}],
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/MB8JsonRunRequest"}
                            }
                        },
                    },
                    "responses": {
                        "200": {
                            "description": "MB 8.0 run payload with final slip, rejected picks, and audit logs.",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/MB8RunResponse"}
                                }
                            },
                        }
                    },
                }
            },
            "/runs": {
                "get": {
                    "operationId": "listMb8Runs",
                    "summary": "List saved MB 8.0 runs",
                    "security": [{"ApiKeyAuth": []}],
                    "parameters": [
                        {
                            "name": "limit",
                            "in": "query",
                            "required": False,
                            "schema": {"type": "integer", "default": 25},
                        }
                    ],
                    "responses": {
                        "200": {
                            "description": "Saved run summaries.",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "runs": {
                                                "type": "array",
                                                "items": {"$ref": "#/components/schemas/MB8RunSummary"},
                                            }
                                        },
                                    }
                                }
                            },
                        }
                    },
                }
            },
            "/runs/{run_id}": {
                "get": {
                    "operationId": "getMb8Run",
                    "summary": "Get one saved MB 8.0 run",
                    "security": [{"ApiKeyAuth": []}],
                    "parameters": [
                        {
                            "name": "run_id",
                            "in": "path",
                            "required": True,
                            "schema": {"type": "string"},
                        }
                    ],
                    "responses": {
                        "200": {
                            "description": "Saved run with full MB 8.0 result.",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/MB8StoredRun"}
                                }
                            },
                        }
                    },
                }
            },
        },
        "components": {
            "schemas": {
                "MB8JsonRunRequest": {
                    "type": "object",
                    "description": "Provide exactly one dataset input: records, csv_text, or xlsx_base64.",
                    "properties": {
                        "source_filename": {"type": "string", "default": "custom-gpt-records.json"},
                        "records": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "additionalProperties": True,
                                "required": ["home_team", "away_team", "league", "market", "odds"],
                                "properties": {
                                    "home_team": {"type": "string"},
                                    "away_team": {"type": "string"},
                                    "league": {"type": "string"},
                                    "market": {"type": "string"},
                                    "odds": {"type": "number"},
                                },
                            },
                        },
                        "csv_text": {
                            "type": "string",
                            "description": "Raw CSV text extracted from an uploaded CSV file.",
                        },
                        "xlsx_base64": {
                            "type": "string",
                            "description": "Base64-encoded XLSX bytes extracted from an uploaded Excel file.",
                        },
                    },
                },
                "MB8RunSummary": {
                    "type": "object",
                    "properties": {
                        "run_id": {"type": "string"},
                        "source_filename": {"type": "string"},
                        "total_rows": {"type": "integer"},
                        "final_count": {"type": "integer"},
                        "rejected_count": {"type": "integer"},
                        "created_at": {"type": "string"},
                    },
                },
                "MB8RunResponse": {
                    "type": "object",
                    "properties": {
                        "run_id": {"type": "string"},
                        "source_filename": {"type": "string"},
                        "total_rows": {"type": "integer"},
                        "final_count": {"type": "integer"},
                        "rejected_count": {"type": "integer"},
                        "result": {"type": "object", "additionalProperties": True},
                    },
                },
                "MB8StoredRun": {
                    "allOf": [
                        {"$ref": "#/components/schemas/MB8RunSummary"},
                        {
                            "type": "object",
                            "properties": {
                                "result": {"type": "object", "additionalProperties": True}
                            },
                        },
                    ]
                },
            },
            "securitySchemes": {
                "ApiKeyAuth": {
                    "type": "apiKey",
                    "in": "header",
                    "name": "X-MB8-API-Key",
                }
            },
        },
    }
