# DNS

This is a high-level explanation of DNS.

## Forward lookup of `www.stellar.org`

Prereq: A client computer typically has DNS servers configured as part of its internet connection.

1. The computer hits its configured DNS server. Name resolutions are typically cached.
    * If there is a cache hit, the DNS server returns the answer. Done.
    * Otherwise, the lookup continues
2. The edge DNS server first hits the root DNS server (`.`), which returns the DNS server for the next level down (`.org`)
3. This continues recursively until the name server for the lowest level is returned. (`www.stellar.org`)
4. the edge DNS server queries this server to obtain the final IP address, returns it, and caches the result.

## Registration

Registration is done through a registrar. Let's assume you're registering `stellar.org`. The registrar you need is one that has a relationship with the operator of `.org`. The registrar contacts the operator of `.org` and tell the operator to use the registrar's name server for `stellar.org`. The registrar then points `stellar.org` to the IP address you specify.
