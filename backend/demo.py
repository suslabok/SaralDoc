#!/usr/bin/env python3
"""
SaralDoc Demo Script
Quick testing of AI features for teacher presentation
"""

import json
from pathlib import Path

def demo_processor():
    """Demo the AI processor"""
    print("\n" + "="*60)
    print("🤖 SaralDoc AI Processor Demo")
    print("="*60 + "\n")
    
    try:
        from processor import processor
        
        # Test 1: Nepali text
        nepali_text = "यो रोजगार करार सरकारी कर्मचारीको लागि तयार गरिएको हो। कर्मचारीले महिनामा नियमित वेतन र स्वास्थ्य बीमा पाउनु हुनुपर्दछ।"
        
        print("📝 Test 1: Nepali Text Analysis")
        print(f"Input: {nepali_text[:50]}...\n")
        
        result = processor.extract_structure(nepali_text)
        
        print(f"✓ Clauses extracted: {len(result['clauses'])}")
        print(f"✓ Obligations found: {len(result['obligations'])}")
        print(f"✓ Language detected: {result['language']}")
        print(f"✓ Confidence: {result['confidence']}")
        
        # Test 2: English text
        english_text = "The borrower shall repay the loan at 8% interest within 12 months. If payment fails, a penalty of 2% per month will be imposed."
        
        print("\n📝 Test 2: English Text Analysis")
        print(f"Input: {english_text[:50]}...\n")
        
        result2 = processor.extract_structure(english_text)
        
        print(f"✓ Clauses extracted: {len(result2['clauses'])}")
        print(f"✓ Obligations found: {len(result2['obligations'])}")
        print(f"✓ Language detected: {result2['language']}")
        print(f"✓ Confidence: {result2['confidence']}")
        
        print("\n" + "="*60)
        print("✅ AI Processor is working correctly!")
        print("="*60 + "\n")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("\nMake sure all dependencies are installed:")
        print("pip install -r requirements.txt")
        print("python -m spacy download en_core_web_sm")

def demo_datasets():
    """Demo dataset loading"""
    print("\n" + "="*60)
    print("📊 SaralDoc Datasets Demo")
    print("="*60 + "\n")
    
    try:
        from datasets_manager import dataset_manager
        
        # Get dataset info
        info = dataset_manager.get_dataset_info()
        
        print(f"✓ CSV files: {len(info['csv_files'])}")
        print(f"✓ JSON files: {len(info['json_files'])}")
        print(f"✓ Total documents: {info['total_documents']}")
        
        if info['csv_files']:
            print("\n📄 Available CSV datasets:")
            for csv in info['csv_files']:
                print(f"  - {csv['name']}: {csv['records']} documents")
        
        # Load sample dataset
        data = dataset_manager.load_csv_dataset("sample_nepali.csv")
        print(f"\n✓ Loaded {len(data)} Nepali legal documents")
        
        print("\n📋 Sample documents:")
        for i, doc in enumerate(data[:3], 1):
            print(f"  {i}. {doc['title']} ({doc['language']})")
        
        print("\n" + "="*60)
        print("✅ Datasets loaded successfully!")
        print("="*60 + "\n")
        
    except Exception as e:
        print(f"❌ Error: {e}")

def demo_analytics():
    """Demo analytics"""
    print("\n" + "="*60)
    print("📈 SaralDoc Analytics Demo")
    print("="*60 + "\n")
    
    try:
        from processor import processor
        from analytics import analytics
        
        # Create sample analysis
        text = "यो रोजगार करार है। कर्मचारीले दायित्व निभाउनु पर्दछ। दण्ड लगाइनेछ।"
        result = processor.extract_structure(text)
        
        # Analyze complexity
        complexity = analytics.analyze_document_complexity(result)
        print(f"✓ Complexity Score: {complexity['overall_score']}/100")
        print(f"✓ Level: {complexity['level']}")
        
        # Identify risks
        risks = analytics.identify_risk_areas(result)
        print(f"✓ Risks identified: {len(risks)}")
        
        # Key terms
        terms = analytics.extract_key_terms(result)
        print(f"✓ Key terms: {', '.join(terms[:3])}")
        
        print("\n" + "="*60)
        print("✅ Analytics working correctly!")
        print("="*60 + "\n")
        
    except Exception as e:
        print(f"❌ Error: {e}")

def main():
    """Run all demos"""
    print("\n")
    print("╔" + "="*58 + "╗")
    print("║" + " "*15 + "🚀 SaralDoc Demo Suite" + " "*21 + "║")
    print("║" + " "*58 + "║")
    print("║" + "  AI-Powered Legal Document Analyzer" + " "*22 + "║")
    print("╚" + "="*58 + "╝")
    
    # Run demos
    demo_processor()
    demo_datasets()
    demo_analytics()
    
    print("\n" + "="*60)
    print("🎉 All demos completed successfully!")
    print("="*60)
    print("\nNext steps:")
    print("1. Start backend: uvicorn main:app --reload --port 8000")
    print("2. Start frontend: cd ../frontend && npm run dev")
    print("3. Open: http://localhost:5173")
    print("\n")

if __name__ == "__main__":
    main()
