# TMP Command Line Interface

A command line tool and reverse-engineering project to flush out a client for the Tether Management Protocol (TMP) and the Tether Discovery (?) Protocol (TDP), which are proprietary TP-Link protocols used in all of their modern devices.

<h1 style="color:red">CAUTION</h1>
<p style="color:red">
Using this protocol is <b><i>extremely dangerous</i></b> for your router. There is no documentation, and changing one thing can lead to bricking the router if a wrong character is entered.
</br></br>
I am not liable for any routers bricked as a result of this code. If you do brick your router, use TFTP in uboot to reflash the firmware.
</br></br>
You have been warned.
</p>


```
usage: tmpcli.py [-h] [-p PAYLOAD] [-V VERSION] [-B BUSINESS_TYPE] [-T PACKET_TYPE] [-o OPCODE] [-t] [-v]
                 server port

positional arguments:
  server                Server IP
  port                  Server port

optional arguments:
  -h, --help            show this help message and exit
  -p PAYLOAD, --payload PAYLOAD
                        Payload to send
  -V VERSION, --version VERSION
                        TMP version
  -B BUSINESS_TYPE, --business-type BUSINESS_TYPE
                        Who knows what this is, @tplink
  -T PACKET_TYPE, --packet-type PACKET_TYPE
                        Toggle TDP or OneMesh
  -o OPCODE, --opcode OPCODE
                        TMP/TDP opcode
  -t, --tdp             Send payload over TDP instead of TMP
  -v, --verbose         Verbose mode - logging enabled
```

## Sending a TMP Packet

The relevant options for TMP are as follows:

```
  -p PAYLOAD, --payload PAYLOAD
                        Payload to send
  -V VERSION, --version VERSION
                        TMP version
  -o OPCODE, --opcode OPCODE
                        TMP/TDP opcode
  -B BUSINESS_TYPE, --business-type BUSINESS_TYPE
                        Who knows what this is, @tplink
```

### Example

Change the router PIN to `12345678`

```
./tmpcli.py -V 1 -B 2 -o 0x030d 127.0.0.1 20002 -p 12345678 -v
```

(See [port forwarding](#port-forwarding) for more details)

## Sending a TDP Packet

The relevant options for TDP are as follows:

```
  -p PAYLOAD, --payload PAYLOAD
                        Payload to send
  -V VERSION, --version VERSION
                        TMP version
  -T PACKET_TYPE, --packet-type PACKET_TYPE
                        Toggle TDP or OneMesh
  -o OPCODE, --opcode OPCODE
                        TMP/TDP opcode
  -t, --tdp             Send payload over TDP instead of TMP
```

### Example

Send a TDP packet version 1 to `192.168.0.1`.

```
./tmpcli.py -t 192.168.0.1 20002 -V 1 -T 1
```

## Port Forwarding

The TMP Server is listening on localhost. Thankfully, dropbear only disallows shell access, which means port forwarding is possible (this is how the Tether app manages the router).

```
ssh admin@192.168.0.1 -L 20002:127.0.0.1:20002 -N
```

The password is the same as the one for the web admin. You may need to specify the Cipher and Key specs in order to get SSH to make a connection. I leave that as an exercise for the user.

## References

1. [Pedro Ribeiro (@pedrib1337) and Radek Domanski (@RabbitPro)](https://www.thezdi.com/blog/2020/4/6/exploiting-the-tp-link-archer-c7-at-pwn2own-tokyo)
    - this blogpost was immensely helpful for the TdpPacket class. Thanks to Pedro and Radek.