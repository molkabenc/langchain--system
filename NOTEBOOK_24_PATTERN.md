# Notebook 24 Pattern Implementation

This document demonstrates the exact implementation of the "Notebook 24" pattern in our Streamlit application.

## Pattern: prep_for_template with RunnableLambda

### Core Implementation

```python
from langchain_core.runnables import RunnableLambda, RunnableParallel
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser

# 1. Preparation function (Notebook 24 pattern)
prep_for_template = RunnableLambda(lambda text: {"text": text})

# 2. Structured prompt template
PROMPT_TEMPLATE = ChatPromptTemplate.from_template("""
Analyse cette phrase : "{text}"
...
""")

# 3. Output parser
json_parser = JsonOutputParser()

# 4. LCEL chain composition
chain = prep_for_template | PROMPT_TEMPLATE | llm | json_parser

# 5. Parallel runnables
parallel_chain = RunnableParallel(
    main_analysis=chain,
    metadata=prep_for_template | RunnableLambda(lambda data: {
        "length": len(data["text"]),
        "word_count": len(data["text"].split()),
        "has_punctuation": any(c in data["text"] for c in "!?.")
    })
)
```

## Why This Pattern?

### 1. prep_for_template
Transforms raw input into a dictionary format that templates expect:
```python
"Hello" → {"text": "Hello"}
```

### 2. Pipe Operator (|)
Chains components together in sequence:
```python
input | step1 | step2 | step3 | output
```

### 3. RunnableParallel
Executes multiple branches concurrently:
```python
         input
         /   \
    branch1  branch2
         \   /
       combined
```

## Example Execution Flow

### Input
```python
text = "Je suis très satisfait de cette collaboration."
```

### Execution
```python
parallel_result = parallel_chain.invoke(text)
```

### Processing
```
text
├─→ main_analysis branch
│   ├─→ prep_for_template: {"text": "Je suis très satisfait..."}
│   ├─→ PROMPT_TEMPLATE: formatted prompt
│   ├─→ LLM: model inference
│   └─→ json_parser: parsed JSON
│
└─→ metadata branch
    ├─→ prep_for_template: {"text": "Je suis très satisfait..."}
    └─→ RunnableLambda: {"length": 47, "word_count": 7, "has_punctuation": true}
```

### Output
```python
{
    "main_analysis": {
        "sentiment": "POSITIF",
        "sujet_principal": "Collaboration",
        "question_suivi": "Quels sont les bénéfices...",
        "explication": "La phrase exprime..."
    },
    "metadata": {
        "length": 47,
        "word_count": 7,
        "has_punctuation": true
    }
}
```

## Benefits of This Pattern

1. **Composability**: Easy to add more steps
   ```python
   new_step = RunnableLambda(lambda x: process(x))
   chain = prep | template | llm | parser | new_step
   ```

2. **Parallel Processing**: Add more branches
   ```python
   parallel_chain = RunnableParallel(
       analysis=chain,
       metadata=metadata_branch,
       summary=summary_branch,  # New!
       stats=stats_branch       # New!
   )
   ```

3. **Type Safety**: Templates validate inputs
   ```python
   ChatPromptTemplate.from_template("{text}")
   # Ensures "text" key exists in input dict
   ```

4. **Error Handling**: Each component handles errors
   ```python
   try:
       result = chain.invoke(text)
   except OutputParserException as e:
       # JsonOutputParser failed to parse
   ```

## Comparison: Old vs New

### Old Way (Custom Chain)
```python
class SimpleChain:
    def run(self, text):
        prompt = self.prompt_template.replace("{text}", text)
        response = self.llm.invoke(prompt)
        return response.content
```

### New Way (Notebook 24)
```python
prep_for_template = RunnableLambda(lambda text: {"text": text})
chain = prep_for_template | PROMPT_TEMPLATE | llm | json_parser
```

## Testing the Pattern

```python
# Test prep_for_template
result = prep_for_template.invoke("test")
assert result == {"text": "test"}

# Test chain composition
test_chain = prep_for_template | ChatPromptTemplate.from_template("{text}")
# Chain is composable and type-safe

# Test parallel execution
parallel = RunnableParallel(
    branch1=chain,
    branch2=metadata
)
results = parallel.invoke("input")
# Both branches execute concurrently
```

## Advanced Usage

### Adding More Parallel Tasks
```python
parallel_chain = RunnableParallel(
    analysis=main_chain,
    metadata=metadata_chain,
    translation=prep_for_template | translation_llm,
    summary=prep_for_template | summary_llm,
    keywords=prep_for_template | keyword_extractor
)
```

### Conditional Branching
```python
from langchain_core.runnables import RunnableBranch

conditional = RunnableBranch(
    (lambda x: len(x["text"]) < 50, short_text_chain),
    (lambda x: len(x["text"]) < 200, medium_text_chain),
    long_text_chain  # default
)

chain = prep_for_template | conditional
```

## Resources

- [LangChain LCEL Documentation](https://python.langchain.com/docs/expression_language/)
- [Runnables Guide](https://python.langchain.com/docs/expression_language/primitives/runnables)
- [Output Parsers](https://python.langchain.com/docs/modules/model_io/output_parsers/)
- [Parallel Execution](https://python.langchain.com/docs/expression_language/how_to/map)
