import ldap
import os
import boto3
import random
import string

from base64 import b64decode

#Variables
url=os.environ['url']
domain_base_dn=os.environ['domain_base_dn']
user=os.environ['user']


def lambda_handler(event, context):

    ENCRYPTED=os.environ['pw']
    pw='DYzl64qFekMP'
    # pw=boto3.client('kms').decrypt(
    #     CiphertextBlob=b64decode(ENCRYPTED),
    #     EncryptionContext={'LambdaFunctionName': os.environ['AWS_LAMBDA_FUNCTION_NAME']},
    #     )['Plaintext']    
    
    print(user)
    print(pw)
    
    #Set up LDAP connection
    print('Entering handler')
    ldap.set_option(ldap.OPT_X_TLS_REQUIRE_CERT, ldap.OPT_X_TLS_NEVER)
    con = ldap.initialize(url)
    print('ldap initialized')
    con.set_option(ldap.OPT_REFERRALS, 0)
    con.bind_s(user,pw)
    print('connection bound')
    a
    results = con.search_ext_s(domain_base_dn,ldap.SCOPE_SUBTREE,"sAMAccountName=" + slotUserID,attrlist=['monthStarted', 'birthDate', 'distinguishedName','telephoneNumber'])
    print(results)
    
    # Add in conditional logic for Password Reset/MFA
    # birthdate = results[0][1]["birthDate"][0]
    # monthStarted = results[0][1]["monthStarted"][0]
    # phoneNumber = results[0][1]["telephoneNumber"][0]
    # slotBirthDate = event["currentIntent"]["slots"]["DOB"]
    # slotMonth = event["currentIntent"]["slots"]["MonthStarted"]

    # Reset Password
    # if((birthdate == slotBirthDate) and (monthStarted == slotMonth)):
    new_password = ''.join(random.choice(string.ascii_letters + string.digits + string.punctuation) for _ in range(10))
    new_password_utf = new_password.encode('utf-8')
    # new_password = '\"' + new_password + '\"'
    # unicode_pass = new_password.encode('iso-8859-1')
    # password_value = unicode_pass.encode('utf-16-le')
    add_pass = [(ldap.MOD_REPLACE, 'unicodePwd', [new_password_utf])]
    con.modify_s(results[0][1]["distinguishedName"][0],add_pass)        
    # sns = boto3.client('sns')
    # sns.publish(PhoneNumber=phoneNumber, Message='Your new password is ' + new_password )
    print(new_password)
    endData = {
        "dialogAction": {
            "type": "Close",
                "fulfillmentState": "Fulfilled",
                "message": {
                    "contentType": "PlainText",
                    "content": "Your password has been reset and sent to your mobile."
                }
            }
        }
    con.unbind()
    return endData