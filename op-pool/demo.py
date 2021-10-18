from algosdk import *
from algosdk.v2client import algod
from algosdk.v2client.models import DryrunSource, DryrunRequest
from algosdk.future.transaction import *
from sandbox import get_accounts
import base64
import os


token = "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
url = "http://localhost:4001"

_verify = b"A"*64 # 64 bytes since thats the length of a valid signature

client = algod.AlgodClient(token, url)

def demo():
    # Create acct
    addr, pk = get_accounts()[0]
    print("Using {}".format(addr))

    # Create app
    app_id = create_app(addr, pk)
    print("Created App with id: {}".format(app_id))

    # App call with 1 txn
    try:
        sp = client.suggested_params()
        single = [
            get_app_call(addr, sp, app_id, [_verify, _verify])
        ]
        signed_group = [txn.sign(pk) for txn in single]

        write_dryrun(signed_group, "expect-fail", addr)

        txid = client.send_transactions(signed_group)
        print("Sending single transaction: {}".format(txid))

        result = wait_for_confirmation(client, txid, 4)
        print("Result from single: {}".format(result))
    except Exception as e:
        print("Failed to call single app call: {}".format(e))
        

    # App call with 3 txns
    # Only the first transaction passes the verify args, 
    # the others are used increase pooled opcode budget
    try :
        sp = client.suggested_params()
        pooled_group = assign_group_id([
            get_app_call(addr, sp, app_id, [_verify, _verify]), 
            get_app_call(addr, sp, app_id, []),
            get_app_call(addr, sp, app_id, [])
        ])

        signed_group = [txn.sign(pk) for txn in pooled_group]

        write_dryrun(signed_group, "expect-succeed", addr)

        txid = client.send_transactions(signed_group)
        print("Sending grouped transaction: {}".format(txid))

        result = wait_for_confirmation(client, txid, 4)
        print("Success! Confirmed in round: {}".format(result['confirmed-round']))
    except Exception as e:
        print("Failed to call grouped app call: {}".format(e))


def write_dryrun(signed_txn, name, addr):
    path = os.path.dirname(os.path.abspath(__file__))
    # Read in approval teal source
    src = open(os.path.join(path,'approval.teal')).read()

    # Add source
    sources = [DryrunSource(field_name="approv", source=src)]

    # Create request
    drr = DryrunRequest(txns=signed_txn, sources=sources, accounts=[addr])

    # write drr
    file_path = os.path.join(path, name+".msgp")
    data = encoding.msgpack_encode(drr)
    data = base64.b64encode(data.encode())
    with open(file_path, "wb") as f:
        f.write(data)

    print("Created Dryrun file at {} - goto chrome://inspect".format(file_path))

    print("""
      START debugging session
      either use from terminal in this folder or new terminal in same folder
      `tealdbg debug approval.teal --dryrun-req {}.msgp`
    """.format(name))

def get_app_call(addr, sp, app_id, args):
    return ApplicationCallTxn(
            addr, sp, app_id, 
            OnComplete.NoOpOC, 
            app_args=args,
            note=os.urandom(4) #Add random note field to prevent dupe transaction ids
    )

def create_app(addr, pk):

    # Get suggested params from network 
    sp = client.suggested_params()

    path = os.path.dirname(os.path.abspath(__file__))

    # Read in approval teal source && compile
    approval = open(os.path.join(path,'approval.teal')).read()
    app_result = client.compile(approval)
    app_bytes = base64.b64decode(app_result['result'])
    
    # Read in clear teal source && compile 
    clear = open(os.path.join(path,'clear.teal')).read()
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
