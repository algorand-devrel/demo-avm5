from algosdk import *
from algosdk.v2client import algod
from algosdk.future.transaction import *
from sandbox import get_accounts
import base64
import os

client = algod.AlgodClient("aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa", "http://localhost:4001")

def demo():
    # Create acct
    addr, pk = get_accounts()[0]
    print("Using {}".format(addr))

    # Create app
    #app_id = 5
    app_id = create_app(addr, pk)
    print("Created App with id: {}".format(app_id))

    # App call with 1 txn
    try:
        sp = client.suggested_params()
        single = assign_group_id([
            get_app_call(addr, sp, app_id, [b"verify", b"A"*64])
        ])
        signed_group = [txn.sign(pk) for txn in single]
        txid = client.send_transactions(signed_group)
        print("Sending single transaction: {}".format(txid))

        result = wait_for_confirmation(client, txid, 4)
        print("Result from single: {}".format(result))
    except Exception as e:
        print("Failed to call single app call: {}".format(e))
        

    # App call with 3 txns
    try :
        sp = client.suggested_params()
        pooled_group = assign_group_id([
            get_app_call(addr, sp, app_id, [b"verify", b"A"*64]), 
            get_app_call(addr, sp, app_id, []),
            get_app_call(addr, sp, app_id, [])
        ])

        signed_group = [txn.sign(pk) for txn in pooled_group]
        txid = client.send_transactions(signed_group)
        print("Sending grouped transaction: {}".format(txid))

        result = wait_for_confirmation(client, txid, 4)
        print("Result from grouped: {}".format(result))
    except Exception as e:
        print("Failed to call grouped app call: {}".format(e))



def get_app_call(addr, sp, app_id, args):
    return ApplicationCallTxn(
            addr, sp, app_id, 
            OnComplete.NoOpOC, 
            app_args=args,
            note=os.urandom(4)
    )

def create_app(addr, pk):

    # Get suggested params from network 
    sp = client.suggested_params()

    # Read in approval teal source && compile
    approval = open('approval.teal').read()
    app_result = client.compile(approval)
    app_bytes = base64.b64decode(app_result['result'])
    
    # Read in clear teal source && compile 
    clear = open('clear.teal').read()
    clear_result = client.compile(clear)
    clear_bytes = base64.b64decode(clear_result['result'])

    # We dont need no stinkin storage
    schema = StateSchema(0, 0)

    # Create the transaction
    create_txn = ApplicationCreateTxn(addr, sp, 0, app_bytes, clear_bytes, schema, schema)

    # Sign it
    signed_txn = create_txn.sign(pk)

    # Ship it
    txid = client.send_transaction(signed_txn)
    
    # Wait for the result so we can return the app id
    result = wait_for_confirmation(client, txid, 4)

    return result['application-index']

if __name__ == "__main__":
    demo()
