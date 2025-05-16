from setuptools import setup, find_packages

setup(
    name="equipment-tracker",
    version="0.1.0",
    description="A tool for tracking and managing health physics equipment inventory and calibration",
    author="Health Physics Department",
    packages=find_packages(),
    install_requires=[
        "pandas",
        "openpyxl",
        "matplotlib",
        "xlrd>=2.0.1",
        "argparse",
    ],
    entry_points={
        'console_scripts': [
            'equipment-tracker=scripts.analysis.equipment_tracker:main',
            'maintenance-tracker=scripts.analysis.maintenance_tracker:main',
            'data-explorer=scripts.analysis.data_explorer:explorer',
            'calibration-notifier=scripts.utilities.calibration_notifier:main',
        ],
    },
)