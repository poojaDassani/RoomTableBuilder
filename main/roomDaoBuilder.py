import inspect
import os
import re

# Define the template for the DAO interface
DAO_TEMPLATE = """package com.test.test.dao

import androidx.room.*
import com.test.test.models.{entity_name}

    
@Dao
interface {entity_name}Dao {{

    @Insert
    suspend fun insert({entity_namePlural}: List<{entity_name}>): List<Long>

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertOrUpdate({entity_name_lower}: {entity_name})

    @Insert(onConflict = OnConflictStrategy.IGNORE)
    suspend fun insertIfNotExists({entity_name_lower}: {entity_name})

    @Update
    suspend fun update({entity_name_lower}: {entity_name})

    @Delete
    suspend fun delete({entity_name_lower}: {entity_name})

    @Query("SELECT * FROM {table_name}")
    fun getAll{entity_name}(): List<{entity_name}>

    @Query("DELETE FROM {table_name}")
    suspend fun deleteAll()

}}
"""


def generate_dao_files(ENTITY_DIR,OUTPUT_DIR):
    # Get all the entity classes in the directory
    entity_files = [f for f in os.listdir(ENTITY_DIR) if f.endswith(".kt")]

    # Process each entity class
    for file_name in entity_files:
    # Extract the entity name from the file name
        entity_name = os.path.splitext(file_name)[0]

    # Read the entity file
        with open(os.path.join(ENTITY_DIR, file_name), "r") as file:
            entity_code = file.read()

    # Extract the table name from the entity class using regular expression
        table_name_match = re.search("@Entity\(tableName = \"(.*?)\"\)", entity_code)
        if table_name_match:
            table_name = table_name_match.group(1)
        else:
            table_name = entity_name.lower()

# Generate the DAO interface code based on the template
        dao_code = DAO_TEMPLATE.format(
            entity_name=entity_name,
            entity_namePlural=entity_name + "s",
            table_name=table_name,
            entity_name_lower = entity_name.lower()
        )


        if not os.path.exists(OUTPUT_DIR):
            os.makedirs(OUTPUT_DIR)

    # Write the DAO interface code to a file
        dao_file_name = entity_name + "Dao.kt"
        with open(os.path.join(OUTPUT_DIR, dao_file_name), "w") as file:
            file.write(dao_code)

        print(f"Generated DAO interface for {entity_name}")

    print("DAO generation completed!")
