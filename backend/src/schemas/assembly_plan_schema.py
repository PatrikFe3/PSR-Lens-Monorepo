ASSEMBLY_PLAN_SCHEMA = {
    "type": "object",
    "properties": {
        "object_type": {
            "type": "string"
        },
        "assembly_plan": {
            "type": "object",
            "properties": {
                "name": {
                    "type": "string"
                },
                "instructions": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "component_id": {
                                "type": "string"
                            },
                            "component_type": {
                                "type": "string"
                            },
                            "parent_id": {
                                "type": ["string", "null"]
                            },
                            "attachment": {
                                "type": ["string", "null"]
                            }
                        },
                        "required": [
                            "component_id",
                            "component_type",
                            "parent_id",
                            "attachment"
                        ],
                        "additionalProperties": False
                    }
                }
            },
            "required": [
                "name",
                "instructions"
            ],
            "additionalProperties": False
        }
    },
    "required": [
        "object_type",
        "assembly_plan"
    ],
    "additionalProperties": False
}