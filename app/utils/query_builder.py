def get_query(*condition, fetch:str, table:str):
    condition_clauses = " AND ".join(f"{col} = ${i+1}" for i, col in enumerate(condition))
    
    where_clauses = f"WHERE {condition_clauses}" if condition else " " 
    
    query = f""" 
            SELECT {fetch} FROM {table} {where_clauses}
        """
    return query.strip()

def insert_query(model: dict, table:str, returning:str = "*"):
    '''
        The sequence of the values need to be match with the model
    '''

    keys = ", ".join(list(model.keys()))
    placeholder = ", ".join(f'${i+1}' for i in range(len(model.keys())))

    query = f"""
        INSERT INTO {table} ({keys}) VALUES ({placeholder}) RETURNING {returning}
    """
    return query

def update_query(*conditions, model:dict, table:str):
    # set_clauses = ", ".join(f"{column} = {value}" for column, value in model.items())
    set_clauses = ", ".join(f"{column} = ${i+1}" for i, column in enumerate(model.keys()))
    condition_clauses = " AND ".join(f"{condition} = ${i+1+len(model)} " for i, condition in enumerate(conditions))
    query = f"""
        UPDATE {table}
        SET {set_clauses}
        WHERE {condition_clauses}
    """
    
    return query


def delete_query(*condition:str, table:str):

    condition_clauses = " AND ".join(f"{condition} = ${i+1}" for i, condition in enumerate(condition))
    query = f"""
        DELETE FROM {table} WHERE {condition_clauses}
    """
    return query
