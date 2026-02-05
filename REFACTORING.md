# Refactoring: Runnables and Parallel Runnables Implementation

## Overview

This document explains the refactoring of `app.py` from a custom `SimpleChain` implementation to using LangChain's modern LCEL (LangChain Expression Language) with Runnables, Parallel Runnables, and Output Parsers, following the "Notebook 24" pattern.

## Key Changes

### 1. From Simple Chain to Runnables

**Before:**
```python
class SimpleChain:
    """Chaîne simple pour exécuter des prompts"""
    def __init__(self, llm, prompt_template):
        self.llm = llm
        self.prompt_template = prompt_template
    
    def run(self, text):
        prompt = self.prompt_template.replace("{text}", text)
        response = self.llm.invoke(prompt)
        return response.content if hasattr(response, 'content') else str(response)
```

**After:**
```python
# Notebook 24 Pattern: Preparation function
prep_for_template = RunnableLambda(lambda text: {"text": text})

# Build the chain using LCEL
chain = prep_for_template | PROMPT_TEMPLATE | llm | json_parser
```

### 2. Structured Prompt Templates

**Before:**
```python
PROMPT_TEMPLATE = """
Analyse cette phrase : "{text}"
...
"""
```

**After:**
```python
PROMPT_TEMPLATE = ChatPromptTemplate.from_template("""
Analyse cette phrase : "{text}"
...
""")
```

### 3. Automatic JSON Parsing

**Before:**
```python
response = chain.run(text)
response = response.strip()
start = response.find('{')
end = response.rfind('}') + 1
if start != -1 and end != 0:
    json_str = response[start:end]
    result = json.loads(json_str)
```

**After:**
```python
json_parser = JsonOutputParser()
chain = prep_for_template | PROMPT_TEMPLATE | llm | json_parser
result = chain.invoke(text)  # Automatically parsed!
```

### 4. Parallel Runnables

**New Feature:**
```python
parallel_chain = RunnableParallel(
    main_analysis=chain,
    metadata=RunnableLambda(lambda text: {
        "length": len(text),
        "word_count": len(text.split()),
        "has_punctuation": any(c in text for c in "!?.")
    })
)

# Both tasks run in parallel
parallel_result = parallel_chain.invoke(text)
result = parallel_result["main_analysis"]
metadata = parallel_result["metadata"]
```

## Architecture Pattern (Notebook 24)

The implementation follows the "Notebook 24" pattern for parallel chains and runnables:

```
Input Text
    │
    ├─────────────────┬─────────────────┐
    │                 │                 │
    ▼                 ▼                 ▼
prep_for_template   main_analysis    metadata
    │                 │                 │
    ▼                 │                 │
{"text": text}       │                 │
    │                 │                 │
    ├─────────────────┘                 │
    │                                   │
    ▼                                   │
PROMPT_TEMPLATE                         │
    │                                   │
    ▼                                   │
   LLM                                  │
    │                                   │
    ▼                                   │
json_parser                             │
    │                                   │
    └──────────────┬──────────────────┘
                   │
                   ▼
           Parallel Results
        {main_analysis, metadata}
```

## Benefits

1. **Composability**: Chains can be easily composed using the pipe operator (`|`)
2. **Type Safety**: Better type hints and validation
3. **Automatic Parsing**: Output parsers handle JSON parsing automatically
4. **Parallel Execution**: Multiple tasks can run in parallel
5. **Maintainability**: Cleaner, more modular code
6. **Debugging**: Better error messages and stack traces
7. **Standard Pattern**: Uses LangChain's recommended LCEL approach

## Components Used

- **RunnableLambda**: Wraps a function to make it a runnable component
- **RunnableParallel**: Runs multiple runnables in parallel
- **ChatPromptTemplate**: Structured prompt template with variable substitution
- **JsonOutputParser**: Automatically parses JSON from LLM responses
- **LCEL Pipe Operator (`|`)**: Chains components together

## Testing

Run the test script to verify the implementation:

```bash
python3 test_chains.py
```

## References

- [LangChain Expression Language (LCEL)](https://python.langchain.com/docs/expression_language/)
- [Runnables](https://python.langchain.com/docs/expression_language/primitives/runnables)
- [Output Parsers](https://python.langchain.com/docs/modules/model_io/output_parsers/)
