# bind2samba: A converter for BIND zone files to samba-tool invocations

## About

This tool assits when converting an old zone file to a DNS zone run by a Samba
Directory Controller. It can read the zone file and turn its contents into
invocations of `samba-tool dns add ...`. It understands A, AAAA, CNAME, and MX
records. In addtion, one can give subnets in CIDR notation; if A/AAAA records
match the subnets given, reverse PTR records are also created.

## Invocations

Suppose you have the following zone file:

    $ORIGIN example.com.
    $TTL    3d

    example.com. IN      SOA     ns1.example.com. hostmaster.example.com.
    (
            2018022301                  ; Serial
            1h                          ; Refresh
            15m                         ; Retry
            2w                          ; Expire
            1h)                         ; Negative TTL

    example.com.     IN      NS      galathea-bond0.example.com
    example.com.     IN      MX      10 mx


    ;
    ; Local, trusted network:
    ;

    charon          IN      A       172.16.5.1
    charon          IN      AAAA    2001:170:1243:1::1

You can feed it directly to bind2samba:

    % bind2samba example.com.db
    I would run the following commands:
    samba-tool dns add localhost example.com @ MX mx.example.com 10
    samba-tool dns add localhost example.com charon A 172.16.5.1
    samba-tool dns add localhost example.com charon AAAA 2001:170:1243:1::1

Supplying subnets will create PTR records, too:

    % bind2samba \
        --ipv4-subnet=172.16.0.0/12 \
        --ipv6-subnet=2001:170:1243::/48 \
        minimal-example.com.db
    I would run the following commands:
    samba-tool dns add localhost example.com @ MX mx.example.com 10
    samba-tool dns add localhost example.com charon A 172.16.5.1
    samba-tool dns add localhost 16.172.in-addr.arpa 1.5.16.172.in-addr.arpa PTR charon.example.com
    samba-tool dns add localhost example.com charon AAAA 2001:170:1243:1::1
    samba-tool dns add localhost 3.4.2.1.0.7.1.0.1.0.0.2.ip6.arpa 1.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.1.0.0.0.3.4.2.1.0.7.1.0.1.0.0.2.ip6.arpa PTR charon.example.com

Multiple subnets can be given, the best matching will then be used. 

The tool can also provide you with single commands without seeing a full SOA
record, because `--zone example.com` is also a command line option. Then, you
can simply feed records on stdin to it:

    echo 'charon IN A 172.16.5.1' | ../src/bind2samba --zone=example.com

In general, running `bind2samba --help` gives the full list of arguments,
as any well-behaved tool should.

## Reporting bugs, feature wishes, and contributing

The project's website is https://github.com/eveith/bind2samba, but
bug reports, feature wishes, or patches can also just e-mailed to
<eveith+bind2samba@binericien.org>.
