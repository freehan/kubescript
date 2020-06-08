#!/bin/bash
VPN_IP=${VPN ENDPOINT} # local VPN gateway
CIDR_RANGE=${LOCAL CIDR RANGEs} # CIDR range from local environment
PEER_VPN_IP=${REMOTE_VPN_IP} # e.g. Cloud vpn ip
PEER_CIDR_RANGE=${REMOTE_CIDR_RANGEs} # e.g.10.128.0.0/20,10.48.0.0/14,10.177.0.0/20,10.138.0.0/20,10.148.0.0/24
echo 1 > /proc/sys/net/ipv4/ip_forward
apt-get update -yq && sudo apt-get install strongswan -y
cat > /etc/ipsec.secrets <<EOF
$VPN_IP %any : PSK "${VPN PRIVATE KEY}". # e.g. AAAbAbb7AAbA3bAbAAbbAA9bAAA6BBB
EOF
cat > /etc/ipsec.conf <<EOF
conn c-2-e
  authby=psk
  auto=start
  dpdaction=hold
  esp=aes128-sha1-modp3072!
  forceencaps=yes
  ike=aes128-sha1-modp2048!
  keyexchange=ikev2
  mobike=no
  type=tunnel
  leftid=$VPN_IP
  leftsubnet=$CIDR_RANGE
  leftauth=psk
  leftikeport=4500
  right=$PEER_VPN_IP
  rightsubnet=$PEER_CIDR_RANGE
  rightauth=psk
  rightikeport=4500
  lifetime=3h
  ikelifetime=10h
  keyingtries=%forever
EOF
service strongswan restart
