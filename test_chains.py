#!/usr/bin/env python3
"""
Test script to verify the Runnables and Parallel Runnables implementation
"""
import sys

def test_imports():
    """Test that all required modules can be imported"""
    print("Testing imports...")
    try:
        from langchain_core.runnables import RunnableLambda, RunnableParallel
        print("✓ RunnableLambda and RunnableParallel imported successfully")
        
        from langchain_core.prompts import ChatPromptTemplate
        print("✓ ChatPromptTemplate imported successfully")
        
        from langchain_core.output_parsers import JsonOutputParser
        print("✓ JsonOutputParser imported successfully")
        
        return True
    except ImportError as e:
        print(f"✗ Import error: {e}")
        return False

def test_chain_structure():
    """Test that the chain structure can be created"""
    print("\nTesting chain structure...")
    try:
        from langchain_core.runnables import RunnableLambda, RunnableParallel
        from langchain_core.prompts import ChatPromptTemplate
        from langchain_core.output_parsers import JsonOutputParser
        
        # Create prep_for_template
        prep_for_template = RunnableLambda(lambda text: {"text": text})
        print("✓ prep_for_template created successfully")
        
        # Test the lambda function
        result = prep_for_template.invoke("test text")
        assert result == {"text": "test text"}, "prep_for_template output mismatch"
        print("✓ prep_for_template works correctly")
        
        # Create prompt template
        PROMPT_TEMPLATE = ChatPromptTemplate.from_template("""
        Analyse cette phrase : "{text}"
        
        Réponds UNIQUEMENT en JSON.
        """)
        print("✓ ChatPromptTemplate created successfully")
        
        # Create JSON parser
        json_parser = JsonOutputParser()
        print("✓ JsonOutputParser created successfully")
        
        # Test metadata lambda with consistent input format
        metadata_lambda = prep_for_template | RunnableLambda(lambda data: {
            "length": len(data["text"]),
            "word_count": len(data["text"].split()),
            "has_punctuation": any(c in data["text"] for c in "!?.")
        })
        metadata_result = metadata_lambda.invoke("Hello world!")
        assert metadata_result["length"] == 12, "Metadata length mismatch"
        assert metadata_result["word_count"] == 2, "Metadata word_count mismatch"
        assert metadata_result["has_punctuation"] == True, "Metadata punctuation mismatch"
        print("✓ Metadata lambda with consistent input format works correctly")
        
        return True
    except Exception as e:
        print(f"✗ Chain structure error: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("=" * 60)
    print("Testing Runnables and Parallel Runnables Implementation")
    print("=" * 60)
    
    success = True
    
    if not test_imports():
        success = False
        print("\n⚠️  Please install required packages:")
        print("pip install langchain langchain-core")
    
    if success:
        if not test_chain_structure():
            success = False
    
    print("\n" + "=" * 60)
    if success:
        print("✅ All tests passed!")
    else:
        print("❌ Some tests failed")
    print("=" * 60)
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
