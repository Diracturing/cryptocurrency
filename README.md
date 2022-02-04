# A bitcoin based cryptocurrency from scratch
Mastering bitcoin by Andreas M. Antonopoulos and https://developer.bitcoin.org/reference/index.html was used as a reference.


## How to run
It was tested using several virtual ubuntu servers.

In Fullnode.py, change initIp to the server which will run the first full node. The first full node also has to include a single arbitary argument (python3 Fullnode.py "anything"). The next full nodes should not include any argument. All nodes have to start before any node have mined a block. 

## What it does
It starts by connecting all nodes to eachother.
Then when a node wins the mining puzzle it will add the block to the blockchain and send it to other nodes. The block will contain newly mined coins connected to its public key. A simple transaction was tested but basically a wallet has to be implemented to make it easier to send transactions.
