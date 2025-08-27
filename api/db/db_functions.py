"""
Database functions for Group Change Params API
Uses direct Firebird connection for database operations
"""

import fdb
from typing import List, Dict, Any
from modules.config import DB_CONFIG, ENABLE_LOGGING


def get_db_connection():
    """
    Получить соединение с базой данных Firebird
    """
    try:
        con = fdb.connect(
            host=DB_CONFIG['host'],
            port=DB_CONFIG['port'],
            database=DB_CONFIG['database'],
            user=DB_CONFIG['user'],
            password=DB_CONFIG['password'],
            charset=DB_CONFIG['charset']
        )
        return con
    except Exception as e:
        if ENABLE_LOGGING:
            print(f"❌ Ошибка подключения к БД: {e}")
        raise


def get_wood_params() -> List[Dict[str, Any]]:
    """Get all wood (breed) parameters from real database"""
    try:
        con = get_db_connection()
        cur = con.cursor()
        
        sql = "SELECT sp.ID, sp.NAME FROM STRUCTS_PARAMS sp WHERE sp.NAME LIKE '%Wood%'"
        cur.execute(sql)
        rows = cur.fetchall()
        
        result = []
        for row in rows:
            result.append({
                "ID": row[0],
                "NAME": row[1]
            })
        
        cur.close()
        con.close()
        
        if ENABLE_LOGGING:
            print(f"✅ Получено {len(result)} параметров дерева")
            
        return result
        
    except Exception as e:
        if ENABLE_LOGGING:
            print(f"❌ Ошибка получения параметров дерева: {e}")
        raise


def get_available_breeds() -> List[Dict[str, Any]]:
    """Get all available breed options - hardcoded list as specified"""
    # Return predefined list as specified by user
    return [
        {"ID": 1, "CODE": "Сосна Люкс", "TYPEID": 1},
        {"ID": 2, "CODE": "Сосна сращенный", "TYPEID": 1},
        {"ID": 3, "CODE": "Лиственница Люкс", "TYPEID": 2},
        {"ID": 4, "CODE": "Лиственница сращенный", "TYPEID": 2},
        {"ID": 5, "CODE": "Дуб Люкс", "TYPEID": 3},
        {"ID": 6, "CODE": "Дуб сращенный", "TYPEID": 3},
        {"ID": 7, "CODE": "Осина сращенный", "TYPEID": 4},
    ]


def get_color_groups() -> List[Dict[str, Any]]:
    """Get all color groups from real database"""
    try:
        con = get_db_connection()
        cur = con.cursor()
        
        sql = """
        SELECT cg.TITLE as CG_TITLE                          
        FROM COLORGROUP cg
        WHERE cg.DELETED = 0
        AND cg.GROUPID IN (1,2,3,5,6)
        ORDER BY cg.TITLE
        """
        cur.execute(sql)
        rows = cur.fetchall()
        
        result = []
        for row in rows:
            result.append({
                "CG_TITLE": row[0]
            })
        
        cur.close()
        con.close()
        
        if ENABLE_LOGGING:
            print(f"✅ Получено {len(result)} групп цветов")
            
        return result
        
    except Exception as e:
        if ENABLE_LOGGING:
            print(f"❌ Ошибка получения групп цветов: {e}")
        raise


def get_colors_by_group(group_title: str) -> List[Dict[str, Any]]:
    """Get colors by group from real database"""
    print(f"🔄 БД: Запрос цветов для группы '{group_title}'")
    try:
        con = get_db_connection()
        cur = con.cursor()
        
        sql = """
        SELECT c.TITLE as COLOR                    
        FROM COLORS c
        JOIN COLORGROUP cg ON cg.GROUPID = c.GROUPID
        WHERE c.DELETED = 0 
        AND cg.TITLE = ?
        ORDER BY c.TITLE
        """
        print(f"🔄 БД: Выполняем SQL: {sql}")
        print(f"🔄 БД: Параметр: group_title = '{group_title}'")
        
        cur.execute(sql, (group_title,))
        rows = cur.fetchall()
        
        result = []
        for row in rows:
            result.append({
                "COLOR": row[0]
            })
        
        cur.close()
        con.close()
        
        print(f"🔄 БД: Получено {len(result)} цветов для группы '{group_title}'")
        if ENABLE_LOGGING:
            print(f"✅ Получено {len(result)} цветов для группы '{group_title}'")
            
        return result
        
    except Exception as e:
        print(f"❌ БД: Ошибка получения цветов для группы '{group_title}': {e}")
        if ENABLE_LOGGING:
            print(f"❌ Ошибка получения цветов для группы '{group_title}': {e}")
        raise


def get_order_colors(order_id: int) -> List[Dict[str, Any]]:
    """Get colors currently used in order from real database"""
    try:
        con = get_db_connection()
        cur = con.cursor()
        
        sql = """
        SELECT DISTINCT c.TITLE as COLOR_TITLE                                
        FROM ORDERS_ITEMS_ADDS_SETPARAMS oiasp
        JOIN COLORS c ON c.COLORID = oiasp.COLORVALUEID
        WHERE (oiasp.ID IN 
            (SELECT oiasp2.ID
            FROM ORDERS o2
            JOIN ORDERS_ITEMS oi2 ON oi2.ORDERID = o2.ID
            JOIN ORDERS_ITEMS_ADDS oia2 ON oia2.ORDERITEMID = oi2.ID
            JOIN ORDERS_ITEMS_ADDS_SETPARAMS oiasp2 ON oiasp2.ORDERITEMADDID = oia2.ID
            WHERE o2.ID = ?))
        AND (oiasp.PARAMID IN (SELECT sp.ID FROM STRUCTS_PARAMS sp WHERE sp.PARAMTYPE = 3))
        ORDER BY c.TITLE
        """
        cur.execute(sql, (order_id,))
        rows = cur.fetchall()
        
        result = []
        for row in rows:
            result.append({
                "COLOR_TITLE": row[0]
            })
        
        cur.close()
        con.close()
        
        if ENABLE_LOGGING:
            print(f"✅ Получено {len(result)} цветов для заказа {order_id}")
            
        return result
        
    except Exception as e:
        if ENABLE_LOGGING:
            print(f"❌ Ошибка получения цветов для заказа {order_id}: {e}")
        raise


def get_order_info(order_id: int) -> List[Dict[str, Any]]:
    """Get order information from real database"""
    try:
        con = get_db_connection()
        cur = con.cursor()
        
        sql = """
        SELECT 
            o.ID,
            o.ORDERNO,
            o.DATEORDER,
            o.ADRESSINSTALL as ORDER_NAME,
            co.NAME as CUSTOMER_NAME
        FROM ORDERS o
        LEFT JOIN CUSTOMERS c ON c.CUSTOMERID = o.CUSTOMERID
        LEFT JOIN CONTRAGENTS co ON co.CONTRAGID = c.CONTRAGID
        WHERE o.ID = ?
        """
        cur.execute(sql, (order_id,))
        rows = cur.fetchall()
        
        result = []
        for row in rows:
            # Format date to string for JSON serialization
            date_value = row[2]
            if date_value:
                try:
                    if hasattr(date_value, 'strftime'):
                        formatted_date = date_value.strftime("%Y-%m-%d")
                    else:
                        formatted_date = str(date_value)
                except Exception:
                    formatted_date = str(date_value) if date_value else None
            else:
                formatted_date = None
                
            result.append({
                "ID": row[0],
                "ORDERNO": row[1],
                "DATEORDER": formatted_date,
                "ORDER_NAME": row[3],
                "CUSTOMER_NAME": row[4]
            })
        
        cur.close()
        con.close()
        
        if ENABLE_LOGGING:
            print(f"✅ Получена информация о заказе {order_id}")
            
        return result
        
    except Exception as e:
        if ENABLE_LOGGING:
            print(f"❌ Ошибка получения информации о заказе {order_id}: {e}")
        raise


def update_breed_in_order(order_id: int, breed_code: str, selected_breeds: List[str] = None) -> bool:
    """
    Update breed (wood type) in order using the provided SQL query
    """
    print("🔧" + "=" * 79)
    print("🔧 STARTING BREED UPDATE PROCESS (ADDS)")
    print(f"🔧 Order ID: {order_id}")
    print(f"🔧 Breed Code: {breed_code}")
    print(f"🔧 Selected Breeds: {selected_breeds}")
    print("🔧" + "=" * 79)
    
    try:
        con = get_db_connection()
        cur = con.cursor()
        
        # Build SQL with optional filter for selected breeds
        if selected_breeds:
            # Create placeholders for IN clause
            placeholders = ",".join(["?" for _ in selected_breeds])
            breed_filter = f"""
            AND oiasp.ID IN (
                SELECT oiasp3.ID
                FROM ORDERS_ITEMS_ADDS_SETPARAMS oiasp3
                JOIN ENUM_ITEMS ei3 ON ei3.ID = oiasp3.ENUMVALUEID
                WHERE ei3.CODE IN ({placeholders})
                AND oiasp3.PARAMID IN (SELECT sp.ID FROM STRUCTS_PARAMS sp WHERE sp.NAME LIKE '%Wood%')
            )"""
        else:
            breed_filter = ""
        
        sql = f"""
        UPDATE ORDERS_ITEMS_ADDS_SETPARAMS oiasp
        SET oiasp.ENUMVALUEID = (
            SELECT ei2.ID
            FROM (
                SELECT ei.TYPEID
                FROM ORDERS_ITEMS_ADDS_SETPARAMS oiasp2
                JOIN ENUM_ITEMS ei ON ei.ID = oiasp2.ENUMVALUEID
                WHERE oiasp2.ID = oiasp.ID
            ) t
            JOIN ENUM_ITEMS ei2 ON ei2.TYPEID = t.TYPEID
            WHERE LOWER(TRIM(ei2.CODE)) LIKE ?
        )
        WHERE (
            oiasp.ID IN (
                SELECT oiasp2.ID
                FROM ORDERS o2
                JOIN ORDERS_ITEMS oi2 ON oi2.ORDERID = o2.ID
                JOIN ORDERS_ITEMS_ADDS oia2 ON oia2.ORDERITEMID = oi2.ID
                JOIN ORDERS_ITEMS_ADDS_SETPARAMS oiasp2 ON oiasp2.ORDERITEMADDID = oia2.ID
                WHERE o2.ID = ?
            )
        )
        AND (
            oiasp.PARAMID IN (
                SELECT sp.ID 
                FROM STRUCTS_PARAMS sp 
                WHERE sp.NAME LIKE '%Wood%'
            )
        )
        {breed_filter}
        """
        
        # Prepare parameters
        breed_param = f"{breed_code.lower()}"
        params = [breed_param, order_id]
        if selected_breeds:
            params.extend(selected_breeds)
        params = tuple(params)
        
        print(f"🔧 Original breed_code: '{breed_code}'")
        print(f"🔧 Lowercased: '{breed_code.lower()}'")
        print(f"🔧 With wildcards: '{breed_param}'")
        print(f"🔧 Final parameters: {params}")
        print(f"🔧 Parameter types: {[type(p).__name__ for p in params]}")
        
        print("🔧 About to execute UPDATE query...")
        cur.execute(sql, params)
        
        # Get the number of affected rows
        affected_rows = cur.rowcount
        
        # Commit the transaction
        con.commit()
        
        cur.close()
        con.close()
        
        print(f"✅ Breed updated successfully for order {order_id}")
        print(f"   Affected rows: {affected_rows}")
        print("🔧" + "=" * 79)
        return True
        
    except Exception as e:
        print(f"❌ Error updating breed: {e}")
        print("🔧" + "=" * 79)
        return False


def update_color_in_order(order_id: int, new_color: str, new_colorgroup: str, old_colors: List[str]) -> bool:
    """
    Update color in order using the provided SQL query
    """
    print("🔧" + "=" * 79)
    print("🔧 STARTING COLOR UPDATE PROCESS")
    print(f"🔧 Order ID: {order_id}")
    print(f"🔧 New Color: {new_color}")
    print(f"🔧 New Color Group: {new_colorgroup}")
    print(f"🔧 Selected Old Colors: {old_colors}")
    print("🔧" + "=" * 79)
    
    try:
        con = get_db_connection()
        cur = con.cursor()
        
        # For Firebird, we need to use IN with parameters properly
        # We'll execute the query with parameters
        
        sql = """
        UPDATE ORDERS_ITEMS_ADDS_SETPARAMS oiasp
        SET oiasp.COLORVALUEID = (
            SELECT c.COLORID
            FROM COLORS c
            JOIN COLORGROUP cg ON cg.GROUPID = c.GROUPID
            WHERE c.TITLE LIKE ?
            AND cg.TITLE LIKE ?
        )
        WHERE (
            oiasp.ID IN (
                SELECT oiasp2.ID
                FROM ORDERS o2
                JOIN ORDERS_ITEMS oi2 ON oi2.ORDERID = o2.ID
                JOIN ORDERS_ITEMS_ADDS oia2 ON oia2.ORDERITEMID = oi2.ID
                JOIN ORDERS_ITEMS_ADDS_SETPARAMS oiasp2 ON oiasp2.ORDERITEMADDID = oia2.ID
                LEFT JOIN COLORS c ON c.COLORID = oiasp2.COLORVALUEID
                WHERE o2.ID = ?
                AND c.TITLE IN ({})
            )
        )
        AND (
            oiasp.PARAMID IN (
                SELECT sp.ID 
                FROM STRUCTS_PARAMS sp 
                WHERE sp.PARAMTYPE = 3
            )
        )
        """.format(",".join(["?" for _ in old_colors]))
        
        # Prepare parameters: new_color, new_colorgroup, order_id, then old_colors
        params = (f"%{new_color}%", f"%{new_colorgroup}%", order_id) + tuple(old_colors)
        
        cur.execute(sql, params)
        
        # Get the number of affected rows
        affected_rows = cur.rowcount
        
        # Commit the transaction
        con.commit()
        
        cur.close()
        con.close()
        
        if ENABLE_LOGGING:
            print(f"✅ Color updated successfully for order {order_id}")
            print(f"   Affected rows: {affected_rows}")
            
        return True
        
    except Exception as e:
        if ENABLE_LOGGING:
            print(f"❌ Error updating color: {e}")
        return False


def update_breed_in_stuffsets_orderitems(order_id: int, breed_code: str, selected_breeds: List[str] = None) -> bool:
    """
    Update breed (wood type) in stuffsets orderitems using ORDERS_ITEMS_SETPARAMS table
    """
    print("🔧" + "=" * 79)
    print("🔧 STARTING STUFFSETS BREED UPDATE PROCESS")
    print(f"🔧 Order ID: {order_id}")
    print(f"🔧 Breed Code: {breed_code}")
    print(f"🔧 Selected Breeds: {selected_breeds}")
    print("🔧" + "=" * 79)
    
    try:
        con = get_db_connection()
        cur = con.cursor()
        
        # Build SQL with optional filter for selected breeds
        if selected_breeds:
            # Create placeholders for IN clause
            placeholders = ",".join(["?" for _ in selected_breeds])
            breed_filter = f"""
            AND oisp.ID IN (
                SELECT oisp3.ID
                FROM ORDERS_ITEMS_SETPARAMS oisp3
                JOIN ENUM_ITEMS ei3 ON ei3.ID = oisp3.ENUMVALUEID
                WHERE ei3.CODE IN ({placeholders})
                AND oisp3.PARAMID IN (SELECT sp.ID FROM STRUCTS_PARAMS sp WHERE sp.NAME LIKE '%Wood%')
            )"""
        else:
            breed_filter = ""
        
        sql = f"""
        UPDATE ORDERS_ITEMS_SETPARAMS oisp
        SET oisp.ENUMVALUEID = (
            SELECT ei2.ID
            FROM (
                SELECT ei.TYPEID
                FROM ORDERS_ITEMS_SETPARAMS oisp2
                JOIN ENUM_ITEMS ei ON ei.ID = oisp2.ENUMVALUEID
                WHERE oisp2.ID = oisp.ID
            ) t
            JOIN ENUM_ITEMS ei2 ON ei2.TYPEID = t.TYPEID
            WHERE LOWER(TRIM(ei2.CODE)) LIKE ?
        )
        WHERE (
            oisp.ID IN (
                SELECT oisp2.ID
                FROM ORDERS o2
                JOIN ORDERS_ITEMS oi2 ON oi2.ORDERID = o2.ID
                JOIN ORDERS_ITEMS_SETPARAMS oisp2 ON oisp2.ORDERITEMID = oi2.ID
                WHERE o2.ID = ?
                AND oi2.STUFFSETID IS NOT NULL
            )
        )
        AND (
            oisp.PARAMID IN (
                SELECT sp.ID 
                FROM STRUCTS_PARAMS sp 
                WHERE sp.NAME LIKE '%Wood%'
            )
        )
        {breed_filter}
        """
        
        # Prepare parameters
        breed_param = f"{breed_code.lower()}"
        params = [breed_param, order_id]
        if selected_breeds:
            params.extend(selected_breeds)
        params = tuple(params)
        
        print(f"🔧 Original breed_code: '{breed_code}'")
        print(f"🔧 Lowercased: '{breed_code.lower()}'")
        print(f"🔧 With wildcards: '{breed_param}'")
        print(f"🔧 Final parameters: {params}")
        print(f"🔧 Parameter types: {[type(p).__name__ for p in params]}")
        
        print("🔧 About to execute UPDATE query for stuffsets orderitems...")
        cur.execute(sql, params)
        
        # Get the number of affected rows
        affected_rows = cur.rowcount
        
        # Commit the transaction
        con.commit()
        
        cur.close()
        con.close()
        
        print(f"✅ Stuffsets breed updated successfully for order {order_id}")
        print(f"   Affected rows: {affected_rows}")
        print("🔧" + "=" * 79)
        return True
        
    except Exception as e:
        print(f"❌ Error updating stuffsets breed: {e}")
        print("🔧" + "=" * 79)
        return False


def get_stuffsets_breeds_in_order(order_id: int) -> List[Dict[str, Any]]:
    """Get breeds currently used in stuffsets orderitems from real database"""
    try:
        con = get_db_connection()
        cur = con.cursor()
        
        sql = """
        SELECT DISTINCT ei.CODE as BREED_CODE                                
        FROM ORDERS_ITEMS_SETPARAMS oisp
        JOIN ENUM_ITEMS ei ON ei.ID = oisp.ENUMVALUEID
        WHERE (oisp.ID IN 
            (SELECT oisp2.ID
            FROM ORDERS o2
            JOIN ORDERS_ITEMS oi2 ON oi2.ORDERID = o2.ID
            JOIN ORDERS_ITEMS_SETPARAMS oisp2 ON oisp2.ORDERITEMID = oi2.ID
            WHERE o2.ID = ?
            AND oi2.STUFFSETID IS NOT NULL))
        AND (oisp.PARAMID IN (SELECT sp.ID FROM STRUCTS_PARAMS sp WHERE sp.NAME LIKE '%Wood%'))
        ORDER BY ei.CODE
        """
        cur.execute(sql, (order_id,))
        rows = cur.fetchall()
        
        result = []
        for row in rows:
            result.append({
                "BREED_CODE": row[0]
            })
        
        cur.close()
        con.close()
        
        if ENABLE_LOGGING:
            print(f"✅ Получено {len(result)} пород дерева для stuffsets в заказе {order_id}")
            
        return result
        
    except Exception as e:
        if ENABLE_LOGGING:
            print(f"❌ Ошибка получения пород дерева для stuffsets в заказе {order_id}: {e}")
        raise


def get_adds_breeds_in_order(order_id: int) -> List[Dict[str, Any]]:
    """Get breeds currently used in adds (ORDERS_ITEMS_ADDS) from real database"""
    try:
        con = get_db_connection()
        cur = con.cursor()
        
        sql = """
        SELECT DISTINCT ei.CODE as BREED_CODE                                
        FROM ORDERS_ITEMS_ADDS_SETPARAMS oiasp
        JOIN ENUM_ITEMS ei ON ei.ID = oiasp.ENUMVALUEID
        WHERE (oiasp.ID IN 
            (SELECT oiasp2.ID
            FROM ORDERS o2
            JOIN ORDERS_ITEMS oi2 ON oi2.ORDERID = o2.ID
            JOIN ORDERS_ITEMS_ADDS oia2 ON oia2.ORDERITEMID = oi2.ID
            JOIN ORDERS_ITEMS_ADDS_SETPARAMS oiasp2 ON oiasp2.ORDERITEMADDID = oia2.ID
            WHERE o2.ID = ?))
        AND (oiasp.PARAMID IN (SELECT sp.ID FROM STRUCTS_PARAMS sp WHERE sp.NAME LIKE '%Wood%'))
        ORDER BY ei.CODE
        """
        cur.execute(sql, (order_id,))
        rows = cur.fetchall()
        
        result = []
        for row in rows:
            result.append({
                "BREED_CODE": row[0]
            })
        
        cur.close()
        con.close()
        
        if ENABLE_LOGGING:
            print(f"✅ Получено {len(result)} пород дерева для дополнений в заказе {order_id}")
            
        return result
        
    except Exception as e:
        if ENABLE_LOGGING:
            print(f"❌ Ошибка получения пород дерева для дополнений в заказе {order_id}: {e}")
        raise


def get_stuffsets_colors_in_order(order_id: int) -> List[Dict[str, Any]]:
    """Get colors currently used in stuffsets orderitems from real database"""
    try:
        con = get_db_connection()
        cur = con.cursor()
        
        sql = """
        SELECT DISTINCT c.TITLE as COLOR_TITLE                                
        FROM ORDERS_ITEMS_SETPARAMS oisp
        JOIN COLORS c ON c.COLORID = oisp.COLORVALUEID
        WHERE (oisp.ID IN 
            (SELECT oisp2.ID
            FROM ORDERS o2
            JOIN ORDERS_ITEMS oi2 ON oi2.ORDERID = o2.ID
            JOIN ORDERS_ITEMS_SETPARAMS oisp2 ON oisp2.ORDERITEMID = oi2.ID
            WHERE o2.ID = ?
            AND oi2.STUFFSETID IS NOT NULL))
        AND (oisp.PARAMID IN (SELECT sp.ID FROM STRUCTS_PARAMS sp WHERE sp.PARAMTYPE = 3))
        ORDER BY c.TITLE
        """
        cur.execute(sql, (order_id,))
        rows = cur.fetchall()
        
        result = []
        for row in rows:
            result.append({
                "COLOR_TITLE": row[0]
            })
        
        cur.close()
        con.close()
        
        if ENABLE_LOGGING:
            print(f"✅ Получено {len(result)} цветов для stuffsets в заказе {order_id}")
            
        return result
        
    except Exception as e:
        if ENABLE_LOGGING:
            print(f"❌ Ошибка получения цветов для stuffsets в заказе {order_id}: {e}")
        raise


def update_color_in_stuffsets_orderitems(order_id: int, new_color: str, new_colorgroup: str, old_colors: List[str]) -> bool:
    """
    Update color in stuffsets orderitems using ORDERS_ITEMS_SETPARAMS table
    """
    print("🔧" + "=" * 79)
    print("🔧 STARTING STUFFSETS COLOR UPDATE PROCESS")
    print(f"🔧 Order ID: {order_id}")
    print(f"🔧 New Color: {new_color}")
    print(f"🔧 New Color Group: {new_colorgroup}")
    print(f"🔧 Selected Old Colors: {old_colors}")
    print("🔧" + "=" * 79)
    
    try:
        con = get_db_connection()
        cur = con.cursor()
        
        # Build SQL with filter for selected old colors
        if old_colors:
            # Create placeholders for IN clause
            placeholders = ",".join(["?" for _ in old_colors])
            color_filter = f"""
            AND oisp.ID IN (
                SELECT oisp3.ID
                FROM ORDERS_ITEMS_SETPARAMS oisp3
                JOIN COLORS c3 ON c3.COLORID = oisp3.COLORVALUEID
                WHERE c3.TITLE IN ({placeholders})
                AND oisp3.PARAMID IN (SELECT sp.ID FROM STRUCTS_PARAMS sp WHERE sp.PARAMTYPE = 3)
            )"""
        else:
            color_filter = ""
        
        sql = f"""
        UPDATE ORDERS_ITEMS_SETPARAMS oisp
        SET oisp.COLORVALUEID = (
            SELECT FIRST 1 c.COLORID
            FROM COLORS c
            JOIN COLORGROUP cg ON cg.GROUPID = c.GROUPID
            WHERE c.TITLE = ?
            AND cg.TITLE = ?
        )
        WHERE (
            oisp.ID IN (
                SELECT oisp2.ID
                FROM ORDERS o2
                JOIN ORDERS_ITEMS oi2 ON oi2.ORDERID = o2.ID
                JOIN ORDERS_ITEMS_SETPARAMS oisp2 ON oisp2.ORDERITEMID = oi2.ID
                WHERE o2.ID = ?
                AND oi2.STUFFSETID IS NOT NULL
            )
        )
        AND (
            oisp.PARAMID IN (
                SELECT sp.ID 
                FROM STRUCTS_PARAMS sp 
                WHERE sp.PARAMTYPE = 3
            )
        )
        {color_filter}
        """
        
        # Prepare parameters: new_color, new_colorgroup, order_id, then old_colors
        params = [new_color, new_colorgroup, order_id]
        if old_colors:
            params.extend(old_colors)
        params = tuple(params)
        
        print(f"🔧 New color: '{new_color}'")
        print(f"🔧 New color group: '{new_colorgroup}'")
        print(f"🔧 Final parameters: {params}")
        print(f"🔧 Parameter types: {[type(p).__name__ for p in params]}")
        
        print("🔧 About to execute UPDATE query for stuffsets colors...")
        cur.execute(sql, params)
        
        # Get the number of affected rows
        affected_rows = cur.rowcount
        
        # Commit the transaction
        con.commit()
        
        cur.close()
        con.close()
        
        print(f"✅ Stuffsets colors updated successfully for order {order_id}")
        print(f"   Affected rows: {affected_rows}")
        print("🔧" + "=" * 79)
        return True
        
    except Exception as e:
        print(f"❌ Error updating stuffsets colors: {e}")
        print("🔧" + "=" * 79)
        return False


def test_connection() -> bool:
    """Test database connection"""
    try:
        con = get_db_connection()
        cur = con.cursor()
        
        sql = "SELECT 1 FROM RDB$DATABASE"
        cur.execute(sql)
        result = cur.fetchone()
        
        cur.close()
        con.close()
        
        if ENABLE_LOGGING:
            print("✅ Database connection test successful")
            
        return True
        
    except Exception as e:
        if ENABLE_LOGGING:
            print(f"❌ Database connection test failed: {e}")
        return False
