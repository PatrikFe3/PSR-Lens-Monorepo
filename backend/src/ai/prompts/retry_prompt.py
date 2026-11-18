RETRY_RULES = """

The previous assembly plan was rejected.

Your task is to correct the previous response.

Follow these instructions:
1. Read the validation error carefully.
2. Identify the exact problem in the previous assembly plan.
3. Correct the problem without unnecessarily changing valid components.
4. Preserve valid component IDs and relationships.
5. Return the complete corrected JSON.
6. Follow the original instructions and JSON schema.
"""