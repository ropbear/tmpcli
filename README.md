# tmpcli

A command line tool based on reverse-engineering the Tether Management Protocol server and client on TP-Link devices.

## ⚠️ Warning ⚠️

Using this protocol is **extremely dangerous** for your router. There is no documentation, and changing one thing can lead to bricking the router if a wrong character is entered.
I am not liable for any routers bricked as a result of this code. If you do brick your router, use TFTP in uboot to reflash the firmware.
You have been warned.

## Usage

```
usage: tmpcli.py [-h] [-p PAYLOAD] [-o OPCODE] [-v] host port

positional arguments:
  host                  Host IPv4
  port                  TCP port

options:
  -h, --help            show this help message and exit
  -p PAYLOAD, --payload PAYLOAD
                        Data to send
  -o OPCODE, --opcode OPCODE
                        TMP opcode
  -v, --verbose         Verbose mode - logging enabled
```
## Port Forwarding

The TMP Server is listening on localhost. Thankfully, dropbear only disallows shell access, which means port forwarding is possible (this is how the Tether app manages the router).

```
ssh admin@192.168.0.1 -L 20002:127.0.0.1:20002 -N
```

The password is the same as the one for the web admin. You may need to specify the Cipher and Key specs in order to get SSH to make a connection. I leave that as an exercise for the user.

## Example

The example below should return a JSON object which contains a list of clients connected to the device.

```
$ python3 tmpcli.py 127.0.0.1 20002 -o 0x310 -p '{"amount":32,"start_index":0}'   
INFO:root:Connected to 127.0.0.1:20002
{
	"start_index":	0,
	"client_list":	[{
			"mac":	"DE-AD-BE-EF-CA-FE",
			"conn_type":	"wired",
			"time_period":	-1,
			"ip":	"192.168.0.100",
			"access_time": -19975507200,
			"online":	true,
			"name":	"aHR0cHM6Ly93d3cueW91dHViZS5jb20vd2F0Y2g/dj1kUXc0dzlXZ1hjUQ==",
			"owner_id":	-1,
			"remain_time":	-1,
			"owner_name":	"",
			"client_type":	"other",
			"enable_priority":	false
		}],
	"sum":	1,
	"amount":	1
}
```

## References

1. [Pedro Ribeiro (@pedrib1337) and Radek Domanski (@RabbitPro)](https://www.thezdi.com/blog/2020/4/6/exploiting-the-tp-link-archer-c7-at-pwn2own-tokyo)
    - this blogpost was immensely helpful for the TdpPacket class. Thanks to Pedro and Radek.