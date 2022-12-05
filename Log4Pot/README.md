# Log4Pot

A honeypot for the Log4Shell vulnerability (CVE-2021-44228).

License: [GPLv3.0](https://www.gnu.org/licenses/gpl-3.0.html)

## Features

* Listen on various ports for Log4Shell exploitation.
* Detect exploitation in request line and headers.
* Download exploit payloads recursively.
* Log to file and Azure blob storage.

## Usage

1. Install Poetry: `curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python3 -`
2. Fetch this GitHub repository `git clone https://github.com/thomaspatzke/Log4Pot.git`
3. Change directory into the local copy with `cd Log4Pot`
4. Install pycurl dependencies (Debian / Ubuntu): `apt install libcurl4-openssl-dev libssl-dev python3-dev build-essential`
5. Install python dependencies: `poetry install`
6. Put parameters into log4pot.conf, see `poetry run python log4pot.py --help` for an overview.
7. Run: `poetry run python log4pot.py @log4pot.conf`

Alternatively, you can also run log4pot without external dependencies:
```
$ python log4pot.py @log4pot.conf
```
This will run log4pot without support for logging to Azure blob storage.

## Redirecting traffic / non-container setup

To redirect traffic to port 80 and 443 to Log4Pot, use following iptables commands:

`iptables -t nat -A PREROUTING -i eth0 -p tcp --dport 80 -j REDIRECT --to-port 8080`

`iptables -t nat -A PREROUTING -i eth0 -p tcp --dport 443 -j REDIRECT --to-port 8443`

## Log Analysis Tool

The script `log4pot-loganalyzer.py` extracts all payloads, decodes them with the current decoder and builds a timeline from both. Use is as follows:

```
python log4pot-loganalyzer.py -o <output directory> <input log files>
```

## Analyzing Logs with JQ

List payloads from exploitation attempts:
```
select(.type == "exploit") | .payload
```

Decode all base64-encoded payloads from JNDI exploit:
```
select(.type == "exploit" and (.payload | contains("Base64"))) | .payload | sub(".*/Base64/"; "") | sub ("}$"; "") | @base64d
```

Extract all SHA256 hashes from files downloaded from URLs:
```
[ .[] | select(.type == "payload") | .urls | select((. | length) > 0) | to_entries | .[].value | select((. | length) == 64) ] | unique | .[]
```
