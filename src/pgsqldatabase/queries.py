"""
This a module with strings SQL requests to Database class

All strings have to be used in string format(). In formate() you need to put name of table
Typical usage example:

    GET_USER_QUERY.format(self.table_name)
"""
GET_ALL_ADMINS_ID = '''
SELECT user_id FROM {0}
WHERE is_admin = 1
'''

# Create table
CREATE_TABLE_QUERY = '''
CREATE TABLE IF NOT EXISTS {0}(
    user_id INTEGER PRIMARY KEY,
    full_name TEXT,
    user_name TEXT,
    is_admin INTEGER DEFAULT 0,
    history JSONB DEFAULT '[]'::jsonb
)
'''

# Get all information of user by id
GET_USER_QUERY = '''
SELECT * 
FROM {0} 
WHERE user_id = $1
'''

# Get all information from all users
GET_ALL_USERS_QUERY = '''
SELECT *
FROM {0}
'''

# Insert new user to table
INSERT_USER_QUERY = '''
INSERT INTO {0} (user_id, full_name, user_name, is_admin, history) 
VALUES ($1, $2, $3, $4, $5)
'''

# Count users
COUNT_USERS_QUERY = '''
SELECT COUNT(*) 
FROM {0}
'''

# Get all ids in table
GET_ALL_USER_IDS_QUERY = '''
SELECT user_id 
FROM {0}
'''

# Get session history by user id
GET_USER_HISTORY_QUERY = '''
SELECT history 
FROM {0} 
WHERE user_id = $1
'''

# Update session history by user id
UPDATE_USER_HISTORY_QUERY = '''
UPDATE {0} 
SET history = $2 
WHERE user_id = $1
'''

# Delete user by id
DELETE_USER_QUERY = '''
DELETE FROM {0}
'''

# Drop all information in table
DROP_TABLE_QUERY = '''
DROP TABLE {0}
'''
