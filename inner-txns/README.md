AVM 1.0 Inner Transactions Demo
------------------------

This demo is meant to illustrate how you can use the new Inner Transaction functionality in a Smart Contract.

The Smart Contracts are written in [PyTeal](https://developer.algorand.org/docs/get-details/dapps/pyteal/) in `app.py` and are compiled to TEAL. The only function it performs is that on a call from the application creator, it creates a new ASA with the name specified in the first argument and unitname specified in the second argument and total supply as the third argument. 

The `demo.py` file contains logic to deploy the Application from the Smart Contracts on chain, then call the application,  then read the transaction pool to see the asset id of the created asset.


Technical Details
-----------------

InnerTransaction are created and submitted as part of the Smart Contract execution. 

    1. Begin construction of inner transaction
    2. Set appropriate fields
    3. Submit transaction

Currently the inner transactions are limited to: PaymentTx, AssetTransferTx, AssetConfigTx, AssetFreezeTx.

Inner transactions default to the Application Address as the sender but may be called on behalf of a sender that has been Rekeyed to the Application Account.

Up to 16 inner transactions may be created and submitted.
