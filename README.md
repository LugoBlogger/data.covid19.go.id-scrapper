# web-scrapper.py
This simple scrapper is created using Python to test a possibility to use `multiprocessing` and `threading` modules 
for unrelated usage (depends on who we are, 😆).

When the prototyped program scrapped a dynamics web page using Selenium, there is no a verbose argument in `selenium.webdriver.Chrome`
to let us know that the headless web browser is running or not. I prefer to run a program with minimalistic verbosity to make
sure that the program is running as I intended and also a little bit acknowledged me that the program doesn't run forever
(like most of ML algorithms). 

And somehow, I thought that it was a great step to know how to run mutliple methods in a single run. 
Then I decided to create an indicator, by printing a simple dots simulataneously running with the headless web browser.
The two main source for my inspiration to speed-up building the code are
comming from ![StackOverflow]("https://stackoverflow.com/questions/10415028/how-can-i-recover-the-return-value-of-a-function-passed-to-multiprocessing-proce").
and ![GeeksforGeeks: Code #4]("https://www.geeksforgeeks.org/start-and-stop-a-thread-in-python/"). The code that I have written
and that two main sources are very unrelated but the logical structure almost similar (with several modifications in data types
and flow of the program).

## Demo 

<p align="center">
<img src="https://github.com/LugoBlogger/web-scrapper/blob/master/web-scrapper.gif" width=50%>
</p>

## Usage
The program is self-contained with its documentation. We can get the information by typing in terminal

```
$ python web-scrapping.py -h
```

## To do list

- Improve the design in the printed terminal output
- Transform all `def` into `class` for succint and robust structure.
