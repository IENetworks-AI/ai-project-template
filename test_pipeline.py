#!/usr/bin/env python3
"""
Test script for Retail Sales Insight Pipeline
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from pipelines.data_pipeline import run_data_pipeline, get_sales_insights
from src.utils.logging import get_logger

logger = get_logger('test_pipeline')

def test_pipeline():
    """Test the complete Retail Sales Insight pipeline"""
    print("🧪 Testing Retail Sales Insight Pipeline...")
    print("=" * 50)
    
    try:
        # Test the main pipeline
        success = run_data_pipeline()
        
        if success:
            print("✅ Pipeline completed successfully!")
            
            # Test getting insights
            insights = get_sales_insights()
            if insights:
                print("✅ Sales insights retrieved successfully!")
                print(f"📊 Found {insights.get('categories_above_threshold', 0)} categories above threshold")
            else:
                print("⚠️  No sales insights available")
            
            print("\n📊 Next steps:")
            print("1. Check data/processed/ for output files")
            print("2. Start API: python api/app.py")
            print("3. Test API endpoints")
        else:
            print("❌ Pipeline failed!")
            return False
            
    except Exception as e:
        print(f"❌ Error during pipeline test: {e}")
        return False
    
    return True

if __name__ == "__main__":
    test_pipeline() 