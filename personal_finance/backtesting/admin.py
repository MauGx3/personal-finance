"""Django admin configuration for backtesting models."""

from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from decimal import Decimal

from .models import (
    Strategy, Backtest, BacktestResult, BacktestPortfolioSnapshot,
    BacktestTrade
)


@admin.register(Strategy)
class StrategyAdmin(admin.ModelAdmin):
    """Admin interface for trading strategies."""
    
    list_display = [
        'name', 'strategy_type', 'user', 'initial_capital',
        'max_position_size', 'asset_count', 'backtest_count', 'is_active', 'created_at'
    ]
    list_filter = ['strategy_type', 'is_active', 'rebalance_frequency', 'created_at']
    search_fields = ['name', 'description', 'user__username']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('user', 'name', 'description', 'strategy_type', 'is_active')
        }),
        ('Portfolio Settings', {
            'fields': ('initial_capital', 'rebalance_frequency')
        }),
        ('Risk Management', {
            'fields': ('max_position_size', 'stop_loss_percentage', 'take_profit_percentage')
        }),
        ('Strategy Parameters', {
            'fields': ('parameters',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    filter_horizontal = ['asset_universe']
    
    def asset_count(self, obj):
        """Display number of assets in strategy universe."""
        count = obj.asset_universe.count()
        return format_html(
            '<span style="color: {};">{}</span>',
            'green' if count > 0 else 'red',
            count
        )
    asset_count.short_description = 'Assets'
    
    def backtest_count(self, obj):
        """Display number of backtests run for this strategy."""
        count = obj.backtests.count()
        if count > 0:
            url = reverse('admin:backtesting_backtest_changelist') + f'?strategy__id__exact={obj.id}'
            return format_html('<a href="{}">{} backtests</a>', url, count)
        return '0 backtests'
    backtest_count.short_description = 'Backtests'


class BacktestTradeInline(admin.TabularInline):
    """Inline admin for backtest trades."""
    model = BacktestTrade
    extra = 0
    readonly_fields = [
        'asset', 'trade_type', 'date', 'quantity', 'price',
        'gross_value', 'transaction_cost', 'slippage_cost', 'reason'
    ]
    fields = readonly_fields
    can_delete = False
    
    def has_add_permission(self, request, obj=None):
        return False


class BacktestPortfolioSnapshotInline(admin.TabularInline):
    """Inline admin for portfolio snapshots."""
    model = BacktestPortfolioSnapshot
    extra = 0
    readonly_fields = [
        'date', 'total_value', 'cash_balance', 'invested_value',
        'cumulative_return', 'daily_return'
    ]
    fields = readonly_fields
    can_delete = False
    
    def has_add_permission(self, request, obj=None):
        return False


@admin.register(Backtest)
class BacktestAdmin(admin.ModelAdmin):
    """Admin interface for backtests."""
    
    list_display = [
        'name', 'strategy_name', 'status', 'duration_display',
        'progress_percentage', 'total_return_display', 'sharpe_ratio_display',
        'execution_time_display', 'created_at'
    ]
    list_filter = ['status', 'created_at', 'start_date', 'end_date']
    search_fields = ['name', 'description', 'strategy__name']
    readonly_fields = [
        'status', 'progress_percentage', 'started_at', 'completed_at',
        'execution_time_display', 'created_at', 'updated_at'
    ]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('strategy', 'name', 'description')
        }),
        ('Time Period', {
            'fields': ('start_date', 'end_date', 'benchmark_asset')
        }),
        ('Execution Parameters', {
            'fields': ('transaction_costs', 'slippage')
        }),
        ('Status', {
            'fields': (
                'status', 'progress_percentage', 'error_message',
                'started_at', 'completed_at', 'execution_time_display'
            )
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    inlines = [BacktestTradeInline, BacktestPortfolioSnapshotInline]
    
    def strategy_name(self, obj):
        """Display strategy name with link."""
        url = reverse('admin:backtesting_strategy_change', args=[obj.strategy.id])
        return format_html('<a href="{}">{}</a>', url, obj.strategy.name)
    strategy_name.short_description = 'Strategy'
    
    def duration_display(self, obj):
        """Display backtest duration in a readable format."""
        days = obj.duration_days
        if days < 30:
            return f"{days} days"
        elif days < 365:
            months = days // 30
            return f"{months} months"
        else:
            years = days // 365
            months = (days % 365) // 30
            return f"{years}y {months}m"
    duration_display.short_description = 'Duration'
    
    def total_return_display(self, obj):
        """Display total return with color coding."""
        try:
            result = obj.result
            total_return = float(result.total_return)
            color = 'green' if total_return >= 0 else 'red'
            return format_html(
                '<span style="color: {}; font-weight: bold;">{:.2f}%</span>',
                color, total_return
            )
        except:
            return '-'
    total_return_display.short_description = 'Total Return'
    
    def sharpe_ratio_display(self, obj):
        """Display Sharpe ratio with color coding."""
        try:
            result = obj.result
            if result.sharpe_ratio:
                sharpe = float(result.sharpe_ratio)
                if sharpe >= 2.0:
                    color = 'darkgreen'
                elif sharpe >= 1.0:
                    color = 'green'
                elif sharpe >= 0.5:
                    color = 'orange'
                else:
                    color = 'red'
                return format_html(
                    '<span style="color: {}; font-weight: bold;">{:.2f}</span>',
                    color, sharpe
                )
        except:
            pass
        return '-'
    sharpe_ratio_display.short_description = 'Sharpe Ratio'
    
    def execution_time_display(self, obj):
        """Display execution time in readable format."""
        exec_time = obj.execution_time
        if exec_time:
            if exec_time < 60:
                return f"{exec_time:.1f}s"
            elif exec_time < 3600:
                return f"{exec_time/60:.1f}m"
            else:
                return f"{exec_time/3600:.1f}h"
        return '-'
    execution_time_display.short_description = 'Execution Time'


@admin.register(BacktestResult)
class BacktestResultAdmin(admin.ModelAdmin):
    """Admin interface for backtest results."""
    
    list_display = [
        'backtest_name', 'total_return_display', 'annualized_return_display',
        'volatility_display', 'sharpe_ratio_display', 'max_drawdown_display',
        'total_trades', 'win_rate_display'
    ]
    list_filter = ['created_at']
    search_fields = ['backtest__name', 'backtest__strategy__name']
    readonly_fields = [
        'backtest', 'total_return', 'annualized_return', 'volatility',
        'sharpe_ratio', 'max_drawdown', 'var_95', 'calmar_ratio',
        'total_trades', 'winning_trades', 'losing_trades', 'win_rate',
        'average_win', 'average_loss', 'benchmark_return', 'alpha', 'beta',
        'information_ratio', 'final_portfolio_value', 'cash_balance',
        'total_transaction_costs', 'profit_factor_display', 'expectancy_display',
        'created_at', 'updated_at'
    ]
    
    fieldsets = (
        ('Backtest Information', {
            'fields': ('backtest',)
        }),
        ('Performance Metrics', {
            'fields': (
                'total_return', 'annualized_return', 'volatility', 'sharpe_ratio'
            )
        }),
        ('Risk Metrics', {
            'fields': ('max_drawdown', 'var_95', 'calmar_ratio')
        }),
        ('Trading Statistics', {
            'fields': (
                'total_trades', 'winning_trades', 'losing_trades', 'win_rate',
                'average_win', 'average_loss', 'profit_factor_display', 'expectancy_display'
            )
        }),
        ('Benchmark Comparison', {
            'fields': ('benchmark_return', 'alpha', 'beta', 'information_ratio'),
            'classes': ('collapse',)
        }),
        ('Portfolio Statistics', {
            'fields': (
                'final_portfolio_value', 'cash_balance', 'total_transaction_costs'
            ),
            'classes': ('collapse',)
        }),
        ('Detailed Data', {
            'fields': ('daily_returns', 'portfolio_values', 'trade_history'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def backtest_name(self, obj):
        """Display backtest name with link."""
        url = reverse('admin:backtesting_backtest_change', args=[obj.backtest.id])
        return format_html('<a href="{}">{}</a>', url, obj.backtest.name)
    backtest_name.short_description = 'Backtest'
    
    def total_return_display(self, obj):
        """Display total return with color coding."""
        total_return = float(obj.total_return)
        color = 'green' if total_return >= 0 else 'red'
        return format_html(
            '<span style="color: {}; font-weight: bold;">{:.2f}%</span>',
            color, total_return
        )
    total_return_display.short_description = 'Total Return'
    
    def annualized_return_display(self, obj):
        """Display annualized return with color coding."""
        ann_return = float(obj.annualized_return)
        color = 'green' if ann_return >= 0 else 'red'
        return format_html(
            '<span style="color: {};">{:.2f}%</span>',
            color, ann_return
        )
    annualized_return_display.short_description = 'Annualized Return'
    
    def volatility_display(self, obj):
        """Display volatility with appropriate formatting."""
        vol = float(obj.volatility)
        if vol < 10:
            color = 'green'
        elif vol < 20:
            color = 'orange'
        else:
            color = 'red'
        return format_html(
            '<span style="color: {};">{:.2f}%</span>',
            color, vol
        )
    volatility_display.short_description = 'Volatility'
    
    def sharpe_ratio_display(self, obj):
        """Display Sharpe ratio with color coding."""
        if obj.sharpe_ratio:
            sharpe = float(obj.sharpe_ratio)
            if sharpe >= 2.0:
                color = 'darkgreen'
            elif sharpe >= 1.0:
                color = 'green'
            elif sharpe >= 0.5:
                color = 'orange'
            else:
                color = 'red'
            return format_html(
                '<span style="color: {}; font-weight: bold;">{:.2f}</span>',
                color, sharpe
            )
        return '-'
    sharpe_ratio_display.short_description = 'Sharpe Ratio'
    
    def max_drawdown_display(self, obj):
        """Display max drawdown with color coding."""
        dd = float(obj.max_drawdown)
        if dd < 5:
            color = 'green'
        elif dd < 15:
            color = 'orange'
        else:
            color = 'red'
        return format_html(
            '<span style="color: {};">{:.2f}%</span>',
            color, dd
        )
    max_drawdown_display.short_description = 'Max Drawdown'
    
    def win_rate_display(self, obj):
        """Display win rate with color coding."""
        if obj.win_rate is not None:
            rate = float(obj.win_rate) * 100
            if rate >= 60:
                color = 'green'
            elif rate >= 40:
                color = 'orange'
            else:
                color = 'red'
            return format_html(
                '<span style="color: {};">{:.1f}%</span>',
                color, rate
            )
        return '-'
    win_rate_display.short_description = 'Win Rate'
    
    def profit_factor_display(self, obj):
        """Display calculated profit factor."""
        pf = obj.profit_factor
        if pf:
            pf_val = float(pf)
            if pf_val >= 2.0:
                color = 'green'
            elif pf_val >= 1.2:
                color = 'orange'
            else:
                color = 'red'
            return format_html(
                '<span style="color: {};">{:.2f}</span>',
                color, pf_val
            )
        return '-'
    profit_factor_display.short_description = 'Profit Factor'
    
    def expectancy_display(self, obj):
        """Display calculated expectancy."""
        exp = obj.expectancy
        if exp:
            exp_val = float(exp)
            color = 'green' if exp_val > 0 else 'red'
            return format_html(
                '<span style="color: {};">{:.2f}%</span>',
                color, exp_val
            )
        return '-'
    expectancy_display.short_description = 'Expectancy'


@admin.register(BacktestPortfolioSnapshot)
class BacktestPortfolioSnapshotAdmin(admin.ModelAdmin):
    """Admin interface for portfolio snapshots."""
    
    list_display = [
        'backtest_name', 'date', 'total_value_display', 'cash_percentage_display',
        'invested_percentage_display', 'daily_return_display', 'cumulative_return_display'
    ]
    list_filter = ['backtest', 'date']
    search_fields = ['backtest__name']
    readonly_fields = [
        'backtest', 'date', 'total_value', 'cash_balance', 'invested_value',
        'daily_return', 'cumulative_return', 'positions', 'benchmark_value',
        'benchmark_return', 'cash_percentage_display', 'invested_percentage_display'
    ]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('backtest', 'date')
        }),
        ('Portfolio Values', {
            'fields': (
                'total_value', 'cash_balance', 'invested_value',
                'cash_percentage_display', 'invested_percentage_display'
            )
        }),
        ('Performance', {
            'fields': ('daily_return', 'cumulative_return')
        }),
        ('Benchmark', {
            'fields': ('benchmark_value', 'benchmark_return'),
            'classes': ('collapse',)
        }),
        ('Positions', {
            'fields': ('positions',),
            'classes': ('collapse',)
        })
    )
    
    def backtest_name(self, obj):
        """Display backtest name with link."""
        url = reverse('admin:backtesting_backtest_change', args=[obj.backtest.id])
        return format_html('<a href="{}">{}</a>', url, obj.backtest.name)
    backtest_name.short_description = 'Backtest'
    
    def total_value_display(self, obj):
        """Display total value with formatting."""
        return f"${obj.total_value:,.2f}"
    total_value_display.short_description = 'Total Value'
    
    def cash_percentage_display(self, obj):
        """Display cash percentage."""
        pct = float(obj.cash_percentage)
        color = 'orange' if pct > 20 else 'black'
        return format_html(
            '<span style="color: {};">{:.1f}%</span>',
            color, pct
        )
    cash_percentage_display.short_description = 'Cash %'
    
    def invested_percentage_display(self, obj):
        """Display invested percentage."""
        pct = float(obj.invested_percentage)
        return f"{pct:.1f}%"
    invested_percentage_display.short_description = 'Invested %'
    
    def daily_return_display(self, obj):
        """Display daily return with color coding."""
        if obj.daily_return:
            ret = float(obj.daily_return)
            color = 'green' if ret >= 0 else 'red'
            return format_html(
                '<span style="color: {};">{:.2f}%</span>',
                color, ret
            )
        return '-'
    daily_return_display.short_description = 'Daily Return'
    
    def cumulative_return_display(self, obj):
        """Display cumulative return with color coding."""
        ret = float(obj.cumulative_return)
        color = 'green' if ret >= 0 else 'red'
        return format_html(
            '<span style="color: {}; font-weight: bold;">{:.2f}%</span>',
            color, ret
        )
    cumulative_return_display.short_description = 'Cumulative Return'


@admin.register(BacktestTrade)
class BacktestTradeAdmin(admin.ModelAdmin):
    """Admin interface for individual trades."""
    
    list_display = [
        'backtest_name', 'date', 'asset_symbol', 'trade_type_display',
        'quantity_display', 'price_display', 'value_display', 'cost_display',
        'reason'
    ]
    list_filter = ['trade_type', 'date', 'backtest']
    search_fields = ['backtest__name', 'asset__symbol', 'reason']
    readonly_fields = [
        'backtest', 'asset', 'trade_type', 'date', 'quantity', 'price',
        'transaction_cost', 'slippage_cost', 'gross_value', 'net_value',
        'signal_strength', 'reason', 'portfolio_value_before',
        'portfolio_value_after', 'position_size_percentage', 'total_cost_display'
    ]
    
    fieldsets = (
        ('Trade Information', {
            'fields': (
                'backtest', 'asset', 'trade_type', 'date', 'reason'
            )
        }),
        ('Trade Details', {
            'fields': (
                'quantity', 'price', 'gross_value', 'net_value', 'signal_strength'
            )
        }),
        ('Costs', {
            'fields': (
                'transaction_cost', 'slippage_cost', 'total_cost_display'
            )
        }),
        ('Portfolio Impact', {
            'fields': (
                'portfolio_value_before', 'portfolio_value_after',
                'position_size_percentage'
            )
        })
    )
    
    def backtest_name(self, obj):
        """Display backtest name with link."""
        url = reverse('admin:backtesting_backtest_change', args=[obj.backtest.id])
        return format_html('<a href="{}">{}</a>', url, obj.backtest.name)
    backtest_name.short_description = 'Backtest'
    
    def asset_symbol(self, obj):
        """Display asset symbol with link."""
        url = reverse('admin:assets_asset_change', args=[obj.asset.id])
        return format_html('<a href="{}">{}</a>', url, obj.asset.symbol)
    asset_symbol.short_description = 'Asset'
    
    def trade_type_display(self, obj):
        """Display trade type with color coding."""
        colors = {
            'buy': 'green',
            'sell': 'red',
            'short': 'orange',
            'cover': 'blue'
        }
        color = colors.get(obj.trade_type, 'black')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color, obj.trade_type.upper()
        )
    trade_type_display.short_description = 'Type'
    
    def quantity_display(self, obj):
        """Display quantity with appropriate formatting."""
        return f"{obj.quantity:,.8f}".rstrip('0').rstrip('.')
    quantity_display.short_description = 'Quantity'
    
    def price_display(self, obj):
        """Display price with formatting."""
        return f"${obj.price:,.6f}".rstrip('0').rstrip('.')
    price_display.short_description = 'Price'
    
    def value_display(self, obj):
        """Display trade value with formatting."""
        return f"${obj.gross_value:,.2f}"
    value_display.short_description = 'Value'
    
    def cost_display(self, obj):
        """Display total costs with formatting."""
        total_cost = obj.transaction_cost + obj.slippage_cost
        return f"${total_cost:,.2f}"
    cost_display.short_description = 'Total Cost'
    
    def total_cost_display(self, obj):
        """Display total cost for readonly field."""
        return f"${obj.total_cost:,.2f}"
    total_cost_display.short_description = 'Total Cost'