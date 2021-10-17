AVM 1.0 Opcode Budget Pooling demo
----------------------------------

This demo is meant to illustrate how you can use grouped AppCall transactions to provide a single AppCall with a greater cost budget during execution. 

The Smart Contracts are written in [PyTeal](https://developer.algorand.org/docs/get-details/dapps/pyteal/) available in `app.py` and are compiled to TEAL. During an AppCall the arguments are inspected to determine if it should try to execute the Ed25519Verify opcode. If no arguments are provided, we return success immediately, Otherwise the bytes in the arguments array are passed to the Ed25519Verify function. The results from the verification are popped since we don't actually care if they succeed in this case and we return success as long as the program doesn't fail from an opcode budget error.

The `demo.py` file contains logic to deploy the Application from the smart contracts on chain, then call the application. There are 2 attempts to call application, the first with a single AppCall transaction which should fail given the budget requirements (1900>700). The second attempt to call the application contains 3 AppCall transactions, with only the first triggering the Ed25519Verify function and is expected to return success since the budget is pooled across 3 transactions (1900<(3*700)).


Technical Details
----------------

Each opcode in a Smart Contract comes with an associated `cost` of execution, with some opcodes costing more than others depending on how computationally expensive they are to execute.  For example the Ed25519Verify opcode comes with a cost of 1900 since it is expensive to compute.  Smart contracts are currently limited to a budget of 700. This limitation allows the network to stay fast and efficient but it was often diffuclt to design around with a complex application.

Opcode Budget Pooling provides a way for developers to overcome this limitation at the cost of additional transaction submissions. 

An AppCall transaction may now be grouped with up to 15 other AppCall transactions allowing the opcode budget to be pooled. This means that instead of a cost budget of 700, with a group of 16 AppCall transactions a single AppCall is provided a budget of 16 * 700 or 11200!
