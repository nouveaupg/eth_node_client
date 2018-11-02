# eth_node_client setup

#### Dependencies (apt-get,yum)
1. install golang
2. install git

Create user ethereum
Switch to user ethereum

`$ git clone https://github.com/ethereum/go-ethereum.git`

`$ cd go-ethereum`
`$ make geth`

Switch to root
Install config/geth.service into systemd

`# systemctl enable geth.service`


## CentOS 7

CentOS 7 comes with Python 2.7, you can query the API with
scripts/sync_rpc_client2.py in the repository but otherwise you
need to install Python 3

`# yum install centos-release-scl`

