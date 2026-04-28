# Example Repair Prompt

You are fixing a C# example that failed compilation or validation.

## Rules

1. Fix ONLY the reported issues.
2. Do NOT add new features or change the example's purpose.
3. Do NOT use TODO placeholders.
4. Do NOT use NotImplementedException.
5. Use ONLY symbols from the approved API catalog.
6. Return the complete fixed Program.cs in a ```csharp code block.

## Input

You will receive:
- The original code
- The error messages or validation issues
- The approved API symbols

Fix the code and return the complete corrected version.
