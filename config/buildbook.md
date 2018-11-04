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
1. Open a Terminal and add the repository to your Yum install.
`# yum install -y https://centos7.iuscommunity.org/ius-release.rpm`
2. Update Yum to finish adding the repository.
`# yum update`
3. Download and install Python
`# yum install -y python36u python36u-libs python36u-devel python36u-pip`

## Installing eth_node_client

1. git clone https://github.com/ICOFactory/eth_node_client.git
2. UPDATE THE config.json FILE
3. Install a service into systemd using the warden.service example,
best way I know how to do this now is to use absolute filepaths for the
log and config files on each server. When you start it will hang, CTRL-C to exit the
process and systemd will restart it in the background. Maybe someday it will be better.
4. Verify on the ERCMaster Ethereum Network Panel that traffic is being received.