# Architecture Comparison

## Before: Custom SimpleChain

```
User Input (text)
       ↓
SimpleChain.run()
       ↓
Manual string.replace()
       ↓
     LLM
       ↓
Manual JSON extraction
  - Find '{'
  - Find '}'
  - Parse JSON
       ↓
Display Result
```

**Issues:**
- ❌ Manual string manipulation
- ❌ Error-prone JSON extraction
- ❌ No parallel processing
- ❌ Not composable
- ❌ Custom implementation

## After: Runnables & Parallel Runnables (Notebook 24 Pattern)

```
User Input (text)
       │
       ├─────────────────┬──────────────────┐
       │                 │                  │
       ▼                 ▼                  ▼
   Main Branch      Metadata Branch   (Future Branches...)
       │                 │
       ▼                 ▼
prep_for_template  prep_for_template
   {"text": text}    {"text": text}
       │                 │
       ▼                 ▼
ChatPromptTemplate  RunnableLambda
       │            (compute metadata)
       ▼                 │
      LLM                │
       │                 │
       ▼                 │
JsonOutputParser          │
  (automatic!)            │
       │                 │
       └────────┬────────┘
                │
                ▼
     RunnableParallel Result
    {main_analysis, metadata}
                │
                ▼
         Display Results
```

**Benefits:**
- ✅ Type-safe templates
- ✅ Automatic JSON parsing
- ✅ Parallel execution
- ✅ Composable chains
- ✅ Standard LangChain patterns
- ✅ Better error handling

## Code Comparison

### Before (Custom Chain)
```python
class SimpleChain:
    def __init__(self, llm, prompt_template):
        self.llm = llm
        self.prompt_template = prompt_template
    
    def run(self, text):
        prompt = self.prompt_template.replace("{text}", text)
        response = self.llm.invoke(prompt)
        return response.content

# Usage
chain = SimpleChain(llm, PROMPT_TEMPLATE)
response = chain.run(text)

# Manual JSON extraction
start = response.find('{')
end = response.rfind('}') + 1
json_str = response[start:end]
result = json.loads(json_str)
```

### After (Runnables)
```python
# Notebook 24 Pattern
prep_for_template = RunnableLambda(lambda text: {"text": text})

# LCEL Chain Composition
chain = prep_for_template | PROMPT_TEMPLATE | llm | json_parser

# Parallel Execution
parallel_chain = RunnableParallel(
    main_analysis=chain,
    metadata=prep_for_template | RunnableLambda(lambda data: {...})
)

# Usage - Automatic!
parallel_result = parallel_chain.invoke(text)
result = parallel_result["main_analysis"]  # Already parsed!
metadata = parallel_result["metadata"]
```

## Key Improvements

| Aspect | Before | After |
|--------|--------|-------|
| **Chain Building** | Custom class | LCEL with pipe operator |
| **Input Preparation** | String replace | RunnableLambda |
| **Template** | String | ChatPromptTemplate |
| **JSON Parsing** | Manual extraction | JsonOutputParser |
| **Parallel Tasks** | None | RunnableParallel |
| **Error Handling** | Try/catch | Built-in |
| **Composability** | Limited | High |
| **Type Safety** | None | Yes |

## Performance Gains

- **Parallel Execution**: Metadata computed while LLM processes (faster)
- **No Manual Parsing**: Reduces processing overhead
- **Error Prevention**: Type-safe templates prevent runtime errors

## Maintainability

- **Standard Patterns**: Other developers familiar with LangChain understand instantly
- **Extensibility**: Easy to add more parallel branches
- **Testing**: Each component testable independently
- **Debugging**: Better stack traces and error messages
