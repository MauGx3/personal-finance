"""Tests for Banco Inter import functionality."""

import tempfile
from decimal import Decimal
from pathlib import Path

from django.contrib.auth import get_user_model
from django.test import TestCase

from personal_finance.assets.models import Asset
from personal_finance.portfolios.models import Portfolio
from ..importers import BancoInterImportService, BancoInterMonthlyReportParser
from ..models import DocumentImport

User = get_user_model()


class BancoInterImportTestCase(TestCase):
    """Test cases for Banco Inter import functionality."""
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass'
        )
        self.import_service = BancoInterImportService()
    
    def test_document_import_model_creation(self):
        """Test creating a DocumentImport record."""
        doc_import = DocumentImport.objects.create(
            user=self.user,
            document_type='BANCO_INTER_MONTHLY_REPORT',
            original_filename='test_report.csv',
            file_path='/tmp/test_report.csv',
            status='PENDING'
        )
        
        self.assertEqual(doc_import.user, self.user)
        self.assertEqual(doc_import.document_type, 'BANCO_INTER_MONTHLY_REPORT')
        self.assertEqual(doc_import.status, 'PENDING')
        self.assertEqual(str(doc_import), 
                        'Banco Inter - Relatório Mensal de Investimentos - test_report.csv (PENDING)')
    
    def test_monthly_report_parser_decimal_parsing(self):
        """Test decimal parsing for Brazilian number format."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write('Ativo,Posição,Valor\n')
            f.write('PETR4,100,"R$ 1.234,56"\n')
            temp_path = f.name
        
        try:
            parser = BancoInterMonthlyReportParser(temp_path, self.user)
            
            # Test decimal parsing
            self.assertEqual(parser._parse_decimal('R$ 1.234,56'), Decimal('1234.56'))
            self.assertEqual(parser._parse_decimal('1.234,56'), Decimal('1234.56'))
            self.assertEqual(parser._parse_decimal('(123,45)'), Decimal('-123.45'))
            self.assertEqual(parser._parse_decimal(''), Decimal('0'))
            
        finally:
            Path(temp_path).unlink()
    
    def test_document_types_choices(self):
        """Test that all document types are properly defined."""
        choices = dict(DocumentImport.DOCUMENT_TYPES)
        
        self.assertIn('BANCO_INTER_MONTHLY_REPORT', choices)
        self.assertIn('BANCO_INTER_BROKERAGE_NOTE', choices)
        self.assertIn('BANCO_INTER_EXTRACT', choices)
        
        self.assertEqual(choices['BANCO_INTER_MONTHLY_REPORT'], 
                        'Banco Inter - Relatório Mensal de Investimentos')
        self.assertEqual(choices['BANCO_INTER_BROKERAGE_NOTE'], 
                        'Banco Inter - Nota de Corretagem')
        self.assertEqual(choices['BANCO_INTER_EXTRACT'], 
                        'Banco Inter - Extrato')