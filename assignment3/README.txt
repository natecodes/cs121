Instructions for running the search engine
------------------------------------------
Building the index:
 - install any dependencies such as nltk
 - run "python indexer.py" from the command line
 - it will print out every time 100 documents are parsed,
   every time a batch file is created (every 10K documents),
   and when merging, every time an index file is created

Running the search from command line:
 - run "python search.py" from the command line
 - the terminal will prompt you for a query
 - type in your query then press enter
 - the terminal will give you results, their relevancy scores, and the total search time
 - type "exit" to stop the search

Running the search with Web GUI:
 - the Web GUI is a Next.js project bootstrapped with "create-next-app"
 - run "python server.py" from the command line to start the Python server
 - run "yarn install" from the command line to install the necessary packages
 - run "yarn dev" from the command line to run the development server
 - open http://localhost:3000 in your browser to see the result.
