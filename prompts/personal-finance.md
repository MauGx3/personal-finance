# Personal Finance Project default prompt

## Prompt Identification

- **Name**: Personal Finance Project default prompt
- **Version**: 0.4
- **Created By**: MauGx3
- **Last Modified**: 2025-09-12
- **Category**: Web and desktop app

## Purpose and Goals

- **Primary Goal**: Create a basic web and desktop app using Python, Django and Docker, primarily focused on functionality, that contains the features stated on the SCAFF structure below.
- **Use Cases**: web development, software development, finance, investing
- **Expected Output**: A simple GUI that has functional modules to be further developed and debugged.

## Technical Configuration

- **Target Model**: GitHub Copilot
- **Parameters**:
  - Temperature: 0.5
  - Token Limit: 5 tokens
  - Top-K: N/A
  - Top-P: N/A

## S.C.A.F.F. Structure

### Situation

This code uses Django as the web framework. The code depends on many dependencies, but the finance packages are essential, such as `yfinance`, `stockdex` etc that need to work properly and have fallbacks to guarantee best functionality for the app. The complete list of packages to be used in the project:

#### Data

* `polars` https://github.com/pola-rs/polars: Polars is an analytical query engine written for DataFrames. It is designed to be fast, easy to use and expressive. Better substitute to `pandas`. [Docs](https://docs.pola.rs/api/python/stable/reference/index.html) (also available for [node.js](https://github.com/pola-rs/nodejs-polars), [js-polars](https://github.com/pola-rs/js-polars), [[Rust]] and [[R]])
* `DataProfiler` https://github.com/capitalone/DataProfiler: The DataProfiler is a Python library designed to make data analysis, monitoring, and **sensitive data detection** easy. Loading **Data** with a single command, the library automatically formats & loads files into a DataFrame. **Profiling** the Data, the library identifies the schema, statistics, entities (PII / NPI) and more. Data Profiles can then be used in downstream applications or reports. [Docs](https://capitalone.github.io/DataProfiler/)
* `pyjanitor` https://pyjanitor-devs.github.io/pyjanitor/: Data cleaning and tidying-up for Polars, Pandas and many other tools. [Docs](https://pyjanitor-devs.github.io/pyjanitor/)
* `polars-fin` https://github.com/LVG77/polars-fin: calculates financial metrics related to capital gains calculations and more.
* `patito` https://github.com/JakobGM/patito: offers a simple way to declare pydantic data models which double as schema for your polars data frames. These schema can be used for: Simple and performant data frame validation, Easy generation of valid mock data frames for tests, Retrieve and represent singular rows in an object-oriented manner and Provide a single source of truth for the core data models in your code base. [Docs](https://patito.readthedocs.io/)
* `functime` https://github.com/functime-org/functime: production-ready **global forecasting** and **time-series feature extraction** on **large panel datasets**. also comes with time-series [preprocessing](https://docs.functime.ai/ref/preprocessing/) (box-cox, differencing etc), cross-validation [splitters](https://docs.functime.ai/ref/cross-validation/) (expanding and sliding window), and forecast [metrics](https://docs.functime.ai/ref/metrics/) (MASE, SMAPE etc). All optimized as [lazy Polars](https://pola-rs.github.io/polars-book/user-guide/lazy/using/) transforms. [Docs](https://docs.functime.ai/)
* `chartpy` https://github.com/cuemacro/chartpy: chartpy creates a simple easy to use API to plot in a number of great Python chart libraries like plotly (via cufflinks), bokeh and matplotlib, with a unified interface
* `tcapy` https://github.com/cuemacro/tcapy: library for doing transaction cost analysis (TCA).
* `bt` https://github.com/pmorissette/bt: flexible backtesting framework for Python used to test quantitative trading strategies. **Backtesting** is the process of testing a strategy over a given data set. This framework allows you to easily create strategies that mix and match different [Algos](http://pmorissette.github.io/bt/bt.html#bt.core.Algo). It aims to foster the creation of easily testable, re-usable and flexible blocks of strategy logic to facilitate the rapid development of complex trading strategies. [Docs](http://pmorissette.github.io/bt)

#### Finance

* `polars-trading` https://github.com/ngriffiths13/polars-trading: meant to provide some nice utilities for working with market data in Polars DataFrames. Much of the original inspiration has come from Marcos Lopez de Prado's book _Advances in Financial Machine Learning_. It is a work in progress with some basic functionality that will be added to over time.
* `polars-order-book` https://github.com/ChristopherRussell/polars-order-book: provides plugins for the Polars library that efficiently calculate summary information (price and quantity) for the top N levels of an order book.
* `polars-ta` https://github.com/wukan1986/polars_ta: implements common technical analysis (TA) indicators as fast, vectorized Polars expressions. It's used to compute indicators like SMA/EMA, RSI, MACD, Bollinger Bands, etc., directly on Polars DataFrames for trading analysis, backtesting, and feature engineering.
* `OptionLab` https://github.com/rgaveiga/optionlab: designed to provide quick evaluation of option strategy ideas. The code produces various outputs, including the profit/loss profile of the strategy on a user-defined target date, the range of stock prices for which the strategy is profitable (i.e., generating a return greater than $0.01), the Greeks associated with each leg of the strategy using the Black-Sholes model, the resulting debit or credit on the trading account, the maximum and minimum returns within a specified lower and higher price range of the underlying asset, and an estimate of the strategy's probability of profit. [Docs](https://rgaveiga.github.io/optionlab)
* `investing-algorithm-framework` https://github.com/coding-kitties/investing-algorithm-framework: built to streamline the entire lifecycle of quantitative trading strategies from signal generation and backtesting to live deployment. It offers a complete quantitative workflow, featuring two dedicated backtesting engines: A vectorized backtest engine for fast signal research and prototyping and An event-based backtest engine for realistic and accurate strategy evaluation. The framework supports live trading across multiple exchanges and offers flexible deployment options, including Azure Functions and AWS Lambda. Designed for extensibility, it allows you to integrate custom strategies, data providers, and order executors, enabling support for any exchange or broker. It natively supports multiple data formats, including OHLCV, ticker, and custom datasets with seamless compatibility for both Pandas and Polars DataFrames. [Docs](https://coding-kitties.github.io/investing-algorithm-framework/)
* `qis` https://github.com/ArturSepp/QuantInvestStrats: implements Python analytics for visualisation of financial data, performance reporting, analysis of quantitative strategies.
* `earnalotbot` https://github.com/julianwagle/earnalotbot: scaffolding for advanced python based developers looking to make trading bots. It comes equipped with basic packages for live-trading, paper-trading, web-scrapping, reinforcement-learning, a database for long-term strategy analysis and much more.
* `pandas_market_calendars` https://github.com/rsheftel/pandas_market_calendars: The pandas_market_calendars package looks to fill that role with the holiday, late open and early close calendars for specific exchanges and OTC conventions. pandas_market_calendars also adds several functions to manipulate the market calendars and includes a date_range function to create a pandas DatetimeIndex including only the datetimes when the markets are open. Additionally the package contains product specific calendars for future exchanges which have different market open, closes, breaks and holidays based on product type. [Docs](http://pandas-market-calendars.readthedocs.io/en/latest/)
* `findatapy` https://github.com/cuemacro/findatapy: creates an easy to use Python API to download market data from many sources including ALFRED/FRED, Bloomberg, Yahoo, Google etc. using a unified high level interface. Users can also define their own custom tickers, using configuration files. There is also functionality which is particularly useful for those downloading FX market data.
* `yahoo-finance-server` https://github.com/AgentX-ai/yahoo-finance-server **A Model Context Protocol (MCP) server that lets your AI interact with Yahoo Finance** - get comprehensive stock market data, news, financials, and more..
* `finmarketpy` https://github.com/cuemacro/finmarketpy: enables you to analyze market data and also to backtest trading strategies using a simple to use API, which has prebuilt templates for you to define backtest.
* `Finance` https://github.com/shashankvemuri/Finance: collection of 150+ Python for Finance programs for gathering, manipulating, and analyzing stock market data.
* `yfinance-cache` https://github.com/ValueRaider/yfinance-cache: Persistent caching wrapper for `yfinance` module. Intelligent caching, not dumb caching of web requests - only update cache where missing/outdated and new data expected. Idea is to minimise fetch frequency and quantity - Yahoo API officially only cares about frequency, but I'm guessing they also care about server load from scrapers.
* `yfinance` https://github.com/ranaroussi/yfinance: offers a Pythonic way to fetch financial & market data from [Yahoo!Ⓡ finance](https://finance.yahoo.com). [Docs](https://ranaroussi.github.io/yfinancehttps://ranaroussi.github.io/yfinance)
* `eiten` https://github.com/tradytics/eiten: implements various statistical and algorithmic investing strategies such as **Eigen Portfolios**, **Minimum Variance Portfolios**, **Maximum Sharpe Ratio Portfolios**, and **Genetic Algorithms** based Portfolios. It allows you to build your own portfolios with your own set of stocks that can beat the market. The rigorous testing framework included in Eiten enables you to have confidence in your portfolios.
* `thepassiveinvestor` https://github.com/JerBouma/ThePassiveInvestor: offers passive investing strategies, mostly through ETFs.
* `FinanceDatabase` https://github.com/JerBouma/FinanceDatabase: features 300,000+ symbols containing Equities, ETFs, Funds, Indices, Currencies, Cryptocurrencies, and Money Markets. It therefore allows you to obtain a broad overview of sectors, industries, types of investments, and much more.
* `FinanceToolkit` https://github.com/JerBouma/FinanceToolkit: open-source toolkit in which all relevant financial ratios ([150+](https://github.com/JerBouma/FinanceToolkit#core-functionality-and-metrics)), indicators and performance measurements are written down in the most simplistic way allowing for complete transparency of the method of calculation ([proof](https://github.com/JerBouma/FinanceToolkit/blob/main/financetoolkit/ratios/valuation_model.py)). This enables you to avoid dependence on metrics from other providers that do not provide their methods. With a large selection of financial statements in hand, it facilitates streamlined calculations, promoting the adoption of a consistent and universally understood methods and formulas.
* `stock-indicators-python` https://github.com/facioquo/stock-indicators-python: **Stock Indicators for Python** is a PyPI library package that produces financial market technical indicators. Send in historical price quotes and get back desired indicators such as moving averages, Relative Strength Index, Stochastic Oscillator, Parabolic SAR, etc. [Docs](https://python.stockindicators.dev/)

### Challenge

Create a complete personal finance/investing platform complete with portfolio tracking, asset data visualization, charts, quantitative analysis, backtesting etc. The app should be available as a deployment on Render for easier development with automatic container creation.

### Audience

Keep the code accessible to junior developers where possible, but don't let it be a constraint for making better code if a more complex approach would lead to better performance, security etc. Use comments where needed to explain code for a junior dev, in that case.

### Format

Code should follow Pythonic foundations. Use Google documentation guidelines for the Python code. This project was started by using the [cookiecutter-django] template. Formatter is `ruff`, `uv` should be preferred over `pip` when available. Tests will be done using `pytest`. Use `docker-compose` for local development and testing. Use `git` for version control, with a branching strategy that uses `main` as production-ready code, and `dev` as the main development branch. Feature branches should be used for specific features or bug fixes. The code should follow the "Easier to ask for forgiveness than permission" or EAFP style unless LBYL is assessed to be a better option for that particular block of code.

### Foundations

This code will be mostly deployed as a Docker container, so there should be a focus on maintain security and performance for a Docker app. For my personal use, I will run the app on a QNAP NAS running QTS 5. A large amount of data will be expected to be used as the app develops and the user collects more data, so consider best practices for following Big Data performance.

## Usage Guidelines

- **For Security-Critical Components**:

  - Set temperature: 0.0-0.2
  - Include explicit security requirements
  - Request detailed documentation of security measures
- **For Performance-Sensitive Components**:

  - Specify performance constraints
  - Request optimization techniques
  - Require complexity analysis
- **For UI Components**:

  - Include accessibility requirements
  - Specify responsive design needs
  - Reference design system patterns

## Effectiveness Metrics

- **Success Rate**: 85% usable on first attempt
- **Iteration Count**: Usually 3 to 5 iterations
- **Issues Found**: None so far
- **Time Savings**: Approximately 5 to 7 hours per implementation

## Documentation

- **Related Components**: N/A
- **Security Review**: Codebase verified by Snyk.io
- **Notes and Insights**: This prompt was created based on the Vibe Coding Framework and follows the S.C.A.F.F. Prompt Structure. Refer to this docs regarding AI coding: [https://docs.vibe-coding-framework.com/](https://docs.vibe-coding-framework.com/)
- **Improvement History**:
  - 0.1: initial prompt
  - 0.2: added more details to the SCAFF structure
  - 0.3: added more packages to Situation and added Render info
  - 0.4: added EAFP info
