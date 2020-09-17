import boto3
import ldap3
import os
from base64 import b64decode

SERVER=os.environ['SERVER']
BASEDN=os.environ['DOMAIN_BASE_DN']
USER = os.environ['USER']
ENCRYPTED = os.environ['PW']
PW = boto3.client('kms').decrypt(
    CiphertextBlob=b64decode(ENCRYPTED),
    EncryptionContext={'LambdaFunctionName': os.environ['AWS_LAMBDA_FUNCTION_NAME']}
)['Plaintext'].decode('utf-8')

def lambda_handler(event, context):
    
    slotUserID = event["currentIntent"]["slots"]["UserID"]
    RESET_USER=slotUserID+"@corp.example.com"
    SEARCHFILTER='(&(userPrincipalName='+RESET_USER+')(objectClass=person))'

    USER_DN=""
    USER_CN=""

    ldap_server = ldap3.Server(SERVER, get_info=ldap3.ALL)
    conn = ldap3.Connection(ldap_server, USER, PW, auto_bind=True)
    conn.search(search_base = BASEDN,
             search_filter = SEARCHFILTER,
             search_scope = ldap3.SUBTREE,
             attributes = ['cn', 'givenName', 'userPrincipalName'],
             paged_size = 5)

    for entry in conn.response:
        print(entry)
        if entry.get("dn") and entry.get("attributes"):
            if entry.get("attributes").get("userPrincipalName"):
                if entry.get("attributes").get("userPrincipalName") == RESET_USER:
                    USER_DN=entry.get("dn")
                    USER_CN=entry.get("attributes").get("cn")
    
    NEWPWD = 'nIzF3Vi5HV3N'
    
    print("Found user:", USER_CN)
    print(USER_DN)
    result = ldap3.extend.microsoft.modifyPassword.ad_modify_password(conn, USER_DN, NEWPWD, PW,  controls=None)
    print(result)
    
    return {
        
        'dialogAction' : {
            "type": "Close",
            "fulfillmentState": "Fulfilled",
            "message": {
              "contentType": "PlainText",
              "content": "Your password has been reset to the default value"
            }
        }
    } 
