def get_query(*condition, fetch:str, table:str):
    """
        Generates a SELECT query
            example: SELECT * FROM users WHERE email = $1

        parameter: *condition 
            the conditions you want on your query(e.g., 'WHERE email = $1')

            you will pass the conditions like this 
                get_query("email", fetch="*", table="users)
    """

    
    condition_clauses = " AND ".join(f"{col} = ${i+1}" for i, col in enumerate(condition)) # generates '<condition> = $1 AND <condition> = $2' based on how is your condition
    
    where_clauses = f"WHERE {condition_clauses}" if condition else " " # adds your conditon clauses WHERE clause (e.g, WHRE <conditon clauses>)
    
    query = f""" 
            SELECT {fetch} FROM {table} {where_clauses}
        """
    return query.strip()

def insert_query(model: dict, table:str, returning:str = "*"):
    '''
        Generates insert query
            Example: INSERT INTO users (<keys>) VALUES (<placeholder>) RETURNING (<returning>)
    '''

    keys = ", ".join(list(model.keys())) # generates the keys such as name, email and etc..
    placeholder = ", ".join(f'${i+1}' for i in range(len(model.keys()))) # generates the placeholder (e.g., $1, $2)

    query = f"""
        INSERT INTO {table} ({keys}) VALUES ({placeholder}) RETURNING {returning}
    """
    return query

def update_query(*conditions, model:dict, table:str):
    """
        Generates update query
            Example: UPDATE users SET name = $1 WHERE user_id = $1
    """
    set_clauses = ", ".join(f"{column} = ${i+1}" for i, column in enumerate(model.keys())) # generates set_clauses that indicates what to change/update on the DB
    condition_clauses = " AND ".join(f"{condition} = ${i+1+len(model)} " for i, condition in enumerate(conditions))# generates '<condition> = $1 AND <condition> = $2' based on how is your condition
    query = f"""
        UPDATE {table}
        SET {set_clauses}
        WHERE {condition_clauses}
    """
    
    return query


def delete_query(*condition:str, table:str):
    """
        Generate delete query
            Example: DELETE FROM users WHERE user_id = $1
    """

    condition_clauses = " AND ".join(f"{condition} = ${i+1}" for i, condition in enumerate(condition))# generates '<condition> = $1 AND <condition> = $2' based on how is your condition
    query = f"""
        DELETE FROM {table} WHERE {condition_clauses}
    """
    return query
