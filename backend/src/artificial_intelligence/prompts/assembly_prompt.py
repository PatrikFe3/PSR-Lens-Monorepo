# Rules for assembly plan creation
ASSEMBLY_RULES = """
Rules for assembly plan creation

Available component types:
- brick_1x1
- brick_2x1
- brick_2x2
- brick_4x2
- brick_4x4
- brick_6x2

Available attachment directions:
- top
- bottom
- left
- right
- front
- back

Rules:
1. Use only the available component types.
2. Every component must have a unique component_id.
3. Exactly one component must be the root component.
4. The root component must have:
   - parent_id = null
   - attachment = null
5. Every non-root component:
   - must reference an existing component_id as parent_id
   - use exactly one of the available attachment directions
   - have a parent_id different from its own component_id
6. Every component must be connected to the root component through parent relationships.
7. Do not create circular parent relationships.
8. Keep the assembly appropriate for the requested complexity.
9. Create a plan that can be assembled from the available components.
10. Return only data matching the provided JSON schema.

Example:

{{
  "assembly_plan": {{
    "name": "Simple Modular Structure",
    "instructions": [
      {{
        "component_id": "base",
        "component_type": "brick_4x2",
        "parent_id": null,
        "attachment": null
      }},
      {{
        "component_id": "upper",
        "component_type": "brick_2x2",
        "parent_id": "base",
        "attachment": "top"
      }},
      {{
        "component_id": "left_module",
        "component_type": "brick_2x1",
        "parent_id": "base",
        "attachment": "left"
      }},
      {{
        "component_id": "right_module",
        "component_type": "brick_2x1",
        "parent_id": "base",
        "attachment": "right"
      }},
      {{
        "component_id": "front_module",
        "component_type": "brick_1x1",
        "parent_id": "base",
        "attachment": "front"
      }},
      {{
        "component_id": "back_module",
        "component_type": "brick_1x1",
        "parent_id": "base",
        "attachment": "back"
      }}
    ]
  }},
  "object_type": "assembly_plan"
}}
"""