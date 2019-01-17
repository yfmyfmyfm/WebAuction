import web

db = web.database(dbn='sqlite',
        db='AuctionBase.db' #TODO: add your SQLite database filename
    )

######################BEGIN HELPER METHODS######################

# Enforce foreign key constraints
# WARNING: DO NOT REMOVE THIS!
def enforceForeignKey():
    db.query('PRAGMA foreign_keys = ON')

# initiates a transaction on the database
def transaction():
    return db.transaction()
# Sample usage (in auctionbase.py):
#
# t = sqlitedb.transaction()
# try:
#     sqlitedb.query('[FIRST QUERY STATEMENT]')
#     sqlitedb.query('[SECOND QUERY STATEMENT]')
# except Exception as e:
#     t.rollback()
#     print str(e)
# else:
#     t.commit()
#
# check out http://webpy.org/cookbook/transactions for examples

# returns the current time from your database
def getTime():
    # TODO: update the query string to match
    # the correct column and table name in your database
    query_string = 'select Time from CurrentTime'
    results = db.query(query_string)
    # alternatively: return results[0]['currenttime']
    return results[0].Time # TODO: update this as well to match the
                                  # column name

# returns a single item specified by the Item's ID in the database
# Note: if the `result' list is empty (i.e. there are no items for a
# a given ID), this will throw an Exception!
def getItemById(item_id):
    # TODO: rewrite this method to catch the Exception in case `result' is empty
    query_string = 'select * from Items where itemID = $itemID'
    try:
        result = db.query(query_string, {'itemID': item_id})
        return result[0]
    except not result:
        return "No result"
    
    
def getCategoryById(item_id):
    query_string = 'select * from Categories where ItemId = $ItemID'
    try:
        result = db.query(query_string, {'ItemID': item_id})
        return result
    except not result:
        return "No result"

def getBidById(item_id):
    query_string = 'select * from Bids where ItemId = $ItemID order by Time desc'
    try:
        result = db.query(query_string, {'ItemID': item_id})
        return result
    except not result:
        return "No result"

def auctionGetter(item_id):
    query_string = 'SELECT * FROM Bids WHERE ItemID = $itemID ORDER BY Time DESC LIMIT 1'
    result = query('select * from bids where itemid = $itemid order by time desc limit 1', { 'itemid': item_id })
    if(result) :
        return result[0]
    else :
        return None
    
def getStatusById(item_id):
    query_open = 'select * from Items where ItemID = $ItemID and Started <= (select Time from CurrentTime) and Ends > (select Time from CurrentTime) and (Currently < Buy_Price or Buy_Price is NULL)'
    result_open = db.query(query_open, {'ItemID' : item_id})
    if result_open:
	return 'open'
    else:
        query_close = 'select * from Items where ItemID = $ItemID and (Ends <= (select Time from CurrentTime) or Currently >= Buy_Price)'
        result_close = db.query(query_close, {'ItemID':item_id})
        if result_close:
	    return 'close'
        else:
	    return 'not started'
# wrapper method around web.py's db.query method
# check out http://webpy.org/cookbook/query for more info
def query(query_string, vars = {}):
    return list(db.query(query_string, vars))

#####################END HELPER METHODS#####################

#TODO: additional methods to interact with your database,
# e.g. to update the current time
def updateTime(time):
    txn = transaction()
    try:
        
#         ##if time is less than or equal to current time, return false
#         q1 = query('select time from currenttime where time <= $time', {'time':time})
#         if (len(q1)<= 0 ):
#             return "Fail to update time"
        query_string = 'update CurrentTime set Time = $time'
        db.query(query_string, {'time':time})
    except:
        txn.rollback()
        return "Cannot Update"
    else:
        txn.commit()
        return "Successfully update time"

def addBid(item_id, user_id, amount):
    txn = transaction()
    try:
        ##check whether the user exists.if not, directly return false.
        q1 = query('select * from Users where UserID =  $user_id', vars={ 'user_id' : user_id })
        if (len(q1)<=0): 
            return False
        ##check whether the item is exist and open and the amount if greater than currently: if not, directly return false.
        q2 = query('select * from Items where ItemID = $item_id and Started <= (select Time from CurrentTime) and Ends > (select Time from CurrentTime) and ( (Buy_Price is NULL) or (Currently < Buy_Price) ) and Currently < $Amount', vars={'item_id':item_id, 'Amount': amount })
        if (len(q2)<=0):
            return False
        ##check if there has already exists bid at the current time: if yes, return false
        q3 = query('select * from bids where ItemID = $item_id and time = (select Time from CurrentTime)', vars={'item_id':item_id })
        if (len(q3)>0):
            return False
        ##if buy price in items is not null
        ####if ends in items hasn't been reached, but given amount has been greater than buy price
        ######update ends to currenttime
        db.query('update Items SET Ends=(select Time from CurrentTime) WHERE ItemID=$item_id and ( (not (buy_price is NULL)) and ($Amount >= buy_price) )', {'item_id':item_id, 'Amount': amount})
        ##add new bid to table bids
        db.query('insert into Bids values($item_id, $user_id, $Amount, (select Time from CurrentTime))', {'item_id':item_id, 'user_id':user_id, 'Amount':amount})
#         ##if number of bids in items == 0, first bid = amount in table items
#         db.query('update Items SET first_bid=$Amount WHERE ItemID=$item_id and number_of_bids = 0', {'item_id':item_id, 'Amount': amount})
    #     ##currently change to amount, and number of bids++ in table items
    #     query('update Items SET currently=$Amount, number_of_bids = (1+(select number_of_bids from items where itemid = $item_id)) WHERE ItemID=$item_id', {'item_id':item_id, 'Amount': amount})
    except:
        txn.rollback()
        return False
    else:
        txn.commit()
        return True

def browse(itemID = '', category = '', description = '', pmin = '', pmax = '', status = ''):
    query_string = 'select * from Items where '
    field = {}
    flag = True
    if itemID != '':
        field['itemID'] = itemID
        query_string += 'ItemID in (select ItemID from Items where ItemID = $itemID)'
        flag = False 

    if category != '':
        field['category'] = category
        if flag == True:
            query_string += 'ItemID in (select ItemID from Categories where Category = $category)'
            flag = False
        else:
            query_string += ' and ItemID in (select ItemID from Categories where Category = $category)'
            
    if description != '':    
        field['description'] = description
        if flag == True: 
            query_string += 'ItemID in (select ItemID from Items where Description like $description)'
            flag = False
        else:
            query_string += ' and ItemID in (select ItemID from Items where Description like $description)'
            
    if pmin != '':
        field['pmin'] = pmin
        if flag == True:
            query_string += 'ItemID in (select ItemID from Items where Currently >= $pmin)'
            flag = False
        else:
            query_string += ' and ItemID in (select ItemID from Items where Currently >= $pmin)'

    if pmax != '':
        field['pmax'] = pmax
        if flag == True: 
            query_string += 'ItemID in (select ItemID from Items where Currently <= $pmax)'
            flag = False
        else:
            query_string += ' and ItemID in (select ItemID from Items where Currently <= $pmax)'

    if status == 'open':
        if flag == True:
            query_string += 'Started <= (select Time from CurrentTime) and Ends > (select Time from CurrentTime) and (Currently < Buy_Price or Buy_Price is NULL)'
            flag = False
        else:
            query_string += ' and Started <= (select Time from CurrentTime) and Ends > (select Time from CurrentTime) and (Currently < Buy_Price or Buy_Price is NULL)'
    elif status == 'close':
        if flag == True:
            query_string += '(Ends <= (select Time from CurrentTime) or Currently >= Buy_Price)'
            flag = False
        else:
            query_string += ' and (Ends <= (select Time from CurrentTime) or Currently >= Buy_Price)'
    elif status == 'notStarted':
        if flag == True:
            query_string += 'Started> (select Time from CurrentTime)'
            flag = False
        else:
            query_string += ' and Started> (select Time from CurrentTime)'

    if flag == True:
        query_string = 'select * from Items'
    result = db.query(query_string, field)
    return result
