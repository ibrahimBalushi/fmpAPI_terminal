# FinancialModelingPrep api terminal / fmpAPI_terminal
Command-line interface to access and process financial data from www.financialmodelingprep.com. 
This program produce charts and tables.

# About this package
It is a command-line prompter in terminal to retrieve and visualize various financial data from www.financialmodelingprep.com
Designed to produce tables and charts summarizing financial metrics of companies trades on various stock exhcnages. 

# Pre-requirsites
An apikey from FinancialModelingPrep needs is needed, and should be stored in the environment variable `FMP_API_KEY`.
`
To permanently store your api key in your .bashrc file run:

echo 'export FMP_API_KEY=12345678' >> ~.bashrc

# Installation
Download this git repo, open the base folder and run

pip install . 

or for an in-place editable installation run

pip install . -e

# Examples
To demonstrate some of its key functionalities, please run the example.py script which walks you through six examples.
