import os
from main import prompt


# # tests are performed by reading commands from commands.txt and running them in prompter
# with open("help/commands.txt","r") as commands:
#     cmds = commands.readlines()

# run_=True
# for i in range(len(cmds)):
#     if cmds[i][0] == '[':
#         print("\nTesting command: "+cmds[i][:-1]+'\n')
#         prompt(eval(cmds[i][:-1]), run_=True)    

gap="\n\n      "
print('Introductory example:\n')

# # print aapl statements table 2021
example1 = "Example 1) display the 2021 financial statements for Apple in the terminal as provided by FinancialModelingPrep, key in fmpAPI terminal:"+gap+"print aapl statements table 2021'\n\nOnce the code terminates, a new prompter will appear. Key in 'exit' to go to the next example.\n"
print(example1)
os.system('python3 main.py')
print("\nNote: Quarterly data requires paid subscription, but the code can handle it; you'll just get an error if you're using the free version.")

# # web sec aapl 2021 10K
example2 = "\nExample 2) Retrieving the offical 10K filing from the SEC website is also possible. Key in:"+gap+"web sec aapl 2021 10K\n\nOnce done, key in 'exit' to go to the next example.\n"
print(example2)
os.system('python3 main.py')

# # print aapl income chart 5 Y
example3 = "\nExample 3) You can produce various charts using a pre-determined set of financial data super-imposed into one chart. Here I will consider income. Key in:"+gap+"print aapl income chart 5 Y\n\nIn addition to income, you can look at: stockequity, liability, margins, investment, valuation. Once done, Key in 'exit' to go to the next example.\n"
print(example3)
os.system('python3 main.py')

# # make watchlist alltrends 10 Y
example4 = "\nExample 4) Instead of producing one chart for one ticker at a time, lets say you want to produce all the types of charts for a list of tickers. You will find a textfile in chart/watchlist/tickers.txt. Open it and you will see the ticker list for Apple, Microsoft and Google. Keep the folder open and key in the prompter:"+gap+"make watchlist alltrends 10 Y\n\nOnce done, key in 'exit' to go to the next example.\n"
print(example4)
os.system('python3 main.py')
print("\nYou can edit the ticker list at anytime. You can also create new folders in /chart/ with it's own tickers.txt dedicated to a new list.\n")

# # compare r 5 Y -t aapl msft goog
example5 = "\nExample 5) You can plot metrics against several competitors for comaprison. To compare price-to-earning for Apple and Microsoft over a course of five years key in:"+gap+"compare pe 5 Y -t aapl msft\n\nOnce done, key in 'exit' to go to the next example.\n"
print(example5)
os.system('python3 main.py')
print("\n The pe is an abbreviation for price-to-earnings. You can view all possible comparison metric commands by keying in:"+gap+"list compare\n")
os.system('python3 main.py')

# # list commands
example6 ="\nExample 6) You can look up the various commands in this package by keying:"+gap+"list commands\n\nOnce done, key in 'exit' to conclude.\n"
print(example6)
os.system('python3 main.py')
print("\nHope this introduction was helpful! Run main.py in terminal to start fmpAPI terminal. \n\nIbrahim Al Balushi")
