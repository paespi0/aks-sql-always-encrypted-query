import os
import logging
# from azure.identity import DefaultAzureCredential
from azure.identity import ManagedIdentityCredential
from azure.keyvault.secrets import SecretClient
import pyodbc

# Set up logging
logging.basicConfig(level=logging.INFO)

# Specify the clientId of the user-assigned managed identity; mid: nbhAKSCluster-agentpool (AKV Admin)
user_assigned_identity_client_id = '<managed identity client id>'

# Initialize the Azure Key Vault SecretClient
key_vault_name = "<kvname>"
kv_uri = f"<kv uri>"
# credential = DefaultAzureCredential()
credential = ManagedIdentityCredential(client_id=user_assigned_identity_client_id)
client = SecretClient(vault_url=kv_uri, credential=credential)

# Using mID: nbhAKSCluster-agentpool retrieve the SQL connection string and password from Azure Key Vault
# connection string stored in AKV: Uid is admin user for SQL and sql pw is retrieved from AKV
# app registration (keystoreprincipalid): nbhapp - access is KV Admin, KV Crypto Officer and KV Secrets Officer
# use brackets for app reg client and secret values if either contain special characters
# Server=<SERVERNAME>.database.windows.net;Database=<DBNAME>;Uid=<UID>;ColumnEncryption=Enabled;Encrypt=yes;TrustServerCertificate=yes;KeyStoreAuthentication=KeyVaultClientSecret;KeyStorePrincipalId={app reg client};KeyStoreSecret={app reg secret value};
connection_string_secret_name = "sql-connection-string"
password_secret_name = "sql-password"

try:
    connection_string = client.get_secret(connection_string_secret_name).value
    password = client.get_secret(password_secret_name).value
except Exception as e:
    logging.error("An error occurred while retrieving secrets:", e)
    exit(1)

# Define the ODBC driver
driver = '{ODBC Driver 18 for SQL Server}'

# Complete the connection string with the password and the driver
conn_str = f"DRIVER={driver};" + connection_string + f"PWD={password}"


# Connect to the Azure SQL Database and query the encrypted columns
try:
    with pyodbc.connect(conn_str) as conn:
        with conn.cursor() as cursor:
            # Specify the query to select from the encrypted columns
            cursor.execute("SELECT SSN FROM NBH.Employees")
            row = cursor.fetchone()
            if row is None:
                print("No data returned from query")
            with open('/app/output.txt', 'w') as f:  # Open the file in write mode
                while row:
                    print("Writing row to file:", row)
                    f.write(str(row) + '\n')  # Write the row to the file
                    row = cursor.fetchone()
except pyodbc.Error as e:
    print("An error occurred:", e)

# At the end of app.py
import time
while True:
    time.sleep(60)  # Sleeps for 60 seconds
