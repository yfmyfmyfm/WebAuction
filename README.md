# Web-Interface-An-AuctionBase-System-Given-a-decade-s-eBay-transaction-data-
@Author: Yifan Mei & Meiliu Wu

1. Loaded a decade’s eBay transaction data in JSON (in the directory "ebay-data") form into a self-designed SQLite database (by running "runparser.sh" in the directory "create_auctionbase") following ER design model. 

2. By running "auctionbase.py", generated dynamic HTML pages(in the directory "templates") for an AuctionBase system over the database. 

3. Inside the system, implemented the following functionalities ability (in file "sqlitedb.py") for auction users to enter bids on open auctions, automatic auction closing, ability to browse auctions of interest based on item ID/category/item description/min price/max price/open/closed status, ability to view all relevant information pertaining to a single auction etc. by utilizing Python.
