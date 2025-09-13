"""
Dependency Configuration

Configuration file that defines all dependencies and their characteristics.
This centralizes dependency management instead of scattering try/except blocks.
"""

from typing import Dict, Any

# Dependency configuration with fallback strategies
DEPENDENCY_CONFIG: Dict[str, Dict[str, Any]] = {
    # External finance and data libraries
    "stockdex": {
        "import_path": "stockdex",
        "required": False,
        "fallback_available": True,
        "fallback_strategy": "Use alternative price fetching APIs",
        "description": "Stock data and financial information API",
        "install_command": "pip install stockdex"
    },
    
    "yfinance": {
        "import_path": "yfinance", 
        "required": False,
        "fallback_available": True,
        "fallback_strategy": "Use alternative price data sources",
        "description": "Yahoo Finance API for stock data",
        "install_command": "pip install yfinance"
    },
    
    "yahoofinancials": {
        "import_path": "yahoofinancials",
        "required": False,
        "fallback_available": True,
        "fallback_strategy": "Use yfinance or other price sources",
        "description": "Alternative Yahoo Finance API",
        "install_command": "pip install yahoofinancials"
    },
    
    "alpha_vantage": {
        "import_path": "alpha_vantage",
        "required": False,
        "fallback_available": True,
        "fallback_strategy": "Use free data sources or cached data",
        "description": "Alpha Vantage financial data API",
        "install_command": "pip install alpha_vantage"
    },
    
    # Database dependencies
    "pymongo": {
        "import_path": "pymongo",
        "required": False,
        "fallback_available": True,
        "fallback_strategy": "Use SQLite database backend",
        "description": "MongoDB Python driver",
        "install_command": "pip install pymongo"
    },
    
    "alembic": {
        "import_path": "alembic",
        "required": False,
        "fallback_available": False,
        "fallback_strategy": "Database migrations not available",
        "description": "Database migration tool for SQLAlchemy",
        "install_command": "pip install alembic"
    },
    
    "psycopg2": {
        "import_path": "psycopg2",
        "required": False,
        "fallback_available": True,
        "fallback_strategy": "Use SQLite database backend",
        "description": "PostgreSQL adapter for Python",
        "install_command": "pip install psycopg2-binary"
    },
    
    # Data analysis and visualization
    "pandas": {
        "import_path": "pandas",
        "required": True,
        "fallback_available": False,
        "fallback_strategy": "Core functionality requires pandas",
        "description": "Data manipulation and analysis library",
        "install_command": "pip install pandas"
    },
    
    "numpy": {
        "import_path": "numpy",
        "required": True,
        "fallback_available": False,
        "fallback_strategy": "Core calculations require numpy",
        "description": "Numerical computing library",
        "install_command": "pip install numpy"
    },
    
    "matplotlib": {
        "import_path": "matplotlib",
        "required": False,
        "fallback_available": True,
        "fallback_strategy": "Use plotly or disable visualizations",
        "description": "Plotting and visualization library",
        "install_command": "pip install matplotlib"
    },
    
    "plotly": {
        "import_path": "plotly",
        "required": False,
        "fallback_available": True,
        "fallback_strategy": "Use matplotlib or disable interactive charts",
        "description": "Interactive plotting library",
        "install_command": "pip install plotly"
    },
    
    "seaborn": {
        "import_path": "seaborn",
        "required": False,
        "fallback_available": True,
        "fallback_strategy": "Use matplotlib for basic plots",
        "description": "Statistical data visualization",
        "install_command": "pip install seaborn"
    },
    
    # Machine learning and statistics
    "scikit-learn": {
        "import_path": "sklearn",
        "required": False,
        "fallback_available": True,
        "fallback_strategy": "Disable advanced analytics features",
        "description": "Machine learning library",
        "install_command": "pip install scikit-learn"
    },
    
    "statsmodels": {
        "import_path": "statsmodels",
        "required": False,
        "fallback_available": True,
        "fallback_strategy": "Use basic statistics only",
        "description": "Statistical models and econometrics",
        "install_command": "pip install statsmodels"
    },
    
    # Web and API
    "requests": {
        "import_path": "requests",
        "required": True,
        "fallback_available": False,
        "fallback_strategy": "Core API functionality requires requests",
        "description": "HTTP library for API calls",
        "install_command": "pip install requests"
    },
    
    "fastapi": {
        "import_path": "fastapi",
        "required": False,
        "fallback_available": True,
        "fallback_strategy": "Web API features disabled",
        "description": "Modern web framework for APIs",
        "install_command": "pip install fastapi"
    },
    
    # GUI frameworks
    "tkinter": {
        "import_path": "tkinter",
        "required": False,
        "fallback_available": True,
        "fallback_strategy": "GUI features disabled",
        "description": "Built-in GUI toolkit",
        "install_command": "Usually comes with Python"
    },
    
    "dash": {
        "import_path": "dash",
        "required": False,
        "fallback_available": True,
        "fallback_strategy": "Web dashboard features disabled",
        "description": "Web application framework",
        "install_command": "pip install dash"
    }
}

# Feature flags configuration
FEATURE_FLAGS: Dict[str, Dict[str, Any]] = {
    "portfolio_management": {
        "enabled": True,
        "dependencies": ["pandas", "numpy"],
        "optional_dependencies": ["stockdex", "yfinance"],
        "description": "Core portfolio management features"
    },
    
    "price_fetching": {
        "enabled": True,
        "dependencies": ["requests"],
        "optional_dependencies": ["stockdex", "yfinance", "yahoofinancials", "alpha_vantage"],
        "description": "Stock price data fetching"
    },
    
    "database_storage": {
        "enabled": True,
        "dependencies": [],
        "optional_dependencies": ["pymongo", "psycopg2", "alembic"],
        "description": "Database storage and persistence"
    },
    
    "data_visualization": {
        "enabled": True,
        "dependencies": [],
        "optional_dependencies": ["matplotlib", "plotly", "seaborn"],
        "description": "Data visualization and charting"
    },
    
    "advanced_analytics": {
        "enabled": False,  # Disabled by default, can be enabled if dependencies available
        "dependencies": [],
        "optional_dependencies": ["scikit-learn", "statsmodels"],
        "description": "Advanced financial analytics and machine learning"
    },
    
    "web_interface": {
        "enabled": False,  # Disabled by default
        "dependencies": [],
        "optional_dependencies": ["fastapi", "dash"],
        "description": "Web-based user interface"
    },
    
    "desktop_gui": {
        "enabled": False,  # Disabled by default
        "dependencies": [],
        "optional_dependencies": ["tkinter"],
        "description": "Desktop GUI application"
    }
}