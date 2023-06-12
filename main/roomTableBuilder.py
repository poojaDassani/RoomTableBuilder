import os
import re
import sqlite3
import roomDaoBuilder


ENTITY_DIR = None
def convert_to_camel_case(column_name):
    words = column_name.split('_')
    camel_case_words = [words[0].lower()] + [word.title() for word in words[1:]]
    return ''.join(camel_case_words)


def generate_entity_class(table_name, columns, indexes):
    entity_class = f"@Entity(tableName = \"{table_name}\")\n"
    entity_class += f"data class {convert_to_camel_case_table(table_name)} (\n"

    # column_names = [column[1] for column in columns]

    for i, column in enumerate(columns):
        column_name = column[1]
        column_type = column[2]
        nullable = column[3] == 1  # Check if the column is nullable

        if column_type == "INTEGER":
            column_type = "Int"
        elif column_type == "TEXT":
            column_type = "String"
        elif column_type == "REAL":
            column_type = "Double"

        camel_case_column_name = convert_to_camel_case(column_name)
        
        if column[5] == 1:  # Check if the column is a primary key
            entity_class += f"    @PrimaryKey(autoGenerate = true)\n"
            entity_class += f"    @ColumnInfo(name = \"{column_name}\")\n"
            entity_class += f"    val {camel_case_column_name}: {column_type}"

        elif nullable:
            entity_class += f"    @ColumnInfo(name = \"{column_name}\")\n"
            entity_class += f"    var {camel_case_column_name}: {column_type}? = null"
        else:
            entity_class += f"    @ColumnInfo(name = \"{column_name}\")\n"
            entity_class += f"    var {camel_case_column_name}: {column_type}"
            #comment the above line if have to assign default value to column and uncomment the below line
            #entity_class += f"    var {camel_case_column_name}: {column_type} = {get_default_value(column_type)}"


        if i < len(columns) - 1:
            entity_class += ","

        entity_class += "\n"

    # Specify indexes in database
    # for index in indexes:
    #     index_name = index[1]
    #     indexed_columns = str(index[2])
    #     index_columns = ', '.join([f"\"{convert_to_camel_case(column.strip())}\"" for column in indexed_columns.split(",")])
    #     index_column_names = ', '.join([f"\"{column}\"" for column in indexed_columns.split(",") if column in column_names])
    #     entity_class += f"\n    @Index(name = \"{index_name}\", value = [{index_columns}], unique = {index[3]}, ignoreNull = {index[4]}, columnNames = [{index_column_names}])"

    entity_class += "\n)\n"
    return entity_class

# Specify if any default value exists for column
# def get_default_value(column_type):
#     if "Int" in column_type:
#         return "0"
#     elif "Boolean" in column_type:
#         return "false"
#     elif "String" in column_type:
#         return "\"\""
#     else:
#         return "null"

def convert_to_camel_case_table(table_name):
    words = re.split(r"_", table_name)
    camel_case_name = "".join(word.capitalize() for word in words)
    return camel_case_name

def generate_entity_classes(database_file):
    connection = sqlite3.connect(database_file)
    cursor = connection.cursor()

    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    table_names = cursor.fetchall()

    script_directory = r"path\to\entity\classes"
    global ENTITY_DIR
    ENTITY_DIR = os.path.join(script_directory, "kotlin_files")
    if not os.path.exists(ENTITY_DIR):
        os.makedirs(ENTITY_DIR)

    for table_name in table_names:
        table_name = table_name[0]
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = cursor.fetchall()
        cursor.execute(f"PRAGMA index_list({table_name})")
        indexes = cursor.fetchall()
        entity_class = generate_entity_class(table_name, columns, indexes)

        # Write the entity class to a separate Kotlin file
        file_name = f"{convert_to_camel_case_table(table_name)}.kt"
        file_path = os.path.join(ENTITY_DIR, file_name)
        with open(file_path, "w") as file:
            file.write("package com.test.test.models\n\n")
            file.write("import androidx.room.Entity\n")
            file.write("import androidx.room.PrimaryKey\n")
            file.write("import androidx.room.ColumnInfo\n\n")
            file.write(entity_class)

    cursor.close()
    connection.close()

# Specify the path to your SQLite database file
database_file = r"path\to\db"

# Generate the Room entity classes as separate Kotlin files
generate_entity_classes(database_file)

# Output directory for DAO classes
OUTPUT_DIR = r"path\to\dao"
# Generate the Room entity classes DAO files
roomDaoBuilder.generate_dao_files(ENTITY_DIR, OUTPUT_DIR)