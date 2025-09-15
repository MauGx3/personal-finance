#!/usr/bin/env python
"""
Test script for Banco Inter import functionality.

This script demonstrates the import functionality by parsing sample files
and testing the core components.
"""

import os
import sys
from pathlib import Path
from decimal import Decimal

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Set Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.local')

try:
    import django
    django.setup()
    
    # Import our modules after Django setup
    from django.contrib.auth import get_user_model
    from personal_finance.data_sources.importers import (
        BancoInterMonthlyReportParser,
        BancoInterBrokerageNoteParser,
        BancoInterExtractParser,
        BancoInterImportService
    )
    from personal_finance.data_sources.models import DocumentImport
    
    User = get_user_model()
    
    def test_parsers():
        """Test the individual parsers with sample files."""
        print("🧪 Testing Banco Inter Import Parsers")
        print("=" * 50)
        
        # Create test user
        try:
            user = User.objects.get(username='test_import_user')
        except User.DoesNotExist:
            user = User.objects.create_user(
                username='test_import_user',
                email='test@example.com',
                password='testpass123'
            )
        
        # Test Monthly Report Parser
        print("\n📊 Testing Monthly Report Parser")
        monthly_file = '/tmp/sample_monthly_report.csv'
        if Path(monthly_file).exists():
            parser = BancoInterMonthlyReportParser(monthly_file, user)
            
            print(f"   ✓ Format validation: {parser.validate_format()}")
            
            # Test decimal parsing
            test_values = ['R$ 1.234,56', '1.234,56', '(123,45)', '']
            for value in test_values:
                parsed = parser._parse_decimal(value)
                print(f"   ✓ '{value}' → {parsed}")
            
            # Parse the file
            try:
                parsed_data = parser.parse()
                print(f"   ✓ Parsed {len(parsed_data.get('positions', []))} positions")
                
                for i, pos in enumerate(parsed_data.get('positions', [])[:3]):
                    print(f"     Position {i+1}: {pos['symbol']} - {pos['quantity']} shares - R$ {pos['value']}")
            except Exception as e:
                print(f"   ❌ Parse error: {e}")
        else:
            print(f"   ⚠️  Sample file not found: {monthly_file}")
        
        # Test Brokerage Note Parser
        print("\n📋 Testing Brokerage Note Parser")
        brokerage_file = '/tmp/sample_brokerage_note.csv'
        if Path(brokerage_file).exists():
            parser = BancoInterBrokerageNoteParser(brokerage_file, user)
            
            print(f"   ✓ Format validation: {parser.validate_format()}")
            
            try:
                parsed_data = parser.parse()
                print(f"   ✓ Parsed {len(parsed_data.get('transactions', []))} transactions")
                
                for i, tx in enumerate(parsed_data.get('transactions', [])[:3]):
                    print(f"     Transaction {i+1}: {tx['symbol']} - {tx['transaction_type']} - {tx['quantity']} @ R$ {tx['price']}")
            except Exception as e:
                print(f"   ❌ Parse error: {e}")
        else:
            print(f"   ⚠️  Sample file not found: {brokerage_file}")
        
        # Test Extract Parser  
        print("\n🏦 Testing Extract Parser")
        extract_file = '/tmp/sample_extract.csv'
        if Path(extract_file).exists():
            parser = BancoInterExtractParser(extract_file, user)
            
            print(f"   ✓ Format validation: {parser.validate_format()}")
            
            try:
                parsed_data = parser.parse()
                print(f"   ✓ Parsed {len(parsed_data.get('transactions', []))} transactions")
                
                for i, tx in enumerate(parsed_data.get('transactions', [])[:3]):
                    print(f"     Transaction {i+1}: {tx['description']} - R$ {tx['amount']}")
            except Exception as e:
                print(f"   ❌ Parse error: {e}")
        else:
            print(f"   ⚠️  Sample file not found: {extract_file}")
    
    def test_import_service():
        """Test the full import service."""
        print("\n🔧 Testing Import Service")
        print("=" * 50)
        
        # Create test user
        try:
            user = User.objects.get(username='test_import_user')
        except User.DoesNotExist:
            user = User.objects.create_user(
                username='test_import_user',
                email='test@example.com',
                password='testpass123'
            )
        
        import_service = BancoInterImportService()
        
        # Test monthly report import
        monthly_file = '/tmp/sample_monthly_report.csv'
        if Path(monthly_file).exists():
            try:
                print(f"\n📊 Importing monthly report: {monthly_file}")
                import_record = import_service.import_document(
                    file_path=monthly_file,
                    document_type='BANCO_INTER_MONTHLY_REPORT',
                    user=user
                )
                
                print(f"   ✓ Import Status: {import_record.status}")
                print(f"   ✓ Imported Transactions: {import_record.imported_transactions_count}")
                print(f"   ✓ Document Type: {import_record.get_document_type_display()}")
                
            except Exception as e:
                print(f"   ❌ Import failed: {e}")
        
        # Show import statistics
        total_imports = DocumentImport.objects.filter(user=user).count()
        completed_imports = DocumentImport.objects.filter(user=user, status='COMPLETED').count()
        failed_imports = DocumentImport.objects.filter(user=user, status='FAILED').count()
        
        print(f"\n📈 Import Statistics for {user.username}:")
        print(f"   Total Imports: {total_imports}")
        print(f"   Completed: {completed_imports}")
        print(f"   Failed: {failed_imports}")
    
    def test_models():
        """Test the database models."""
        print("\n💾 Testing Database Models")
        print("=" * 50)
        
        # Test DocumentImport model
        print("\n📄 Testing DocumentImport model")
        
        # Get all document types
        doc_types = DocumentImport.DOCUMENT_TYPES
        print(f"   ✓ Supported document types: {len(doc_types)}")
        
        for code, name in doc_types:
            print(f"     - {code}: {name}")
        
        # Test model creation
        try:
            user = User.objects.get(username='test_import_user')
        except User.DoesNotExist:
            user = User.objects.create_user(
                username='test_import_user',
                email='test@example.com',
                password='testpass123'
            )
        
        doc_import = DocumentImport.objects.create(
            user=user,
            document_type='BANCO_INTER_MONTHLY_REPORT',
            original_filename='test_file.csv',
            file_path='/tmp/test_file.csv',
            status='PENDING'
        )
        
        print(f"   ✓ Created DocumentImport: {doc_import}")
        print(f"     - ID: {doc_import.id}")
        print(f"     - Status: {doc_import.get_status_display()}")
        print(f"     - Document Type: {doc_import.get_document_type_display()}")
    
    if __name__ == '__main__':
        print("🚀 Banco Inter Import Functionality Test")
        print("=" * 60)
        
        test_models()
        test_parsers()
        test_import_service()
        
        print("\n✅ Test completed!")
        print("\nNext steps:")
        print("1. Start the Django development server: python manage.py runserver")
        print("2. Test the API endpoints using the documentation in BANCO_INTER_IMPORT.md")
        print("3. Upload sample files via the API or Django admin interface")

except ImportError as e:
    print(f"❌ Django setup failed: {e}")
    print("Make sure you have Django installed and the project dependencies available.")
except Exception as e:
    print(f"❌ Test failed: {e}")
    import traceback
    traceback.print_exc()