# Rules for assembly plan creation
ASSEMBLY_RULES = """
Available component types:
- brick_1x1
- brick_2x1
- brick_2x2
- brick_4x2
- brick_4x4
- brick_6x2

Rules:
1. Use only the available component types.
2. Every component must have a unique component_id.
3. Exactly one component must be the root component, and must have:
 - parent_id = null
 - attachment = null
4. Every other component:
 - must reference an existing component_id as parent_id
 - must use attachment = "top"
5. Use "top" as attachment when placing a component above its parent.
6. Keep the assembly appropriate for the requested complexity.
7. Create a plan that can be assembled from the available components.
8. Return only data matching the provided JSON schema.

Example of a valid root component:

{{
    "component_id": "base",
    "component_type": "brick_4x2",
    "parent_id": null,
    "attachment": null
}}

Example of a valid child component:

{{
    "component_id": "body",
    "component_type": "brick_2x2",
    "parent_id": "base",
    "attachment": "top"
}}
"""