Despite the fact that the Ethereum node client itself is dependency free,
at this time it relies on a portion of the https://github.com/ethereum/eth_abi.git project repository
to process contract functions.

This project has some complicated dependencies that are recorded in the eth_abi_requirements.txt file.

The best way to get eth_abi working after cloning the repository is creating your own virtual Python 3 environment,
which eth_abi depends upon, and using pip to satisfy the requirements using

pip install -r eth_abi_requirements.txt

It is a short term tactical goal to reduce dependency on Python 3 as much as possible to accelerate the deployment of
nodes until Python3 is completely adopted.