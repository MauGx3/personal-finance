import io
from datetime import date
from decimal import Decimal

import pytest
from django.core.management import call_command
from openpyxl import Workbook

from apps.assets.models import Asset, AssetClass
from apps.importers.base import StatementError
from apps.importers.models import ImportBatch
from apps.importers.services import import_statement, undo_import
from apps.portfolios.models import Holding, Transaction

pytestmark = pytest.mark.django_db

NEGOCIACAO = [
    ["Data do Negócio", "Tipo de Movimentação", "Mercado", "Prazo/Vencimento", "Instituição",
     "Código de Negociação", "Quantidade", "Preço", "Valor"],
    ["15/03/2024", "Compra", "Mercado à Vista", "-", "INTER DTVM LTDA", "PETR4", 100, 25.5, 2550],
    ["15/03/2024", "Compra", "Mercado Fracionário", "-", "INTER DTVM LTDA", "PETR4F", 5, 25.6, 128],
    ["15/03/2024", "Compra", "Mercado Fracionário", "-", "INTER DTVM LTDA", "PETR4F", 5, 25.6, 128],
    ["20/03/2024", "Venda", "Mercado à Vista", "-", "INTER DTVM LTDA", "PETR4", 50, 30, 1500],
    ["21/03/2024", "Compra", "Mercado à Vista", "-", "INTER DTVM LTDA", "HGLG11", 10, 160.1, 1601],
    ["22/03/2024", "Compra", "Opção de Compra", "19/04/2024", "INTER DTVM LTDA", "PETRD30", 100, 1, 100],
]  # fmt: skip

MOVIMENTACAO = [
    ["Entrada/Saída", "Data", "Movimentação", "Produto", "Instituição", "Quantidade",
     "Preço unitário", "Valor da Operação"],
    ["Credito", "02/04/2024", "Dividendo", "PETR4 - PETROLEO BRASILEIRO S.A.", "INTER", 55, 0.5, 27.5],
    ["Credito", "02/04/2024", "Juros Sobre Capital Próprio", "PETR4 - PETROLEO BRASILEIRO S.A.",
     "INTER", 55, 0.2, 9.35],
    ["Credito", "15/04/2024", "Rendimento", "HGLG11 - CSHG LOGISTICA FII", "INTER", 10, 1.1, 11],
    ["Credito", "15/03/2024", "Transferência - Liquidação", "PETR4 - PETROLEO", "INTER", 100, 25.5, 2550],
    ["Debito", "20/03/2024", "Transferência - Liquidação", "PETR4 - PETROLEO", "INTER", 50, 30, 1500],
    ["Credito", "16/04/2024", "Rendimento", "XPML11 - XP MALLS FII", "INTER", 3, "-", "-"],
]  # fmt: skip


def xlsx(rows) -> io.BytesIO:
    workbook = Workbook()
    for row in rows:
        workbook.active.append(row)
    buffer = io.BytesIO()
    workbook.save(buffer)
    buffer.seek(0)
    return buffer


def csv_file(text: str, encoding="utf-8") -> io.BytesIO:
    return io.BytesIO(text.encode(encoding))


def test_b3_negociacao_xlsx_import(portfolio):
    outcome = import_statement(portfolio, xlsx(NEGOCIACAO), "negociacao-2024.xlsx")

    assert outcome.parser.name == "b3_negociacao"
    assert (outcome.created, outcome.skipped) == (5, 0)
    assert outcome.new_assets == ["HGLG11", "PETR4"]
    assert any("PETRD30" in warning for warning in outcome.warnings)

    holding = Holding.objects.get(portfolio=portfolio, asset__ticker="PETR4")
    assert holding.quantity == 60  # 100 + 5 + 5 fractional - 50
    assert holding.ledger_error == ""
    assert Asset.objects.get(ticker="HGLG11").asset_class == AssetClass.FII
    assert not Asset.objects.filter(ticker__startswith="PETR4F").exists()
    first = Transaction.objects.filter(asset__ticker="PETR4").earliest("trade_date", "id")
    assert (first.trade_date, first.price, first.currency, first.broker) == (
        date(2024, 3, 15), Decimal("25.5"), "BRL", "INTER DTVM LTDA",
    )  # fmt: skip


def test_reimporting_the_same_file_creates_nothing(portfolio):
    import_statement(portfolio, xlsx(NEGOCIACAO), "a.xlsx")
    again = import_statement(portfolio, xlsx(NEGOCIACAO), "a-again.xlsx")
    assert (again.created, again.skipped) == (0, 5)
    assert Transaction.objects.count() == 5
    assert ImportBatch.objects.count() == 1


def test_dry_run_writes_nothing(portfolio):
    outcome = import_statement(portfolio, xlsx(NEGOCIACAO), "a.xlsx", dry_run=True)
    assert outcome.created == 5 and outcome.batch is None
    assert not Transaction.objects.exists() and not Asset.objects.exists()


def test_b3_movimentacao_imports_only_cash_income(portfolio):
    outcome = import_statement(portfolio, xlsx(MOVIMENTACAO), "movimentacao.xlsx")

    assert outcome.parser.name == "b3_movimentacao"
    assert outcome.created == 3
    kinds = dict(Transaction.objects.values_list("kind", "amount"))
    assert kinds == {
        "DIVIDEND": Decimal("27.50"),
        "JCP": Decimal("9.35"),
        "INCOME": Decimal("11.00"),
    }
    assert Asset.objects.get(ticker="PETR4").name == "PETROLEO BRASILEIRO S.A."
    assert any("Transferência - Liquidação" in w and "2" in w for w in outcome.warnings)
    assert any("XPML11" in w for w in outcome.warnings)


def test_b3_csv_with_brazilian_numbers_and_title_lines(portfolio):
    text = (
        "Extrato de negociação;;;;;;;;\n"
        "Data do Negócio;Tipo de Movimentação;Mercado;Prazo/Vencimento;Instituição;"
        "Código de Negociação;Quantidade;Preço;Valor\n"
        "15/03/2024;Compra;Mercado à Vista;-;XP;VALE3;1.000;R$ 62,35;R$ 62.350,00\n"
        "16/03/2024;Doação;Mercado à Vista;-;XP;VALE3;1;R$ 62,35;R$ 62,35\n"
    )
    outcome = import_statement(portfolio, csv_file(text, "latin-1"), "neg.csv")
    assert outcome.created == 1
    assert any("Line 4" in warning for warning in outcome.warnings)
    transaction = Transaction.objects.get()
    assert (transaction.quantity, transaction.price) == (1000, Decimal("62.35"))


def test_generic_csv_supports_us_assets(portfolio):
    text = (
        "date,type,ticker,quantity,price,fees,amount,currency,exchange,broker\n"
        "2024-01-10,BUY,AAPL,10,150.25,1.00,,USD,NASDAQ,IBKR\n"
        "2024-02-15,DIVIDEND,AAPL,,,,2.40,USD,NASDAQ,IBKR\n"
        "2024-02-16,GIFT,AAPL,1,1,,,USD,NASDAQ,IBKR\n"
    )
    outcome = import_statement(portfolio, csv_file(text), "us.csv")
    assert outcome.parser.name == "generic_csv"
    assert outcome.created == 2
    asset = Asset.objects.get(ticker="AAPL")
    assert (asset.exchange, asset.currency) == ("NASDAQ", "USD")
    holding = Holding.objects.get(asset=asset)
    assert holding.average_price == Decimal("150.35")
    assert holding.income == Decimal("2.40")


def test_unrecognised_and_unsupported_files_are_rejected(portfolio):
    with pytest.raises(StatementError, match="not recognised"):
        import_statement(portfolio, csv_file("a,b\n1,2\n"), "x.csv")
    with pytest.raises(StatementError, match="Unsupported"):
        import_statement(portfolio, io.BytesIO(b"%PDF"), "nota.pdf")
    with pytest.raises(StatementError, match="empty"):
        import_statement(portfolio, io.BytesIO(b""), "x.csv")
    with pytest.raises(StatementError, match="does not look like"):
        import_statement(portfolio, xlsx(MOVIMENTACAO), "m.xlsx", parser_name="b3_negociacao")


def test_undo_import_removes_its_transactions(portfolio, petr4, trade):
    trade(petr4, "BUY", "2024-01-02", 10, 20)
    outcome = import_statement(portfolio, xlsx(NEGOCIACAO), "a.xlsx")
    assert undo_import(outcome.batch) == 5
    assert Transaction.objects.count() == 1
    assert Holding.objects.get(asset=petr4).quantity == 10
    assert not Holding.objects.filter(asset__ticker="HGLG11").exists()


def test_import_statement_command(portfolio, tmp_path, capsys):
    path = tmp_path / "negociacao.xlsx"
    path.write_bytes(xlsx(NEGOCIACAO).getvalue())
    call_command("import_statement", str(path))
    assert "created 5" in capsys.readouterr().out
    assert Transaction.objects.count() == 5
